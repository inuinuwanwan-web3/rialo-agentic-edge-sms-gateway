# DevNet mock delivery verification

## Verified result (2026-09-24 UTC)

One official CLI `create-http-post-rex` request was created on Rialo DevNet.
This exercises the native HTTP POST REX path without deploying a new Venus
program. It verifies Relay reachability and an on-chain REX result; it does not
claim to update a Venus workflow's custom state.

- CLI: `rialo 0.18.1-2e1fdefe31cc`
- Public endpoint: `https://temporary-relay.example.invalid/sms/deliver`
- External HTTPS probe: HTTP 200, `mock_608dad68831440c8a161804e576e1b0a`, `delivered`
- DevNet nonce: `sms-relay-20260924-01`
- Creation signature: `2wekKn7FBXWx5e8oRpgVujhhAUHxH8g3hcPoUMi653ojkEt99k4SKJAuXmcTmrHdFyAEcWPoFHqrScZtpVYunP8m`
- Creation status: executed, no error, slot `20231735`
- REX configuration: `OneShot`, one validator, plaintext dummy payload, empty headers
- REX report round: `20231741`
- REX response TEE timestamp: `2026-09-24T13:39:41.899105Z`
- REX response: `{"message_id":"mock_108c24761b28479a9429bae65cd7a9e5","status":"delivered"}`
- Lineage: successful root transaction, no subscriptions or child transactions.
  The delivery JSON is in the REX report, not in the lineage tree.

Only one DevNet POST creation command was executed. The free faucet request
timed out while waiting for confirmation, but a balance read confirmed 1 RLO;
the faucet request was not repeated. No SMS provider or tunnel credential was
configured. Rialo uses its existing local DevNet signing key internally; its
value was not displayed or included in the request. Mock delivery is not a real
SMS delivery confirmation.

## HTTPS setup used

Cloudflare Quick Tunnels are free, temporary, and do not require an account:
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/

The official cloudflared Linux amd64 binary was downloaded to
`/tmp/sms-relay-cloudflared` (version `2026.9.1`). No system service was installed.
The following processes were started separately:

```sh
cd rialo-agentic-edge-sms-gateway
env -u SMS_PROVIDER_API_CREDENTIAL SMS_PROVIDER=mock SMS_RELAY_HOST=127.0.0.1 SMS_RELAY_PORT=8080 python3 -m sms_relay.server
```

```sh
/tmp/sms-relay-cloudflared tunnel --no-autoupdate --url http://127.0.0.1:8080
```

The public URL exists only while the tunnel remains running. Restarting the
tunnel generates a new URL. Stop the Relay and tunnel with Ctrl-C in their
respective terminals when the test is finished. The local Relay uses HTTP on
loopback; the public endpoint uses HTTPS. No paid resources were provisioned.

## Minimal DevNet procedure

Check the actual public URL from the running tunnel. Use only dummy data and
keep the adapter set to `mock`. Verify an external HTTPS POST first:

```sh
curl --fail --silent --show-error --max-time 30 \
  https://temporary-relay.example.invalid/sms/deliver \
  -H 'Content-Type: application/json' \
  --data '{"to":"+12025550101","from":"+12025550102","message":"External HTTPS mock probe"}'
```

The following records the **already executed** DevNet creation command; the temporary hostname has been replaced with a non-routable documentation placeholder.
Do not rerun it to inspect results. For a separately authorized new experiment,
use the current public URL and a fresh nonce of at most 32 UTF-8 bytes.

```sh
rialo --no-setup --network devnet --json client create-http-post-rex \
  https://temporary-relay.example.invalid/sms/deliver \
  '{"to":"+12025550101","from":"+12025550102","message":"Rialo DevNet mock probe sms-relay-20260924-01"}' \
  application/json sms-relay-20260924-01 --validators-per-duty 1
```

Read the existing result without sending another POST:

```sh
rialo --no-setup --network devnet --json client rex info \
  --nonce-str sms-relay-20260924-01
rialo --no-setup --network devnet --json client get-workflow-lineage \
  2wekKn7FBXWx5e8oRpgVujhhAUHxH8g3hcPoUMi653ojkEt99k4SKJAuXmcTmrHdFyAEcWPoFHqrScZtpVYunP8m \
  --full-id true --include-events true
```

`rex_report.updates[].data` contains serialized REX output, not a bare JSON
document. The exact observed update bytes are retained in
`verification/devnet-20260924.json`, along with a decoded response summary.
The summary is a local observation record, not an independently verified proof.

## Remaining Venus integration

The demonstrated route is CLI → DevNet transaction → native HTTP POST REX →
Mock Relay → JSON → on-chain REX report. A Venus workflow can be the next
separate stage: use its HTTP POST operation and adapt the handler to persist
`message_id` and `status`. The previous multi-http-post response schema and its
parse-error success fallback must not be used as confirmation of delivery.
No AGP, Latch, or rialo-first files were changed for this verification.
