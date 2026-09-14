# School Vault

Every page from **Toddle** (all classes) and **Canvas** (CS HL, Pamoja) mirrored into
markdown that lives in this private repo, readable from any device, and exposed to
claude.ai as persistent memory.

```
GitHub Actions (06:00 Berlin daily + manual + API)
  └─ scraper → markdown → commit → push
       │
       ▼
  THIS REPO = the vault
       ├─ Obsidian on the PC          (Obsidian Git plugin)
       ├─ GitHub app on the phone     (read anything, edit notes/)
       └─ MCP server on Hetzner       → claude.ai custom connector
```

**The repo is the state.** Nothing lives only on the server. If the server dies you
lose nothing — rebuild it in ten minutes from [Deploying the MCP server](#deploying-the-mcp-server-from-a-blank-ubuntu-box).

---

## What's in here

```
context.md          regenerated every sync: due in 14 days, latest announcement per class
changes/            2026-09-14.md — what was new, edited, or had its deadline moved
canvas/cs-hl/       assignments, announcements, modules, raw/
toddle/             school/announcements/, <class>/tasks/, raw/
attachments/        content-hashed, append-only, never deleted
notes/              YOURS. The scraper is blocked from writing here, in code.
sync_state.json     watermarks and item counts per source
scraper/            the scrapers (runs on GitHub Actions)
server/             the MCP server (runs on Hetzner)
```

Every note carries frontmatter — `id`, `class`, `type`, `due`, `author`, `url`,
`content_hash` — which is what makes search and change-detection work.

## Guarantees, enforced in code rather than promised in comments

| Rule | Where it lives |
|---|---|
| The scraper can only write `toddle/ canvas/ attachments/ changes/ context.md sync_state.json`. `notes/` is yours. | `scraper/vault.py` → `guard()`, applied to every write **and every delete** |
| Teacher text is verbatim. HTML→markdown only, never summarised or trimmed. | `vault.html_to_md()`; nothing in the write path shortens a body |
| Raw JSON is saved before anything is parsed. | `canvas.get_all()`, `toddle.gql()` → `raw/` |
| A source losing >50% of its items aborts the run and commits nothing. | `report.check_count()`, called with the full scrape in hand, before the first write |
| Writes are atomic — a killed run never leaves a half-written file. | `vault._atomic()` (temp file + `os.replace`) |
| Toddle is rate-limited to 1 request / 2 s. | `toddle.RATE_LIMIT` |
| Secrets live only in GitHub secrets and `.env`. Tokens are never printed. | `.gitignore`, and errors report variable *names* only |

`uv run scraper/selfcheck.py` proves the first four. It runs in CI before every scrape,
so a regression stops the scrape instead of corrupting the vault.

---

## Daily operation

Nothing. Actions runs at **04:00 UTC** (06:00 Berlin in summer, 05:00 in winter —
GitHub cron has no timezone) and commits with a message that is itself the changelog:

```
sync 2026-09-14: 3 new, 1 deadline moved

  new       cs-hl   W3 - Boolean logic
  deadline  cs-hl   Paper 2 mock: 2026-09-20 -> 2026-09-27
```

So `git log --oneline` is a readable history of your school year.

---

## Running a manual sync

Three ways, all the same workflow:

1. **From claude.ai** — just ask: *"sync my school stuff"*. Uses the `sync` tool,
   waits for the run, and tells you what changed.
2. **From the GitHub phone app** — repo → **Actions** → **sync** → **Run workflow**.
3. **From a browser** — <https://github.com/arusadusdg/school-vault/actions/workflows/sync.yml>
   → **Run workflow**. You can pick a `scope`: `full`, `announcements`, `tasks`, or
   `class` (with a class slug).

Locally, if you ever want to:

```bash
uv run scraper/sync.py --scope full
```

⚠️ **Don't make a habit of running the scraper on the same machine where Obsidian has
the vault open.** Actions also writes `context.md` and `sync_state.json`, and two
writers produce merge conflicts in generated files. Let Actions own them.

---

## Setup on a fresh machine

You need [git](https://git-scm.com/download/win) and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/arusadusdg/school-vault.git school-vault
cd school-vault
cp .env.example .env
```

Then open `.env` and fill in `CANVAS_TOKEN` (Canvas → Account → Settings → **+ New
Access Token**). The other values are already correct. Check it works:

```bash
uv run scraper/selfcheck.py && uv run scraper/sync.py
```

uv downloads Python 3.12 itself — you don't need Python installed.

### Adding the GitHub secrets

Only needed once, or when a token is rotated.
**Settings → Secrets and variables → Actions → New repository secret**
(<https://github.com/arusadusdg/school-vault/settings/secrets/actions>):

| Secret | Value |
|---|---|
| `CANVAS_TOKEN` | Canvas → Account → Settings → + New Access Token |
| `CANVAS_BASE_URL` | `https://pamojaeducation.instructure.com` |
| `CANVAS_COURSE_ID` | `734` |
| `TODDLE_STORAGE_STATE` | output of `uv run scraper/make_secret.py` — see [Toddle re-auth](#when-toddle-re-auth-is-needed) |

Not secrets, so they sit in `.github/workflows/sync.yml` as plain values:
`CANVAS_CLASS_SLUG`, `TERM_START`, `TODDLE_ACADEMIC_YEAR_ID`.

---

## Deploying the MCP server from a blank Ubuntu box

Currently: Hetzner CX, Helsinki, `62.238.56.217`, hostname `62-238-56-217.sslip.io`.
sslip.io resolves any `a-b-c-d.sslip.io` to that IP, so no domain purchase and no DNS
setup — and Caddy still gets a real Let's Encrypt certificate.

**1 — base packages, Caddy, uv, firewall** (as root):

```bash
apt-get update -qq && apt-get install -y git curl ufw debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt-get update -qq && apt-get install -y caddy
useradd -m -s /bin/bash vault
sudo -u vault bash -lc 'curl -LsSf https://astral.sh/uv/install.sh | sh'
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
```

**2 — deploy key, so the box can pull the private repo:**

```bash
sudo -u vault bash -lc 'ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" && ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts'
cat /home/vault/.ssh/id_ed25519.pub
```

Paste that into **repo → Settings → Deploy keys → Add deploy key**, tick
**Allow write access** (needed by `remember`), then:

```bash
sudo -u vault bash -lc 'git clone git@github.com:arusadusdg/school-vault.git ~/vault && cd ~/vault && ~/.local/bin/uv sync'
```

**3 — the secret URL.** claude.ai's connector screen has nowhere to put a bearer
header, so the token lives in the URL path and Caddy 404s everything else:

```bash
SECRET=$(openssl rand -hex 20)
echo "$SECRET" > /root/mcp-secret.txt && chmod 600 /root/mcp-secret.txt
cat > /etc/caddy/Caddyfile <<EOF
62-238-56-217.sslip.io {
	log {
		output discard
	}
	handle_path /s/${SECRET}/* {
		reverse_proxy 127.0.0.1:8000
	}
	handle {
		respond "not found" 404
	}
}
EOF
```

Access logging is discarded on purpose — otherwise the secret URL would be written to
disk on every request.

**4 — the service:**

```bash
printf 'GITHUB_PAT=\n' > /etc/school-vault.env && chmod 600 /etc/school-vault.env
cat > /etc/systemd/system/vault-mcp.service <<'EOF'
[Unit]
Description=school-vault MCP server
After=network-online.target
Wants=network-online.target

[Service]
User=vault
WorkingDirectory=/home/vault/vault
EnvironmentFile=/etc/school-vault.env
Environment=GITHUB_REPO=arusadusdg/school-vault
Environment=VAULT_REPO=/home/vault/vault
Environment=MCP_HOST=127.0.0.1
Environment=MCP_PORT=8000
Environment=MCP_ALLOWED_HOSTS=62-238-56-217.sslip.io
ExecStart=/home/vault/.local/bin/uv run --project /home/vault/vault server/vault_mcp.py
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable --now vault-mcp && systemctl restart caddy
```

`MCP_ALLOWED_HOSTS` is not optional. Binding to loopback makes FastMCP require a
loopback `Host` header, but Caddy forwards the real hostname — without this every
request returns **421 Misdirected Request**.

**5 — the token for the `sync` tool.** Make a fine-grained PAT at
<https://github.com/settings/personal-access-tokens/new>: **Only select repositories →
school-vault**, **Repository permissions → Actions → Read and write**. Then, from your
PC (this keeps the token out of your shell history on the server):

```bash
printf 'GITHUB_PAT=%s\n' 'YOUR_TOKEN' | ssh root@62.238.56.217 'cat > /etc/school-vault.env && chmod 600 /etc/school-vault.env && systemctl restart vault-mcp'
```

**6 — check it:**

```bash
ssh root@62.238.56.217 'echo https://62-238-56-217.sslip.io/s/$(cat /root/mcp-secret.txt)/mcp'
```

If the server ever moves to a new IP, update the hostname in **both** the Caddyfile and
`MCP_ALLOWED_HOSTS`, then re-add the connector with the new URL.

---

## Adding the connector in claude.ai

1. <https://claude.ai/settings/connectors> → **Add custom connector**
2. **Name:** `School Vault`
3. **URL:** the output of the command in step 6 above
4. **Add**, then in a chat turn **School Vault** on from the tools menu

🔒 **That URL is a password.** Anyone holding it can read your whole vault. To rotate
it: re-run step 3, `systemctl reload caddy`, and edit the connector's URL.

### The seven tools

| Tool | What it does |
|---|---|
| `get_context()` | Due in 14 days + latest announcement per class. Claude calls this first. |
| `recall(query, class_name?)` | Full-text search over everything, returning teachers' own words |
| `open_note(id)` | One item in full, plus anything linking to it |
| `whats_new(since?)` | New / edited / moved-deadline items since you last asked |
| `whats_due(days=14)` | Deadlines, soonest first |
| `remember(title, text)` | Saves a note to `notes/`, commits, pushes |
| `sync(scope, class_name?)` | Runs a scrape now and reports what changed |

---

## Reading the vault

### Obsidian (PC)

1. Clone the repo somewhere permanent, then **Open folder as vault** on that folder
2. Install the community plugin **Git** (by Vinzent) and enable it
3. Settings → **Git**:
   - **Auto pull interval (minutes):** `10`
   - **Vault backup interval (minutes):** `10`
   - **Pull updates on startup:** on
4. Settings → **Files and links** → **Excluded files**: add `scraper`, `server`,
   `.github` so code doesn't clutter search

Leave push **on**. Actions only writes `canvas/ toddle/ changes/ context.md
sync_state.json`; Obsidian only writes `notes/`. Disjoint paths, so git merges both
sides without conflict — as long as you don't also run the scraper locally.

`context.md` is the file to open each morning.

### GitHub app (phone)

Install **GitHub** → open `arusadusdg/school-vault`. Markdown renders natively, so
`context.md` and `changes/` are readable as-is. You can edit files in `notes/` directly
from the app, and **Actions → sync → Run workflow** gives you on-demand sync without
Claude.

---

## When Toddle re-auth is needed

The workflow fails with **"Toddle re-auth needed"**. It writes nothing when this
happens — a dead session can never empty your vault. Takes about two minutes:

```bash
uv run --with playwright playwright install chromium
uv run --with playwright playwright codegen --save-storage=storage_state.json https://web.toddleapp.com
```

Log into Toddle in the window that opens, let it finish loading, click into a class,
then **close the browser window** — that's what writes the file. Then:

```bash
uv run scraper/make_secret.py
```

This keeps only the `toddleapp.com` cookies and drops your Microsoft SSO cookies, which
the scraper never uses and which have no business being uploaded to GitHub. It writes
`toddle_secret.b64`. Open that file, copy all of it, and paste it into the
`TODDLE_STORAGE_STATE` secret (**Update** on the existing one).

Then run the workflow manually to confirm. Your user/org/curriculum IDs are read back
out of the session file itself, so they re-derive automatically — only
`TODDLE_ACADEMIC_YEAR_ID` in `sync.yml` needs a manual change, once each August.

---

## When something breaks

| Symptom | Cause and fix |
|---|---|
| Workflow red, `Canvas returned 401` | Canvas token expired. New token, update the `CANVAS_TOKEN` secret. |
| Workflow red, `Toddle re-auth needed` | See above. Nothing was committed. |
| Workflow red, `ABORT - got N items, last run had M` | The count guard did its job — a portal changed its frontend or returned a partial page. **Do not bypass it.** Check the portal by hand first; the vault still holds the good data. |
| claude.ai says the connector failed | `ssh root@62.238.56.217 'systemctl status vault-mcp caddy'` and `journalctl -u vault-mcp -n 50` |
| Connector returns 421 | `MCP_ALLOWED_HOSTS` doesn't match the hostname Caddy forwards |
| Tools answer with stale data | The server pulls at most once every 60 s. Wait a minute, or `systemctl restart vault-mcp`. |
| Obsidian shows a merge conflict | Something other than Actions wrote a generated file. Keep the remote version and let the next sync regenerate it. |

Costs: Hetzner ~€4.50/month. Actions is free on private repos (2000 min/month; a sync
uses about 2).

---

## Deliberately not built

- **PDF/DOCX text extraction** into sidecar `.md` so `recall` searches inside
  attachments. There are no documents in the vault yet, only images. Worth adding when
  Toddle tasks start carrying files.
- **Scoped runs skip the count-drop guard** on purpose — an `announcements`-only run
  holds fewer items by design and would otherwise look like a collapse.
- Canvas `/files` returns `[]` because Pamoja hides the Files tab from students. Not a
  bug; module items carry the links.
- No grade prediction, no auto-writing assignments, nothing needing an install on the
  school laptop.
