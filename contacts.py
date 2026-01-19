# contacts.py
import re
import threading
from typing import Dict, Iterable, Optional, Set

import Contacts  # PyObjC binding: pyobjc-framework-Contacts


class ContactsConnector:
  _built: bool = False
  _map: Dict[str, Optional[str]] = {}

  @staticmethod
  def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

  @staticmethod
  def _normalize_us_digits(d: str) -> str:
    # If it’s 11 digits and starts with US country code "1", drop it
    if len(d) == 11 and d.startswith("1"):
      return d[1:]
    return d

  @staticmethod
  def _display_name(contact) -> str:
    given = str(contact.givenName() or "")
    family = str(contact.familyName() or "")
    name = (given + " " + family).strip()
    return name if name else "Unknown"

  @classmethod
  def _ensure_authorized(cls, store, wait_sec: float = 10.0) -> bool:
    status = Contacts.CNContactStore.authorizationStatusForEntityType_(
      Contacts.CNEntityTypeContacts
    )

    if status == Contacts.CNAuthorizationStatusAuthorized:
      return True

    if status != Contacts.CNAuthorizationStatusNotDetermined:
      # Denied / Restricted
      return False

    ev = threading.Event()
    result = {"ok": False}

    def cb(ok, err):
      result["ok"] = bool(ok)
      ev.set()

    store.requestAccessForEntityType_completionHandler_(
      Contacts.CNEntityTypeContacts, cb
    )

    ev.wait(wait_sec)
    return bool(result["ok"])

  @classmethod
  def build_index_for_handles(cls, handles: Iterable[str]) -> None:
    if cls._built:
      return

    uniq: Set[str] = set(h for h in handles if h)

    # Pre-fill map so get_contact_name() is safe even if auth fails
    cls._map = {h: None for h in uniq}

    # Build desired lookup keys (only for real-looking handles)
    want_emails: Set[str] = set()
    want_last10: Set[str] = set()
    want_last7: Set[str] = set()

    for h in uniq:
      if "@" in h:
        want_emails.add(h.lower())
        continue

      d = cls._digits(h)
      # Filter out short codes / garbage: keep only 7+ digits
      if len(d) < 7:
        continue

      if len(d) >= 10:
        want_last10.add(d[-10:])
      else:
        want_last7.add(d[-7:])

    store = Contacts.CNContactStore.alloc().init()
    if not cls._ensure_authorized(store):
      cls._built = True
      return

    keys = [
      Contacts.CNContactGivenNameKey,
      Contacts.CNContactFamilyNameKey,
      Contacts.CNContactPhoneNumbersKey,
      Contacts.CNContactEmailAddressesKey,
    ]
    req = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)

    phone10_to_name: Dict[str, str] = {}
    phone7_to_name: Dict[str, str] = {}
    email_to_name: Dict[str, str] = {}

    count = {"n": 0}

    def handler(contact, stop_ptr):
        # IMPORTANT: do not return anything from this function.
        count["n"] += 1

        name = cls._display_name(contact)

        for lv in (contact.emailAddresses() or []):
            try:
                e = str(lv.value() or "").lower()
            except Exception:
                continue
            if e:
                email_to_name[e] = name

        for lv in (contact.phoneNumbers() or []):
            try:
                pn = lv.value()
                s = str(pn.stringValue() if pn else "")
            except Exception:
                continue

            d = cls._normalize_us_digits(cls._digits(s))
            if len(d) >= 10:
                phone10_to_name[d[-10:]] = name
            if len(d) >= 7:
                phone7_to_name[d[-7:]] = name

    ok, err = store.enumerateContactsWithFetchRequest_error_usingBlock_(req, None, handler)

    print("enumerate ok:", ok)
    print("enumerate err:", err)
    print("contacts visited:", count["n"])
    print("indexed last10:", len(phone10_to_name))
    print("indexed last7:", len(phone7_to_name))
    print("indexed emails:", len(email_to_name))



    # Fill the map for requested handles
    for h in uniq:
      if "@" in h:
        cls._map[h] = email_to_name.get(h.lower())
        continue

      d = cls._digits(h)
      if len(d) < 7:
        cls._map[h] = None
        continue

      nm = None
      if len(d) >= 10:
        nm = phone10_to_name.get(d[-10:])
      if nm is None:
        nm = phone7_to_name.get(d[-7:])
      cls._map[h] = nm

    cls._built = True

  @classmethod
  def get_contact_name(cls, handle: str) -> Optional[str]:
    if not handle:
      return None
    return cls._map.get(handle)
