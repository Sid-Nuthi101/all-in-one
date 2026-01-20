# Tech Spec: Personalized LLM Fine-Tuning From User Texts (UI out of scope)

**Owner:** (you)  
**Last updated:** 2026-01-19  
**Status:** Draft

## 1) Summary

We will create a per-user personalized language model by fine-tuning an OpenAI base model on the user’s last 3 months of outbound texts (messages **sent by the user**). The resulting fine-tuned model will be stored/identified by OpenAI’s returned `fine_tuned_model` ID, and referenced for future chat completions. Firebase will store metadata mapping `userId -> fine_tuned_model` and related job/versioning data.

> Note: This is “fine-tuning” (supervised fine-tuning), not “pretraining.” OpenAI’s fine-tuning API expects a JSONL dataset and produces a new model ID. :contentReference[oaicite:0]{index=0}

---

## 2) Goals

- Train a **personalized** model per user from the last 3 months of their sent texts.
- Use the fine-tuned model for future responses to mimic the user’s writing style.
- Store model/job metadata in Firebase and associate it with authenticated user accounts.
- Provide a repeatable pipeline with evaluation + regression checks.
- Add automated unit tests (and a minimal integration test) for the pipeline.

## 3) Non-goals

- UI/UX (chat UI, settings screens, opt-in screens) is out of scope.
- Building an iOS extension / on-device training is out of scope.
- Multi-modal (image) fine-tuning is out of scope.
- “Memory”/RAG personalization beyond the fine-tuned style is out of scope (but noted as future work).

---

## 4) Proposed Architecture (High Level)

### Components
1. **Auth + User Identity**
   - Existing login system provides `userId` (Firebase Auth UID or equivalent).

2. **Data Extraction Service**
   - Fetch last 3 months of **sent** user texts from the messages source (e.g., macOS Messages DB via your bridge, or your ingestion pipeline).
   - Output: normalized message records.

3. **Dataset Builder**
   - Converts normalized messages into OpenAI fine-tuning JSONL in **chat format** (one JSON object per line). :contentReference[oaicite:1]{index=1}
   - Optionally adds synthetic “prompt” context to better shape behavior (see §7).

4. **Fine-Tuning Orchestrator**
   - Upload JSONL file to OpenAI with purpose `fine-tune`.
   - Create fine-tuning job against a supported base model.
   - Poll status until completed/failed.
   - Store resulting `fine_tuned_model` ID in Firebase. :contentReference[oaicite:2]{index=2}

5. **Inference Service**
   - For future chats, load `fine_tuned_model` for `userId` from Firebase.
   - If not available, fall back to a base model.

6. **Firebase (Metadata)**
   - Stores model versions, training config, job state, evaluation results, and safety flags.

---

## 5) Data Model (Firebase)

### Collection: `users/{userId}`
- `activeModelId`: string | null (OpenAI fine-tuned model ID)
- `activeModelVersion`: number
- `modelStatus`: enum (`none|training|ready|failed|disabled`)
- `modelUpdatedAt`: timestamp

### Collection: `llmModels/{modelDocId}`
Suggested `modelDocId = userId + ":" + version`

Fields:
- `userId`: string
- `version`: number (monotonic per user)
- `baseModel`: string (e.g., `gpt-4o-mini` or another supported fine-tuning base)
- `openaiTrainingFileId`: string
- `openaiJobId`: string
- `openaiFineTunedModelId`: string | null
- `status`: enum (`queued|running|succeeded|failed|cancelled`)
- `createdAt`: timestamp
- `completedAt`: timestamp | null
- `trainingDataRange`: `{ start: timestamp, end: timestamp }`
- `numMessages`: number
- `tokenEstimate`: number
- `eval`: `{ holdoutLoss?: number, humanScore?: number, styleSimilarity?: number }`
- `safety`: `{ piiRedaction: boolean, userOptIn: boolean, disabledReason?: string }`
- `config`: `{ systemPromptVersion: string, datasetBuilderVersion: string, hyperparams?: object }`
- `artifacts`: `{ datasetHash: string, codeVersionSha: string }`

---

## 6) End-to-End Flow

### 6.1 Trigger
- Trigger when user opts in OR on a schedule (e.g., weekly re-train) OR manually via admin endpoint.

### 6.2 Extract (Last 3 months)
- Query messages for `sender == user` and `timestamp >= now - 90 days`.
- Normalize into:
  - `messageId`, `timestamp`, `text`, `conversationId` (optional), `recipientCount` (optional)

### 6.3 Clean + Filter
- Drop:
  - empty/emoji-only (optional threshold)
  - extremely short messages (e.g., `< 3 chars`) unless common user behavior
  - messages containing only URLs (optional)
- Redact obvious PII:
  - phone numbers, emails, addresses (configurable)
- Deduplicate repeated messages (copy/paste spam)

### 6.4 Build JSONL
OpenAI SFT expects JSONL, one object per line, using chat format. :contentReference[oaicite:3]{index=3}

Each line should look like:
```json
{"messages":[{"role":"system","content":"You write like the user. Match tone and brevity."},{"role":"user","content":"<optional prompt/context>"},{"role":"assistant","content":"<the user’s sent text>"}]}
```

Important: Because we’re training on sent texts, we don’t naturally have “user prompt -> assistant response” pairs. We will create synthetic prompts to elicit the “assistant” output as the user’s message (see §7).


## 6.6 Serve (Inference)

- On each incoming chat request:
  - Resolve `userId` from the authenticated session.
  - Fetch `users/{userId}.activeModelId` from Firebase.
- Decision logic:
  - If `activeModelId` exists **and** `modelStatus == ready`, route the request to OpenAI using the fine-tuned model.
  - Otherwise, fall back to the default base model.
- Attach a lightweight system prompt to reinforce constraints (e.g., safety, verbosity caps).
- Log inference metadata:
  - `requestId`
  - `userId`
  - `modelIdUsed`
  - latency
  - token counts
  - fallback reason (if applicable)

---

## 7 Dataset Strategy (Training From Sent Texts Only)

Because the dataset consists only of **outbound user messages**, we must synthesize prompts so the model learns *style, tone, and phrasing* rather than conversational state.

### 7.1 Core Principle
- The user’s sent message is always treated as the **assistant output**.
- The **user prompt** is synthetic and designed to elicit that output.

### 7.2 Prompt Construction Options

#### Option A: Style Rewrite Prompt (Initial Implementation)
For each user message `T`:

- **System**
  - “You are an assistant that writes messages exactly like the user. Match tone, brevity, slang, punctuation, and emoji usage.”
- **User**
  - “Write a message in the user’s style that says the following.”
- **Assistant**
  - `T`

**Pros**
- Simple and robust
- Maximizes stylistic learning

**Cons**
- Does not encode conversational intent

#### Option B: Intent-Based Prompting (Future Enhancement)
- Classify messages into coarse intents:
  - `confirmation`, `decline`, `question`, `logistics`, `status_update`, `joke`, etc.
- Prompt example:
  - “Write a **logistics update** message in the user’s style.”

**Pros**
- Better controllability at inference
- Enables intent-conditioned generation

**Cons**
- Requires intent classifier + additional tests

### 7.3 Train / Holdout Split
- Sort messages chronologically.
- Use:
  - 90% for training
  - 10% (most recent) as holdout evaluation set
- Holdout is **never** uploaded for fine-tuning.

---

## 8 Model Choice and OpenAI Integration

- Use OpenAI’s **supervised fine-tuning** workflow.
- Dataset requirements:
  - JSONL format
  - One training example per line
  - Chat-style `messages` array
- Training flow:
  1. Upload dataset file with purpose `fine-tune`
  2. Create fine-tuning job referencing uploaded file
  3. Poll job status until terminal state
- Persist returned `fine_tuned_model` ID as immutable artifact.
- New training runs always create a **new version** (no overwrite).

---

## 9 Privacy, Safety, and Compliance

### 9.1 User Consent
- Explicit opt-in required before:
  - data extraction
  - dataset upload
  - model training
- Opt-in state stored in Firebase.

### 9.2 Data Handling
- Raw message text:
  - exists only transiently during dataset construction
  - never stored long-term in Firebase
- Firebase stores:
  - hashes
  - counts
  - OpenAI file/job/model IDs
  - timestamps

### 9.3 Redaction
- Before upload:
  - redact phone numbers
  - redact email addresses
  - redact physical addresses (best-effort)
- Redaction rules are versioned and test-covered.

### 9.4 Disable / Revoke
- User can disable personalization at any time:
  - `users/{userId}.modelStatus = disabled`
- Inference immediately falls back to base model.
- No further training runs are triggered.

---

## 10 Observability

### 10.1 Metrics

**Training**
- dataset build duration
- number of messages
- estimated token count
- job queue time
- job runtime
- success / failure rate

**Inference**
- p50 / p95 latency
- tokens per response
- fine-tuned vs fallback usage rate

### 10.2 Logging
- All logs include:
  - `requestId`
  - `userId`
  - `modelVersion`
- Training logs additionally include:
  - `openaiJobId`

---

## 11 Testing Plan

### 11.1 Unit Tests

#### Data Extraction
- `filters_messages_to_last_90_days`
- `returns_only_user_sent_messages`
- `handles_no_messages_gracefully`

#### Cleaning & Redaction
- `redacts_phone_numbers`
- `redacts_emails`
- `removes_duplicate_messages`
- `filters_short_messages_by_threshold`

#### Dataset Builder
- `produces_valid_jsonl`
- `one_json_object_per_line`
- `includes_system_prompt`
- `deterministic_output_for_same_input`
- `correct_train_holdout_split`

#### Firebase Metadata
- `creates_model_metadata_document`
- `increments_model_version`
- `sets_active_model_on_success`
- `does_not_set_active_model_on_failure`

#### Inference Routing
- `uses_finetuned_model_when_ready`
- `falls_back_when_model_missing`
- `falls_back_when_model_disabled`

---

### 11.2 Integration Test (Mocked External Services)

- Mock OpenAI client:
  - upload returns fixed `fileId`
  - fine-tune creation returns `jobId`
  - polling resolves to `succeeded`
- Assert:
  - Firebase state transitions are correct
  - fine-tuned model ID is persisted
  - inference path selects correct model

---

### 11.3 Contract / Validation Tests

- Validate JSONL schema prior to upload.
- Validate minimum dataset size constraints.
- Validate OpenAI error handling paths:
  - invalid file
  - insufficient examples
  - job failure

### 11.4 Setup (Local Dev)

**Openai:** Required setup for local development and testing:
- Set `OPENAI_API_KEY` in your shell or `.env`.
- Ensure Firebase emulator or credentials are available (Service Account JSON or `GOOGLE_APPLICATION_CREDENTIALS`).
- Configure `FIREBASE_PROJECT_ID` and collection names for `users` and `llmModels`.
- Provide a local message source or fixture data for the data extraction service (e.g., export of last 3 months of sent messages).
- Install dependencies for the pipeline (OpenAI SDK, Firebase Admin SDK, JSONL validation utilities).

---

## 12 Rollout Plan

### Phase 0 — Development
- Single internal user
- Mocked OpenAI
- Full unit test coverage

### Phase 1 — Internal Production
- Limited real fine-tuning runs
- Manual review of outputs
- Cost tracking enabled

### Phase 2 — Beta
- User opt-in
- Automated re-training eligibility checks
- Fallback monitoring

### Phase 3 — Scale
- Dataset size caps
- Minimum message thresholds
- Re-training cooldown windows
- Version rollback support

---

## 13 Failure Modes and Mitigations

| Failure | Mitigation |
|------|-----------|
| Insufficient data | Skip training, mark as `failed_insufficient_data` |
| Training job failure | Persist error, allow retry |
| Quality regression | Roll back to previous version |
| Excessive cost | Cap dataset size and frequency |
| Privacy concern | Immediate disable + fallback |

---

## 14 Open Questions

- Minimum number of messages required to justify training?
  - **Openai:** Require at least 500 sent messages and 10k tokens in the 90-day window; otherwise mark `failed_insufficient_data`.
- Preferred base model for cost vs quality tradeoff?
  - **Openai:** Use `gpt-4o-mini` for initial rollout; allow override via config for future upgrades.
- Retrain cadence: time-based or delta-based?
  - **Openai:** Use a hybrid rule: weekly schedule **and** require ≥20% new messages since last training to proceed.
- Combine fine-tuning with lightweight prompt-based personalization?
  - **Openai:** Yes—prepend a short system prompt at inference time to enforce safety and verbosity caps, but keep stylistic learning in the fine-tuned model.
- Should we support multi-version A/B testing per user?
  - **Openai:** Not in v1; keep a single active model with rollback to previous version on regression.
