# Muse Hello 👋 — TRMNL Plugin

![Preview](preview.png)

Push anything from your Muse to your TRMNL e-ink display. A title, a message, and an optional image — no server, no schedule, just your agent talking to your wall.

## How it works

```
Your Muse → POSTs to TRMNL webhook → your e-ink display
```

Unlike Agent Says (daily briefing), this one is freeform. Your Muse pushes whatever you ask, whenever you ask.

## Setup

### 1. Create a Private Plugin on TRMNL

1. Go [trmnl.com](https://trmnl.com) → **Plugins** → **Add New** → **Private Plugin**
2. Strategy: **Webhook**
3. Name it (e.g., "Muse Hello")
4. Copy the **Webhook URL** — you'll give this to your Muse
5. Paste `template.liquid` into the **Markup** field
6. Set layout to `full`

### 2. Tell your Muse

Give your Muse the webhook URL and say something like:

> Here's my TRMNL webhook URL: `https://trmnl.com/api/custom_plugins/YOUR_PLUGIN_UUID`
>
> When I ask you to put something on my TRMNL, POST this JSON:
> ```json
> {
>   "merge_variables": {
>     "title": "the headline",
>     "body": "the message",
>     "image_url": "optional public image URL"
>   }
> }
> ```
>
> The image has to be publicly reachable with permissive cross-origin headers — raw GitHub URLs work great.

Then just say "put this on my TRMNL" whenever you want.

## Webhook format

```json
{
  "merge_variables": {
    "title": "Hello from Muse",
    "body": "My TRMNL is connected.",
    "image_url": "https://raw.githubusercontent.com/YOU/trmnl-assets/main/portrait.jpg"
  }
}
```

| Variable | Required | Description |
|----------|----------|-------------|
| `title` | Yes | Headline text |
| `body` | Yes | Message text |
| `image_url` | No | Public image URL (shown at 220×220). Must be fetchable by TRMNL's renderer — avoid hosts that send `cross-origin-resource-policy: same-origin`. |

## Image hosting tips

TRMNL renders your markup server-side, so the image URL must be publicly fetchable **without restrictive CORS/CORP headers**. What works:

- Raw GitHub URLs (`raw.githubusercontent.com`) — permissive headers, reliable
- Your own domain

What doesn't:

- Expiring share links (Muse file storage, etc.)
- Hosts that send `cross-origin-resource-policy: same-origin`

Keep images small (under ~50KB, square-ish) — e-ink is 1-bit and the display is 800×480.

## License

MIT
