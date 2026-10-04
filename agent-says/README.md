# Agent Says 🤖 — TRMNL Plugin

![Preview](preview.png)

Send an explicitly approved message and up to five priorities from Rusty to your existing TRMNL Agent Says display. Nothing reads private chats or memory, and no recurring job is installed.

## Current Rusty publisher

Rusty uses its managed GitHub connection to send a `repository_dispatch` event to `AndreaGriffiths11/trmnl-plugins`. GitHub Actions validates that payload and forwards it to the existing `TRMNL_WEBHOOK_URL` Actions secret. The workflow does not generate canned text or scrape repository issues.

The event name and display name are labels, not agent authentication. GitHub repository permissions control who can dispatch; the webhook secret identifies the receiving plugin.

### Before first delivery

Verify the existing Agent Says private plugin in the owner's signed-in TRMNL account. Keep its webhook URL in the repository Actions secret, never in chat, source files, dispatch payloads, or logs. Install the current `template.liquid` in its full-layout markup; it escapes message text. Do not create a replacement plugin merely because a past delivery failed.

### Publish an approved message

Only after the recipient is verified and the owner approves the message, Rusty can run this using its existing managed `gh` credential:

```sh
gh api --method POST repos/AndreaGriffiths11/trmnl-plugins/dispatches --input - <<'JSON'
{
  "event_type": "rusty_agent_says",
  "client_payload": {
    "message": "Hello Andrea — Rusty is connected.",
    "priorities": []
  }
}
JSON
```

This command sends a real display update. The workflow must be on the default branch. Do not use `gh workflow run`: this publisher accepts `repository_dispatch`, not `workflow_dispatch`.

- `message` is required, 1–800 characters.
- `priorities` is optional, an array of up to five nonempty strings, each at most 100 characters.
- Control characters and extra fields are rejected. The complete outbound JSON must fit within 2,000 UTF-8 bytes.
- The workflow sets Rusty's name, signature, UTC date, and all five priority slots. Empty slots clear priorities from an earlier message.
- No private conversation, memory, or work content should be included without explicit approval. Dispatch data is sent to GitHub as well as TRMNL.

A successful dispatch response only means GitHub accepted the event. Check the resulting Actions run for TRMNL's HTTP acceptance. Confirm the physical display separately. The publisher makes one request without automatic retries or redirects and does not print message text, webhook URLs, or response bodies.

Run the offline tests before changing the workflow:

```sh
python3 -m unittest discover -s tests -v
```

## Webhook format

```json
{
  "merge_variables": {
    "agent_name": "Rusty",
    "message": "Four takes to get a clean demo. The fifth one was honest.",
    "signature": "— Rusty 🦀",
    "date": "Mar 16, 2026",
    "priority_1": "Fix Railway env vars",
    "priority_2": "Test checkout flow end-to-end",
    "priority_3": "Ship the TRMNL plugins repo"
  }
}
```

| Variable | Required | Description |
|----------|----------|-------------|
| `agent_name` | No | Display name (default: "Agent") |
| `message` | Yes | The daily message — from your agent's context |
| `signature` | No | Sign-off line (default: agent_name) |
| `date` | Yes | Display date |
| `priority_1` — `priority_5` | No | Today's priorities (only non-empty ones show) |

## License

MIT
