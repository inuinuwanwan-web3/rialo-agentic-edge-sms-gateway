# Rialo Agentic Edge SMS Gateway

Date: 2026-09-25

Rialo CLI 0.18.1 (recorded build: `0.18.1-2e1fdefe31cc`).

Rialo DevNet / Venus / REX based SMS Gateway prototype with HTTPS relay,
mock provider, workflow experiments, and verification evidence.

Agentic Edge Harness Send Email Gateway was investigated, as reported in the
project handoff. SMS Gateway was implemented as an independent prototype.
This repository archives the existing SMS implementation and evidence; it does
not include a separate saved report of the Send Email Gateway investigation.
AGP, Latch, rialo-first, and the existing rialo-agp-latch repository are separate
projects and were not modified for this publication.

## 2026-09-27 SMS Gateway implementation boundary

### Publication scope

This section records implementation and offline verification completed in the
local SMS prototype on 2026-09-27. It does not publish those local source changes
or raw observation evidence. The archived source and usage instructions elsewhere
in this checkout therefore do not yet include the policy boundary, observation
modules, or offline verdict described below. This is a progress record, not a
claim that the published checkout reproduces all 54 tests.

### Completed locally

- A fail-closed local policy boundary calls the mock provider only for an explicit
  `ALLOW`. `DENY`, a missing decision, an invalid decision, and a decision exception
  each result in **0 provider calls**. This is a trusted local injection boundary,
  **not an authenticated connection to an actual REX policy decision**. A future
  REX integration must verify and bind its decision to the request. The local CLI
  supplies no decision and consequently denies delivery by default.
- The offline evidence verdict distinguishes **PASS**, **FAIL**, and
  **INSUFFICIENT_EVIDENCE**. PASS requires a successful start matched to the run,
  a successful handler matched to the workflow, matching report/state/message ID
  evidence, and no ambiguous or conflicting evidence. An explicit matched
  transaction failure yields FAIL. Missing evidence, RPC acquisition errors,
  correlation mismatches, conflicts, and multiple starts are not automatically
  treated as failures; the relevant evidence-insufficient cases are covered.
- The implementation boundary includes the mock provider, input validation,
  secret protection, local policy boundary, observability, transaction
  correlation, REX report/callback/workflow-state handling, and offline verdict.
  These are prototype capabilities, not official Send SMS compatibility claims.

### Offline verification

- New verdict tests: **15 passed / 0 failed**.
- Full suite: **54 passed / 0 failed** — Python **51**, Rust **3**.
- Python tests ran with network socket creation blocked; no network attempts
  occurred. Rust tests used Cargo offline mode.
- During this implementation verification: external network communication **0**,
  real SMS sends **0**, real Email sends **0**, DevNet transactions **0**.
- The saved September 25 success-run evidence receives
  `INSUFFICIENT_EVIDENCE / RPC_ERRORS_OR_UNKNOWN_COVERAGE` from the stricter new
  verdict. This does not change the historical observations above into FAIL.
- Mock `delivered` and an offline PASS do not prove actual SMS delivery,
  confidential policy enforcement, or official Gateway integration.

### Unverified boundary and resumption condition

As checked on 2026-09-27, the [official Agentic Edge Harness](https://agents.rialo.io/)
labels Send SMS **Coming Soon**. The information reviewed does not establish the
formal SMS API, policy-decision format and verification, credential integration,
carrier delivery-result contract, or transaction/workflow correlation identifiers
needed to connect this prototype without assumptions. The review did not exhaust
all possible public material; it makes no claim of compatibility with unpublished
specifications. Validator dispatch and assignment remain subject to the evidence
limitations already recorded above.

**Current status: waiting for official Send SMS publication.** Resume when Rialo
Send SMS is Live and public specifications are available for the API, policy
decision, credential handling, delivery result, and transaction/workflow
correlation. Do not invent these contracts or repeat mock/observability work as
new integration evidence. No new live SMS, Email, or DevNet action was performed
to publish this record; GitHub synchronization is separate from the zero-network
offline verification above.

## Verified status and remaining blocker

The following results are historical observations from 2026-09-24, recorded in
[the native REX run](DEVNET_RUN.md), [its evidence](verification/devnet-20260924.json),
and [the Venus 5000ms summary](verification/venus-5000-20260924/summary.json).
Publication on 2026-09-25 does not rerun DevNet operations or tests.

- **Proven:** Rialo DevNet → REX → HTTPS Relay → MockProvider → response.
  The native HTTP POST REX report contains the mock response.
- **Incomplete:** Venus workflow → REX report → callback → workflow state persistence.
- **Current blocker:** the 5000ms version produced no observed REX report or callback;
  state remained empty after the subscription active commit range ended.
  The cause is unconfirmed; this is not an observed Timeout report.
- Relay tests: **8/8 PASS** (recorded).
- Venus tests: **PASS**, 3/3 (recorded).
- Artifact build: **PASS** (recorded). The existing local PolkaVM artifact SHA-256
  matches the recorded `a6ec33e586aae34902dcce8711275175d943596e301ff3a829b2541ab8d0093e`.
  Build sources, lockfile, generated WIT/manifest and build instructions are included;
  generated binaries and `target/` are excluded.
- DevNet deployment has succeeded; DevNet `start` invoke succeeded.
- Real SMS sends = **0**. Secret exposure = **0** in the recorded experiments;
  publication scanning found no actual credentials in the selected files.
- Cloudflare Quick Tunnel URLs are temporary, **not permanent URLs**.
- Mock `"delivered"` does **not** mean a real SMS was delivered.
- The relationship to **RIALO Points / airdrop credit is unverified**.

## 2026-09-27: final read-only evidence review

The final read-only review confirmed the following successful run:
`verification/2026-09-25-3e4a2c490dc24e0388eb934322f9a9c2/`.
This is a reference to the local evidence directory; its raw logs are not
included in this publication. Results below are the confirmed review findings,
not a new execution performed to publish this update.

- `start_success`: **true**; `handler_success`: **true**.
- `response_report_match`: **true**; `response_state_match`: **true**.
- `start_correlation_matched`: **true**; `missed_duties`: **[]**.
- `state_saved`: **matched**.
- Observed boundaries: `start`, `rex_creation`, `relay_arrival`, `response_sent`,
  `report`, `event`, and `callback`; `state_saved`: **matched**.
- `assignment`: **not_observed**.
- `dispatch`: **unknown_requires_validator_logs**.
- The run instrumented with the 5000ms measurement: **PASS** in this review.

This successful run supersedes the earlier incomplete status as the latest
result; it does not establish the direct root cause of the historical failed
runs. That root cause remains unconfirmed because validator logs are missing.
Assignment and dispatch must not be described as observed or proven.

No new `start`, deployment, invoke, Relay POST, or real SMS send was performed
for this final read-only review or publication. Mock-provider success is not
proof of real SMS delivery. Only this summary is added; raw verification logs,
phone numbers, credentials, tunnel secrets, and private keys are not added.

## 2026-09-27: Harness Email delivery and DevNet correlation audit

### Email E2E: PASS

One real email was sent through the public Rialo Agentic Edge Harness Send Email
interface. This is an Email Gateway observation, separate from the SMS prototype
and its mock-provider verification above.

- Sender label: `test-agent`.
- Test message: `Rialo Agentic Edge test 2026-09-27`.
- Send count: **1**.
- Timestamp: **2026-09-27 18:41:15 JST / 09:41:15 UTC**.
- Harness UI: **Email sent successfully**.
- Request Log: **accepted**; Delivery Log: **delivered**.
- Actual email receipt: **confirmed by the user**.
- Public request-log timestamp, sender label, and message matched the reported
  send; recipient address and raw log/response contents are omitted.

### On-chain correlation: UNCONFIRMED

Read-only DevNet block-time lookup identified:

- Nearest block height: **21740671**.
- Nearest block time: **2026-09-27 09:41:15 UTC**.
- Search window: **2026-09-27 09:36:00–09:46:00 UTC**.
- Corresponding block range: **21738787–21742224**.

The matching block timestamp does not identify the email transaction. Public
Harness logs did not provide a transaction signature, workflow ID, or REX ID
that directly correlates this email with a specific DevNet transaction.
Five transaction metadata entries were obtained at the target-time block;
none was established as the matching email transaction. Full-range metadata
inspection remained incomplete. Further exhaustive RPC enumeration was stopped
for efficiency after prolonged response waits.

Transaction, workflow, REX, callback/event, and workflow-state correlation remain
**unconfirmed**. This does **not** establish that no on-chain record exists.
No claim is made that a transaction was confirmed for this email, that Rialo
 evaluated this activity, or that it qualifies for points or rewards.

### Completion boundary and next resumption conditions

Email delivery verification is complete; do not resend the email merely to
repeat this check. Resume on-chain investigation only when a new correlation
anchor is available: a Harness backend transaction signature, workflow/REX ID,
request-to-transaction mapping, or a documented gateway program/account plus
matching instruction/event evidence. Require a match beyond timestamp alone.
Keep multiple plausible transactions as candidates until uniquely correlated.
Do not resume broad RPC enumeration without new evidence or a targeted query.

The audit performed **0 new live actions** and modified **0 files**; its network
operations were read-only. This documentation update does not resend email or
perform DevNet actions. No recipient address, credentials, private keys, raw
verification logs, or runtime data are included.

## Publication scope and privacy

Files originate from the existing `sms-relay-prototype` directory, with its
`venus-sms`, `tests`, and `verification` subdirectories preserved. The root README
and existing documentation were edited for publication; no missing experiment
results or implementation files were invented. See [Venus build/test commands](venus-sms/README.md#build-and-test)
and the Relay commands below. DevNet commands are historical instructions and
were not executed during this GitHub recording work.

A filename/content scan and review of credential-related fields, URLs, and
encoded RPC payloads found no actual API key, private key, wallet secret,
provider credential, Cloudflare credential, or personal contact data in the
publication set. This is a scoped review of these files, not a claim about all
files on the host. The empty `.env.example` credential setting and clearly named
`SYNTHETIC_*_CANARY` test markers are not real credentials.

Public evidence was minimized as follows:

- Replaced the temporary Tunnel hostname in `DEVNET_RUN.md`,
  `verification/devnet-20260924.json`, and the URL byte array in
  `verification/venus-5000-20260924/rex.json` with
  `https://temporary-relay.example.invalid/sms/deliver`. This is a documentation
  placeholder, not an operational endpoint.
- Replaced the public signer in the two `creator` fields of `rex.json` and
  `start_metadata.json` log messages with `REDACTED_PUBLIC_SIGNER`.
- Removed `transaction_metadata.innerInstructions` from `start_metadata.json`
  (five encoded instructions), including encoded copies of the URL and account
  identifiers. This reduces raw instruction replay/decoding evidence; status,
  logs, compute usage, lineage, REX settings and workflow state evidence remain.
- **No transaction signatures were removed.** Native REX creation, deployment,
  and Venus start signatures remain because they identify historical public
  transactions for verification. Program/workflow/subscription/REX identifiers
  necessary to correlate results are also public chain identifiers, not secrets.
- Dummy `+12025550101` / `+12025550102` test numbers and mock message IDs remain.
  No real recipient data is included.

The JSON files with redactions are edited evidence, not byte-for-byte raw RPC
exports. Original local files remain unchanged. Existing `.git/`, Python caches,
Cargo `target/`, binaries, private configuration, and `/tmp` contents are excluded.
References to historical `/tmp` tool paths in the run notes are documentation
only; no `/tmp` files are published.

## Relay implementation

Independent mock-only delivery endpoint. Python 3.10+; no third-party packages.

## Run

```sh
cd rialo-agentic-edge-sms-gateway
python3 -m sms_relay.server
```

Default endpoint: `POST http://127.0.0.1:8080/sms/deliver`.
Set `SMS_RELAY_HOST` / `SMS_RELAY_PORT` in the process environment to change binding.
`.env.example` documents configuration; no `.env` file is created or auto-loaded.

```sh
curl -X POST http://127.0.0.1:8080/sms/deliver \
  -H 'Content-Type: application/json' \
  -d '{"to":"+12025550101","from":"+12025550102","message":"Mock SMS"}'
```

Success is HTTP 200 with exactly `message_id` and `status`:

```json
{"message_id":"mock_<generated UUID>","status":"delivered"}
```

`delivered` is a **simulated result**, not evidence of SMS delivery. Every accepted
request produces a new ID; retries are separate mock deliveries.
Both phone fields must use E.164 syntax (ASCII `+`, nonzero leading digit,
2–15 digits). This checks syntax only, not whether a number exists.
`message` must be a nonempty string. Extra fields are rejected. JSON request
bodies are limited to 64 KiB. Invalid input returns HTTP 400 with a fixed error;
wrong content type returns 415, oversized input 413, provider failure 502.

## Boundary and credentials

`SmsProvider.deliver(to, from_, message)` is the adapter boundary in
`sms_relay/providers.py`. `build_provider` constructs the selected adapter.
Only `mock` is implemented; selecting any other provider fails at startup.
`SMS_PROVIDER_API_CREDENTIAL` is read from the Relay process environment into a
configuration field excluded from its representation. Mock does not use it.
A future adapter must receive the credential at construction, never via HTTP
request fields, Rialo transaction arguments, workflow state, logs, or source code.
No actual credentials belong in `.env.example`. `.env` and its variants are ignored.

The server does not log request bodies, headers, URLs, or provider exception text.
Provider errors return only a fixed error code. It does not persist requests.
Do not put secrets in `message` or phone fields: these are delivery data, not
credential channels. Relay code cannot enforce how a future Rialo caller records
its own transaction inputs or results.

## Rialo integration boundary

Planned route: Agent/CLI → Rialo DevNet transaction → Venus HTTP POST → this
Relay → provider adapter → JSON response → Rialo workflow/result.
Use `application/json` with the three fields above. The independent Venus implementation and historical deployment records are included
in `venus-sms/` and `verification/`. Localhost is not reachable from remote REX nodes; DevNet
integration needs an externally reachable Relay URL. This prototype has no caller
authentication or policy layer and must remain mock-only at this stage.

The existing `multi-http-post` generic `SubmissionResponse` expects `success` and
`id`; its response handler must later be adapted to this endpoint's `message_id`
and `status`. Do not treat its parse-error fallback as delivery confirmation.
No rate limit, blocked-sender rule, or disallowed-word policy is implemented.
No SMS provider traffic or Mainnet interaction occurs.

The first DevNet native HTTP POST REX round trip succeeded. See
[DEVNET_RUN.md](DEVNET_RUN.md) for the redacted temporary HTTPS URL, transaction signature,
REX report result, exact commands, and the distinction from a Venus state update.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

Tests cover HTTP requests, phone/message validation, mock delivery and JSON shape,
adapter substitution and error redaction, synthetic credential non-disclosure,
and `.env` ignore rules using an isolated temporary Git repository.
