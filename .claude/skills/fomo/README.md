# fomo skill — setup, usage & FAQ

An agent skill for interacting with [fomo.family](https://fomo.family) (a social crypto trading app): market/token research, thesis feeds & analysis, portfolio, quotes, posting theses, and executing swaps.

> ⚠️ **Unofficial & use-at-your-own-risk.** It is not endorsed by fomo, can break without notice, and touches real funds. Read the Security section before using trading. You are responsible for your account and money.

---

## What it can do

| Capability | Needs | Status |
|---|---|---|
| Research: trending, token details, risk warnings, holders, leaderboards | token | ✅ verified live |
| Thesis analysis (read theses + trades + holders + charts) | token | ✅ verified live |
| Portfolio: balances, swaps, watchlist | token | ✅ verified live |
| Swap **quotes** | token | ✅ verified live |
| **Post a thesis** after buying | token | ✅ verified live |
| **Buy** any token (Solana or EVM) | token **+ Solana key** | ✅ built (Solana-origin) |
| **Sell** a Solana token | token **+ Solana key** | ⚠️ built, not yet run with a real key |
| **Sell** an EVM token (ETH/Base/BSC/Monad/Robinhood) | token **+ EVM key** | ⚠️ built, not yet run with a real key |
| Fiat deposit, watchlist edits, transfers, posting comments | — | ❌ not available (no API captured) |

---

## Requirements

- Python 3.9+
- `python3 -m pip install -r scripts/requirements.txt` (`curl_cffi`, `solders`, `eth-account`, `eth-abi`, `rlp`)

`curl_cffi` is **mandatory**: fomo's API is behind Cloudflare bot-protection that blocks normal HTTP clients (plain `curl`/`requests`/`node fetch` get `HTTP 430` even with a valid token). `curl_cffi` impersonates a real browser's TLS fingerprint, which passes.

---

## Setup — the `.env` file (recommended)

All config lives in one file: `scripts/.env` (copy `scripts/.env.example` to `scripts/.env`). It holds your login tokens and, if you want to trade, your signing keys.

```bash
cp scripts/.env.example scripts/.env
```

**1) Tokens.** Two ways:

**Automated (recommended)** — `scripts/login.py` opens a browser, you log in once, and it writes the tokens straight into `.env` for you (no copy-paste). It prints a disclaimer and uses a persistent profile, so later refreshes run headless:
```bash
python3 -m pip install playwright && playwright install chromium   # one-time
python3 scripts/login.py             # a window opens — log in with Google
python3 scripts/login.py --headless  # later: refresh tokens from the saved session
```
- On first run this **creates/fills `.env`** with the token values (keys stay empty).
- `python3 scripts/fomo.py logout` when you're done — wipes the `.env` values, cached session, and browser profile.

> ⚠️ **Don't use your main fomo.family account.** This stores session tokens (and, if you trade, your private key) in plaintext. Use a separate account with limited funds. login.py prints this on every login.

**Keys (only needed to trade):** private keys are **not** in the page (Privy keeps them in a secure enclave) and Privy blocks fully-automated reveal, so there's one human click. `scripts/export_key.py` makes it painless — it drives the browser to the export screen; you click **Export key → Copy key** for a chain, and it captures the key from the clipboard into `.env` (masked; the secret is never printed):
```bash
python3 scripts/export_key.py   # then click Export key + Copy key in the browser
```
Or set a key manually: `python3 scripts/fomo.py set-key solana <key>` / paste into `.env`. Keys don't expire — a one-time step per account.

**Manual** — log into fomo.family, open **DevTools → Console**, and run this to copy three ready-to-paste lines:
```js
copy(`FOMO_ACCESS_TOKEN=${JSON.parse(localStorage.getItem('privy:token'))}
FOMO_REFRESH_TOKEN=${JSON.parse(localStorage.getItem('privy:refresh_token'))}
FOMO_PRIVY_ACCESS_TOKEN=${JSON.parse(localStorage.getItem('privy:pat')||'null')}`)
```
Paste over the matching lines in `.env`.

**2) Keys (only if you'll trade).** Export from fomo/Privy "export wallet" and fill in:
```
FOMO_WALLET_KEY=<solana base58 key>    # buys & Solana sells
FOMO_EVM_KEY=<evm 0x-hex key>          # EVM-token sells
```
Reads, quotes, and thesis posting need **no** keys — leave them blank if you're not trading.

Then verify:
```bash
python3 scripts/fomo.py whoami          # confirms which account resolved
```

- Tokens auto-refresh. The skill caches them in `~/.config/fomo-skill/*.json`; `.env` is the bootstrap. When the refresh token eventually dies, re-paste fresh tokens into `.env` and run `python3 scripts/fomo.py reseed`.
- `.env` is git-ignored. **Never commit it** — it contains tokens and (if set) private keys in plaintext.

### Alternative: paste without a file
```bash
python3 scripts/fomo.py auth '<the JSON from the older snippet>'   # tokens only
python3 scripts/fomo.py set-key solana <key>                       # keys, stored 600
python3 scripts/fomo.py set-key evm    <key>
```

### Multiple accounts

Prefix commands with `FOMO_PROFILE=<name>` — each account gets its own isolated store (`~/.config/fomo-skill/<name>.json`):
```bash
FOMO_PROFILE=alice python3 scripts/fomo.py auth '<alice tokens>'
FOMO_PROFILE=alice python3 scripts/fomo.py whoami
```
No profile → the default account. See [SKILL.md](SKILL.md) for details.

---

## Usage

Research / any endpoint (see `references/endpoints.md` for the full catalog):
```bash
python3 scripts/fomo.py api GET  /watchlist
python3 scripts/fomo.py api POST /proxy/trendingTokens '{}'
```

Quote / execute a swap (token id = `<address>:<chainId>`; amount in raw base units):
```bash
python3 scripts/swap.py     quote   <USDC>:1399811149 <mint>:1399811149 3000000   # Solana / buy
python3 scripts/swap.py     execute <USDC>:1399811149 <mint>:1399811149 3000000
python3 scripts/swap_evm.py quote   <token>:8453 <rawAmount>                       # sell an EVM token
python3 scripts/swap_evm.py execute <token>:8453 <rawAmount>
```

Post a thesis after a buy:
```bash
python3 scripts/fomo.py post-thesis <tokenAddress> <networkId> "your thesis text"
```

---

## Trading & keys

Reads, quotes, and thesis posting work with **just the pasted token — no keys**.

**Executing a swap requires the wallet's private key**, set as an environment variable:
- `FOMO_WALLET_KEY` — base58 Solana secret key (for `swap.py execute`)
- `FOMO_EVM_KEY` — hex EVM private key (for `swap_evm.py execute`)

Export these from fomo/Privy's **"export wallet"** UI. Example:
```bash
FOMO_WALLET_KEY=<sol key> python3 scripts/swap.py execute <USDC>:1399811149 <mint>:1399811149 3000000
```

Set a key only in the shell that runs `execute`; never commit or log it.

---

## Security (read before trading)

This skill is intentionally simple about secrets, which means **you** must be careful:

- Privy tokens are stored **in plaintext** at `~/.config/fomo-skill/*.json` (mode 600). Anyone with read access to that file can act as your fomo account until the tokens expire.
- Private keys are read from **environment variables** and used to sign locally. They are never written to disk by the skill — but env vars can leak via your shell history, process listings, or crash logs. Prefer exporting a key just-in-time and unsetting it after.
- A private key controls **all** funds in that wallet, not just what you're trading. Treat export as high-risk.
- This is an unofficial API on real money. Start with tiny amounts.

---

## FAQ

**Do I need private keys to use this?**
Only to *execute* trades. Research, thesis analysis, portfolio, quotes, and posting theses need only the pasted token.

**Why can't it trade with just my login token, like the website does?**
The website signs transactions inside Privy's embedded-wallet iframe (the key is reconstructed from secret shares in a secure context). There's no way to reproduce that outside the browser, and Privy's server-side signing API requires fomo's private app secret, which we don't have. So the only way to sign a swap headlessly is with the exported key.

**Which token is the login — `privy:token`, `privy:pat`, or the refresh token?**
`privy:token` (the customer access token) is what fomo's API accepts as the bearer. `privy:refresh_token` renews it automatically. `privy:pat` is stored for completeness but unused. The setup snippet grabs all three.

**Can I use it with any fomo account?**
Any account you can **log into** (to grab its tokens) and, for trading, whose keys you can export. You cannot operate on someone else's account you don't control — that's the security boundary, by design.

**Do I need gas / a native token to trade?**
No. Fomo sponsors gas (a grant is passed to its bundler), and all deposits/proceeds are handled in Solana USDC. You just need USDC balance to buy.

**Buying vs selling an EVM token — what's the difference?**
Buying an EVM token spends Solana USDC, so it's a Solana-origin swap (`swap.py`). Selling an EVM token originates on that EVM chain and needs an ERC-4337 signature (`swap_evm.py`) with `FOMO_EVM_KEY`.

**Is there a minimum trade size?**
Yes — about $2 on Solana, $5 on some EVM chains (e.g. Ethereum). The quote returns the exact error if you're under.

**How do deposits work?**
There's no deposit API. "Depositing" means sending USDC/SOL to your wallet address (shown by `whoami`); fiat on-ramp only exists inside the app. Watch `balances` for arrival.

**I get `HTTP 430` / `unauthorized` even with a valid token.**
You're not using the browser-TLS client. Always go through `fomo.py`/`swap*.py` (which use `curl_cffi`); never hand-roll `curl`. If it persists, Cloudflare may have tightened fingerprinting — bump `IMPERSONATE` in `fomo.py` to a newer Chrome.

**Thesis post failed with a 500.**
That endpoint flakes intermittently; `post-thesis` retries once. If it still fails, it genuinely didn't post — try again shortly.

**My commands stopped working after ~an hour.**
The access token expired and refresh failed (refresh tokens expire too). Re-run the setup snippet + `fomo.py auth`.

**Does this run headless / in automation?**
Yes for reads and trading, as long as valid tokens (and keys, for trading) are present. The only manual step is periodically re-pasting tokens when the refresh token expires.

---

## Files
- `SKILL.md` — the agent-facing instructions (endpoints, playbooks, trading rules).
- `scripts/fomo.py` — auth, refresh, whoami, generic API calls, `resolve-trade`, `post-thesis`.
- `scripts/swap.py` — Solana swap quote/execute/status.
- `scripts/swap_evm.py` — EVM-token sell quote/execute (ERC-4337 v0.8).
- `references/endpoints.md` — full API catalog with request/response shapes.
