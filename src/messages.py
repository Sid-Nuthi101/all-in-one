import subprocess
import os
import shutil
import sqlite3
from datetime import datetime
from contacts import ContactsConnector
from typing import Dict, List, Optional, Tuple


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

        handles = [row[6] for row in rows if row[4] == 0 and row[6]]
        ContactsConnector.build_index_for_handles(handles)

        chats: List[Dict[str, Optional[str]]] = []
        for chat_id, display_name, chat_identifier, date_val, is_from_me, text, handle in rows:
            dt = self.apple_time_to_dt(date_val)
            name = display_name or ContactsConnector.get_contact_name(handle) or handle or chat_identifier or "Unknown"
            preview = " ".join((text or "").split()) or "No message"
            time_str = dt.strftime("%I:%M %p").lstrip("0") if dt else ""
            initials = "".join([part[0] for part in name.split()[:2]]).upper() or "?"
            chats.append(
                {
                    "id": str(chat_id),
                    "name": name,
                    "time": time_str,
                    "preview": preview,
                    "initials": initials,
                    "is_from_me": "1" if is_from_me else "0",
                }
            )

        return chats
    
    # Sends a Imessage message 
    def send_imessage(self, phone_or_email, text):
        script = f'''
        tell application "Messages"
            send "{text}" to buddy "{phone_or_email}" of (service 1 whose service type is iMessage)
        end tell
        '''
        subprocess.run(["osascript", "-e", script])

    def last_messages_in_chat(
        self,
        chat_rowid: int,
        limit: int = 100,
    ) -> List[Tuple[int, int, str, Optional[str]]]:
        """
        Returns last N messages for a single conversation (chat ROWID).
        Each row: (date, is_from_me, text, handle)
        """
        self.cur.execute("""
            SELECT
                m.date,
                m.is_from_me,
                COALESCE(m.text, '') AS text,
                h.id AS handle
            FROM chat_message_join cmj
            JOIN message m ON m.ROWID = cmj.message_id
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE cmj.chat_id = ?
            ORDER BY m.date DESC
            LIMIT ?
        """, (chat_rowid, limit))
        return self.cur.fetchall()

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
