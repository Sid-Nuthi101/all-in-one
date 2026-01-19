# ALL IN ONE

**ALL IN ONE** is a macOS-focused, Python-based desktop application that acts as a personal communication copilot.  
It unifies **iMessage context**, **email triage**, and **LLM-powered reasoning** into a single tool that helps you decide **what matters**, **when to respond**, and **how to respond** — without sending anything automatically.

The core principle of this app is **human-in-the-loop automation**: the LLM can analyze, summarize, and draft responses, but **you always approve before anything is sent**.

---

## Features

### 📨 iMessage Intelligence (Planned / In Progress)
- iMessage extension captures recent conversation context
- Message threads are summarized using an LLM
- Suggested replies are generated in your writing style
- App prompts you before sending any response

### 📧 Email Importance Detection
- Ingests emails via IMAP, Gmail API, or forwarding
- LLM assigns an importance score with reasoning
- Highlights time-sensitive or high-priority messages
- Drafts replies only after user approval

### 🧠 Central Reasoning Layer
- Python orchestrator processes all message context
- Firebase acts as the shared backend and state store
- Stores summaries, drafts, importance scores, and user actions

### 🖥️ Native macOS Desktop App
- Built with **PySide6 (Qt)**
- Packaged into a standalone macOS app using **PyInstaller**
- Lightweight UI designed for quick review and action

---

## Architecture Overview

ALL IN ONE is built as a **multi-client, Firebase-backed system** with a clear separation of responsibilities between data collection, reasoning, and execution.

The **macOS client is the primary authority** in the system.  
Both macOS and iPhone clients publish recent message context to Firebase, but **historical backfill, reconciliation, and authoritative state are handled exclusively by the macOS client**.

High-level principles:
- Clients *report state*, they do not decide
- The Python + LLM layer *reasons*, it does not act autonomously
- The user *approves*, nothing is sent implicitly

---

## System Components

### 1. macOS Client (Primary / Authority)

The macOS client is the **source of truth** for iMessage history and execution.

Responsibilities:
- Reads the local iMessage database (`chat.db`) on macOS
- Periodically snapshots the database to avoid locking issues
- Extracts:
  - Recent conversations
  - Per-chat message history
  - Sender identity and directionality
- Performs **historical backfill** for conversations not yet present in Firebase
- Sends structured message payloads to Firebase
- Executes outbound iMessage sends (after approval)

Key properties:
- Runs with local filesystem access
- Handles Apple-specific time formats and contact resolution
- Owns reconciliation when state differs between devices

The macOS client ensures Firebase eventually contains a **complete and consistent view** of message history.

---

### 2. iPhone Client (Secondary / Reporter)

The iPhone client acts as a **low-latency reporter**, not an authority.

Responsibilities:
- Publishes its view of the most recent messages per conversation
- Optimized for:
  - Near-real-time updates
  - Lightweight context snapshots
- Does **not**:
  - Perform historical backfill
  - Resolve conflicts
  - Execute sends

If the iPhone client is offline or missing history, the system remains correct because the macOS client will backfill and reconcile.

---

### 3. Firebase (Shared State Layer)

Firebase acts as the **coordination and synchronization layer** between clients and the reasoning engine.

It stores:
- Message snapshots from all clients
- Conversation metadata
- Thread-level state
- LLM outputs (summaries, importance scores, drafts)
- User actions and approvals

Firebase is treated as:
- **Eventually consistent**
- Append-heavy
- Auditable

The macOS client is responsible for correcting gaps or inconsistencies.

---

### 4. Python Orchestrator (Reasoning Engine)

The Python application is the **central reasoning layer**.

Responsibilities:
- Listens for new or updated message/email payloads
- Aggregates context across devices
- Determines when backfill is complete or pending
- Calls the LLM to:
  - Summarize conversations
  - Detect urgency or required action
  - Classify email importance
  - Draft suggested replies
- Writes results back to Firebase
- Surfaces decisions to the UI

The orchestrator never sends messages directly.

---

### 5. LLM Usage Model

The LLM is used strictly for **analysis and drafting**, not execution.

Typical outputs:
- Thread summaries
- Importance classifications
- Suggested replies
- Explanations of urgency

Constraints:
- No direct access to messaging APIs
- No send permissions
- Bounded context size
- All outputs are reviewable and editable

This ensures predictable, safe behavior.

---

### 6. User Approval Loop (Hard Safety Boundary)

ALL IN ONE enforces a **non-bypassable approval loop**.

Before any outbound action:
- The user is shown:
  - Relevant context
  - The model’s reasoning
  - The drafted response
- The user must explicitly:
  - Approve and send
  - Edit and send
  - Dismiss

No automation crosses this boundary.

---

## Backend Data Model (Conceptual)

Firebase collections are structured to support multi-client sync and auditability:

users/{userId}
devices/{deviceId}
threads/{threadId}
threads/{threadId}/messages/{messageId}
emails/{emailId}
model_outputs/{outputId}
actions/{actionId}


Design goals:
- Append-first writes
- Minimal destructive updates
- Clear ownership (macOS client as authority)

---

## Configuration & Environment Variables

All configuration is managed via environment variables.

Example:

LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here

FIREBASE_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service_account.json

EMAIL_MODE=imap
IMAP_HOST=imap.example.com
IMAP_PORT=993
IMAP_USER=your_email
IMAP_PASSWORD=your_password

REQUIRE_EXPLICIT_SEND_APPROVAL=true
LOG_LEVEL=info


Secrets must never be committed.

---

## Running the System

To run the desktop app locally:

```bash
python main.py
```
This launches the macOS client UI and initializes:

Message ingestion

Firebase listeners

LLM orchestration

Building the macOS App

The macOS client is bundled using PyInstaller.

pyinstaller MyApp.spec


The resulting .app bundle is created in the dist/ directory.

Privacy & Safety Guarantees

No automatic sending of messages or emails

macOS client executes sends only after approval

LLM outputs are advisory only

Message history access is local to the user’s device

Clear separation between collection, reasoning, and execution

Future Extensions

Per-contact response style profiles

Calendar-aware reply suggestions

Priority inbox and daily digests

CRM-style conversation views

On-device embedding cache

Multi-device expansion beyond Apple platforms

Disclaimer

This software interacts with private communications.

You are responsible for:

Compliance with Apple platform policies

Securing credentials and local data

Ensuring informed user consent