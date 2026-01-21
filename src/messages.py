import subprocess
import os
import shutil
import sqlite3
from datetime import datetime
from contacts import ContactsConnector
from typing import Any, Dict, List, Optional, Tuple
from Foundation import NSData, NSKeyedUnarchiver  # type: ignore

APPLE_EPOCH = 978307200  # seconds between 1970-01-01 and 2001-01-01


class MessageBridge:

    def __init__(self, db_path=None):
        if db_path is None:
            self._copy_messages_db_snapshot()
        src = db_path or os.path.expanduser("~/Library/Messages/chat.db")
        self.tmp = "/tmp/chat.db"
        shutil.copy2(src, self.tmp)  # avoids "db locked" issues
        self.conn = sqlite3.connect(self.tmp)
        self.cur = self.conn.cursor()
    
    @staticmethod
    def _copy_messages_db_snapshot() -> None:
        src_db = os.path.expanduser("~/Library/Messages/chat.db")
        tmp_db = "/tmp/chat.db"

        """
        Copy chat.db + WAL/SHM so we include newest messages (WAL mode).
        """
        shutil.copy2(src_db, tmp_db)
        for suffix in ("-wal", "-shm"):
            s = src_db + suffix
            d = tmp_db + suffix
            if os.path.exists(s):
                shutil.copy2(s, d)

    @staticmethod
    def apple_time_to_dt(t):
        if t is None:
            return None
        # Most modern macOS: nanoseconds since 2001-01-01
        ts = (t / 1_000_000_000) + APPLE_EPOCH
        return datetime.fromtimestamp(ts)

    def last_100_messages(self):
        # 1) Fetch messages
        self.cur.execute("""
            SELECT
                m.date,
                m.is_from_me,
                COALESCE(m.text, '') AS text,
                h.id AS handle
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            ORDER BY m.date DESC
            LIMIT 50
        """)
        messages = self.cur.fetchall()

        # 2) Fetch distinct handles (non-me)
        self.cur.execute("""
            SELECT DISTINCT h.id
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            WHERE m.is_from_me = 0 AND h.id IS NOT NULL
            ORDER BY m.date DESC
            LIMIT 200
        """)
        handles = [row[0] for row in self.cur.fetchall()]

        # 3) Build contact index once
        ContactsConnector.build_index_for_handles(handles)

        # 4) Print messages
        for date_val, is_from_me, text, handle in messages:
            dt = self.apple_time_to_dt(date_val)
            sender = "me" if is_from_me else (
                ContactsConnector.get_contact_name(handle) or handle or "unknown"
            )
            print(f"[{dt}] {sender}: {text}")

    def top_chats(self, limit: int = 50) -> List[Dict[str, Optional[str]]]:
        """
        Returns a list of the most recent chats with display-friendly metadata.
        """
        self.cur.execute("""
            SELECT
                c.ROWID AS chat_id,
                c.display_name,
                c.chat_identifier,
                m.date,
                m.is_from_me,
                COALESCE(m.text, '') AS text,
                h.id AS handle
            FROM chat c
            JOIN chat_message_join cmj ON cmj.chat_id = c.ROWID
            JOIN message m ON m.ROWID = cmj.message_id
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE m.date = (
                SELECT MAX(m2.date)
                FROM chat_message_join cmj2
                JOIN message m2 ON m2.ROWID = cmj2.message_id
                WHERE cmj2.chat_id = c.ROWID
            )
            ORDER BY m.date DESC
            LIMIT ?
        """, (limit,))
        rows = self.cur.fetchall()

        chat_ids = [row[0] for row in rows]
        participant_handles: Dict[int, List[str]] = {}
        all_handles: List[str] = [row[6] for row in rows if row[4] == 0 and row[6]]
        for chat_id in chat_ids:
            handles = self._chat_participants(chat_id)
            participant_handles[chat_id] = handles
            all_handles.extend(handles)

        ContactsConnector.build_index_for_handles(all_handles)

        chats: List[Dict[str, Optional[str]]] = []
        for chat_id, display_name, chat_identifier, date_val, is_from_me, text, handle in rows:
            dt = self.apple_time_to_dt(date_val)
            name = display_name or ContactsConnector.get_contact_name(handle) or handle or chat_identifier or "Unknown"
            preview = " ".join((text or "").split()) or "No message"
            time_str = dt.strftime("%I:%M %p").lstrip("0") if dt else ""
            initials = "".join([part[0] for part in name.split()[:2]]).upper() or "?"
            seen_participants = set()
            participant_names = []
            for h in participant_handles.get(chat_id, []):
                if not h:
                    continue
                name_val = ContactsConnector.get_contact_name(h) or h or "Unknown"
                if name_val in seen_participants:
                    continue
                seen_participants.add(name_val)
                participant_names.append(name_val)
            chats.append(
                {
                    "id": str(chat_id),
                    "name": name,
                    "time": time_str,
                    "preview": preview,
                    "initials": initials,
                    "is_from_me": "1" if is_from_me else "0",
                    "participants": participant_names,
                }
            )

        return chats

    def _chat_participants(self, chat_id: int) -> List[str]:
        self.cur.execute("""
            SELECT DISTINCT h.id
            FROM chat_handle_join chj
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE chj.chat_id = ?
        """, (chat_id,))
        return [row[0] for row in self.cur.fetchall() if row[0]]
    
    # Sends a Imessage message 
    def send_imessage(self, phone_or_email, text):
        script = f'''
        tell application "Messages"
            send "{text}" to buddy "{phone_or_email}" of (service 1 whose service type is iMessage)
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
    
    MessageRow = Tuple[int, int, str, Optional[str], str, List[Dict[str, Any]]]

    def _text_from_attributed_body(self, blob: Optional[bytes]) -> str:
        """
        Decode Messages' message.attributedBody (often a 'typedstream' archive).
        Tries:
            1) NSUnarchiver (typedstream)
            2) NSKeyedUnarchiver (keyed)
            3) best-effort byte pattern extraction
        """
        if not blob:
            return ""

        # Ensure it's bytes (sqlite can sometimes hand back memoryview)
        if isinstance(blob, memoryview):
            blob = blob.tobytes()

        # 1) Typedstream path (your blobs: b'\\x04\\x0bstreamtyped...')
        try:
            from Foundation import NSData, NSUnarchiver  # type: ignore

            data = NSData.dataWithBytes_length_(blob, len(blob))
            obj = NSUnarchiver.unarchiveObjectWithData_(data)
            if obj is not None and hasattr(obj, "string"):
                return str(obj.string())
        except Exception:
            pass

        # 2) Keyed-archive fallback (some macOS versions / other blobs)
        try:
            from Foundation import NSData, NSKeyedUnarchiver  # type: ignore

            data = NSData.dataWithBytes_length_(blob, len(blob))
            obj = NSKeyedUnarchiver.unarchiveObjectWithData_(data)
            if obj is not None and hasattr(obj, "string"):
                return str(obj.string())
        except Exception:
            pass

        # 3) Best-effort fallback:
        # Many blobs embed text as: b"\\x01+" + <1 byte length> + <utf8 bytes>
        try:
            marker = b"\x01+"
            i = blob.find(marker)
            if i != -1 and i + 3 <= len(blob):
                n = blob[i + 2]
                start = i + 3
                end = start + n
                if end <= len(blob):
                    return blob[start:end].decode("utf-8", errors="ignore")
        except Exception:
            pass

        return ""

    def last_messages_in_chat(
        self,
        chat_rowid: int,
        limit: int = 100,
    ) -> List[MessageRow]:
        """
        Returns last N messages for a single conversation (chat ROWID).

        Each row:
        (date, is_from_me, text, handle, kind)

        kind:
        - "text"
        - "attachment"  (pure attachment bubble with no visible text)
        - "reaction"    (tapback)
        - "unknown"
        """
        TAPBACK_TYPES = set(range(2000, 2006)) | set(range(3000, 3006))

        self.cur.execute("""
        SELECT
            m.ROWID AS message_rowid,
            m.date,
            m.is_from_me,
            m.text,
            m.attributedBody,
            h.id AS handle,
            m.cache_has_attachments,
            m.associated_message_type
        FROM chat_message_join cmj
        JOIN message m ON m.ROWID = cmj.message_id
        LEFT JOIN handle h ON h.ROWID = m.handle_id
        WHERE cmj.chat_id = ?
        ORDER BY m.date DESC
        LIMIT ?;
        """, (chat_rowid, limit))
        rows = self.cur.fetchall()

        out: List[MessageRow] = []

        for (
        message_rowid,
        date,
        is_from_me,
        text,
        attributed_body,
        handle,
        cache_has_attachments,
        associated_message_type,
        ) in rows:
            raw_text = (text or "")
            if not raw_text.strip() and attributed_body:
                raw_text = self._text_from_attributed_body(attributed_body)

            raw_text = raw_text or ""
            is_placeholder = (raw_text == "￼")

            # Normalize assoc type: some DBs store 0 instead of NULL
            assoc_type = associated_message_type
            if assoc_type == 0:
                assoc_type = None

            is_tapback = (assoc_type in TAPBACK_TYPES)

            has_attachments = (cache_has_attachments == 1)

            kind = "text"
            normalized_text = raw_text

            if is_tapback:
                kind = "reaction"
                # For tapbacks you usually don't want to show any body text
                normalized_text = "Reaction"

            elif has_attachments:
                # Link previews can set attachments but still have real text.
                # Only call it an attachment bubble if there isn't visible text.
                if (not normalized_text.strip()) or is_placeholder:
                    kind = "attachment"
                    normalized_text = "Attachment"
                else:
                    kind = "text"

            elif (not normalized_text.strip()) or is_placeholder:
                kind = "unknown"
                normalized_text = "Unknown"

            out.append((
                int(date),
                int(is_from_me or 0),
                normalized_text,
                handle,
                kind,
            ))

        return out

    def last_100_messages_in_chat(self, chat_rowid: int) -> List[Tuple[int, int, str, Optional[str]]]:
        """
        Returns last 100 messages for a single conversation (chat ROWID).
        Each row: (date, is_from_me, text, handle)
        """
        return self.last_messages_in_chat(chat_rowid, limit=100)

    def last_100_messages_for_latest_conversations(self, x: int) -> Dict[int, List[Tuple[int, int, str, Optional[str]]]]:
        """
        For the latest X conversations (by most recent message.date),
        return last 100 messages per conversation.

        Returns: { chat_rowid: [ (date, is_from_me, text, handle), ... ] }
        """
        # Get latest x chats by most recent message time
        self.cur.execute("""
            SELECT
                cmj.chat_id,
                MAX(m.date) AS last_date
            FROM chat_message_join cmj
            JOIN message m ON m.ROWID = cmj.message_id
            GROUP BY cmj.chat_id
            ORDER BY last_date DESC
            LIMIT ?
        """, (x,))
        chat_ids = [row[0] for row in self.cur.fetchall()]

        # Build contacts index from all handles in these chats (non-me)
        # (optional but speeds up printing names)
        if chat_ids:
            placeholders = ",".join("?" for _ in chat_ids)
            self.cur.execute(f"""
                SELECT DISTINCT h.id
                FROM chat_message_join cmj
                JOIN message m ON m.ROWID = cmj.message_id
                LEFT JOIN handle h ON h.ROWID = m.handle_id
                WHERE cmj.chat_id IN ({placeholders})
                  AND m.is_from_me = 0
                  AND h.id IS NOT NULL
                LIMIT 2000
            """, tuple(chat_ids))
            handles = [r[0] for r in self.cur.fetchall()]
            ContactsConnector.build_index_for_handles(handles)

        out: Dict[int, List[Tuple[int, int, str, Optional[str]]]] = {}
        for chat_id in chat_ids:
            out[chat_id] = self.last_messages_in_chat(chat_id, limit=100)

        return out

if __name__ == "__main__":
    MessageBridge._copy_messages_db_snapshot()
    mb = MessageBridge()

    chats = mb.last_100_messages_for_latest_conversations(5)

    for chat_id, msgs in chats.items():
        print("\n" + "=" * 80)
        print(f"CHAT {chat_id} (showing {len(msgs)} most recent)")
        print("=" * 80)
        for date_val, is_from_me, text, handle in msgs:
            dt = mb.apple_time_to_dt(date_val)
            sender = "me" if is_from_me else (ContactsConnector.get_contact_name(handle) or handle or "unknown")
            print(f"[{dt}] {sender}: {text}")
