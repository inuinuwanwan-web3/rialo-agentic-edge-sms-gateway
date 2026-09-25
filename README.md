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
