---
name: fomo-sapiens
description: Fomo Sapiens — research, trade, and write theses on fomo.family (social crypto trading app). Market/token research, thesis analysis, portfolio, deposits, and live trading (Solana + EVM swaps). Use when the user mentions fomo, fomo.family, trading memecoins, thesis feeds, or their fomo portfolio.
---

# Fomo Sapiens

A reverse-engineered agent client for the fomo.family private API (captured & verified live 2026-09-01). Python scripts live in `scripts/`; full endpoint catalog with request/response shapes in `references/endpoints.md` — **read it before calling unfamiliar endpoints**.

## What you can do (and how to ask)

The user talks in plain language; map their intent to the actions below. If they seem new or unsure, offer this menu and start with **"set me up."**

| The user says… | You do |
|---|---|
| "set me up" / "log me in" / first use | Run the **Onboarding** steps below (login → relay balance/deposit → optionally export keys). |
| "what's my balance / portfolio?" | `python3 scripts/fomo.py balances` and report total + holdings. |
| "where do I deposit?" / "add funds" | Show the Solana + EVM deposit addresses (`balances` has them); funds convert to Solana USDC. |
| "what's trending?" | `POST /proxy/trendingTokens`. |
| "research X" / "what's the thesis on X?" | Run the **Thesis analysis playbook** (details, warnings, holders, theses, chart). |
| "research the top N trending tokens and tell me why they go up" | `trendingTokens` → take the top N → run the **Thesis analysis playbook** on each → synthesize per-token drivers (see the **Trending research** example). |
| "buy $N of X" | Resolve the token+chain, check warnings, quote, then `swap.py execute` — no confirmation step (see **Trading**). After it fills, *ask* if they want a thesis — never auto-post. |
| "sell X" / "sell 50% of X" | Read the balance, compute the raw amount, `swap.py` (Solana) or `swap_evm.py` (EVM). Just sell — no confirmation step. |
| "post a thesis for X" | Read others' theses first, then `fomo.py post-thesis` (show the text as you post it; don't block on approval). |
| "who's winning?" / leaderboard | `GET /v2/leaderboard[/24h|/7d|/30d]`. |
| "how am I doing?" / "my stats" / "agent leaderboard" | `python3 scripts/fomo.py ledger status` (own PnL/volume) or `GET <LEDGER_URL>/leaderboard` — the **agent ledger**, see below. |
| "stop tracking my trades" / "opt out" | `python3 scripts/fomo.py ledger off` (deletes the agent + its trades server-side, stops reporting). `ledger on` re-enables. |
| "log me out" | `python3 scripts/fomo.py logout` (wipes tokens, keys, session; the ledger opt-out choice persists). |

**First-time / no-clue path:** (1) "set me up" → onboarding (any Google account works — no fomo account needed beforehand; one is created on first sign-in); (2) deposit USDC to the shown address; (3) "what's trending?" or "research \<token\>"; (4) "buy $5 of \<token\>"; (5) optionally have it post a thesis — it asks first, never auto-posts. The skill executes without asking for confirmation, so the user should state exact amounts. Always start tiny.

## Onboarding — guide the user through these steps, in order

Walk a new user through setup one step at a time; relay each result in chat before moving on.

1. **Bootstrap** (once): `bash scripts/bootstrap.sh` (Windows: `powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1`). It finds Python ≥ 3.9 or **installs one if the machine has none** (Homebrew / apt / dnf / winget, else a standalone `uv`-managed Python — no admin rights needed), builds a private venv in `~/.config/fomo-sapiens/venv`, and installs all deps plus Playwright + Chromium. Idempotent. Afterwards every `python3 scripts/...` command below works unchanged: the scripts re-exec into that venv automatically. If any script ever prints `Fomo Sapiens: Missing Python packages` or `python3: command not found`, run the bootstrap — don't hand-install.
2. **Log in**: `python3 scripts/login.py` → a browser opens; tell the user to log in with Google. **The Google account does NOT need an existing fomo account** — if it has never been used on fomo.family, signing in creates a brand-new fomo account from scratch (fresh handle + embedded Solana/EVM wallets, $0 balance). Tell the user this up front so they can use a throwaway Google account; the rest of onboarding is identical (an empty new account just needs a deposit, step 3). If it doesn't capture within ~20s after they log in, stop it and run `python3 scripts/login.py --headless`.
3. **Relay in chat** (login.py prints all of it): the **account handle**, the **balance**, and the **ledger line** — login auto-registers the account on the agent ledger under its fomo handle (`[ledger] registered as agent '<handle>' …`); tell the user in one sentence that their trades will be tracked for PnL/leaderboard and that `ledger off` opts out at any time. If the line says registration failed, say so and move on — it's non-fatal and retried on the next login/trade. **If the account is empty, show the deposit addresses** (Solana + EVM) and tell them to deposit ≥ their intended trade size (funds convert to Solana USDC).
4. **MANDATORY after login — ask which mode they want (always show this message).** Right after relaying the balance, tell the user Fomo Sapiens can run in two modes and ask which they'd like:
   - **Analysis & social — no keys, works right now with just the login:** research any token (trending, details, scam/risk warnings, holders, price history), read and analyze the community's theses, **post your own thesis**, see your portfolio/balances and deposit addresses, get price **quotes**, and browse leaderboards. Nothing is signed and no private key is touched.
   - **Trading (buy & sell) — needs your signing keys.** Explain *why*: executing a swap has to sign a transaction, and fomo signs inside the Privy wallet in the browser; there's no server-side signing available to us, so the only way to trade from here is to pull the wallet's private keys. Reassure them the keys are **kept encrypted locally** — exported straight into a Fernet-encrypted store, the encryption key held in a separate file outside the project, decrypted only in memory at the moment of signing, never written in plaintext and never sent anywhere.

   **Do not pull keys unless the user opts into trading.** If they choose analysis only, skip the key step and go straight to research / thesis work.
5. **Only if the user enabled trading — pull the keys:** run `python3 scripts/export_key.py` (default = both; always both, so a later EVM sell doesn't stall). **A visible browser window opens and drives itself (~1-3 min) — tell the user up front NOT to click anything in that window until it finishes or they're explicitly prompted** (a stray click can interrupt the automated capture). It stores both keys **encrypted**. If it can't capture automatically after 3 tries (e.g. Privy rate-limits the export), it prompts the user to click **Export key → Copy key** on the **Solana address** and then a **Base (EVM) address** themselves (they paste nothing; the plain **"Copy"** button copies only the public address — use **"Copy key"**). It exits non-zero if a key is still missing — re-run `python3 scripts/export_key.py <missing chain>` (or `both`); don't start a trade with a missing key.
6. **Trade / research** as requested (see below). The swap scripts decrypt the keys just-in-time to sign; run `python3 scripts/fomo.py show-account` and reveal the raw keys in chat only if the user explicitly asks — they otherwise stay encrypted at rest.
7. **Keep the session alive between turns and sessions** — never log out on your own, not after a trade, not at the end of a conversation. Only when the user *explicitly* asks ("log me out", "wipe my keys") run `python3 scripts/fomo.py logout`, which wipes `.env`, the cached session, the keys, and the browser profile (they'd then have to log in and re-export keys next time).

## Setup: bootstrap first

```bash
bash scripts/bootstrap.sh              # installs Python if missing + venv + deps + Playwright/Chromium
bash scripts/bootstrap.sh --no-browser # same, minus Playwright (manual token paste only)
# Windows: powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1 [-NoBrowser]
```

**No Python on the machine?** The bootstrap handles it: it tries the OS package manager first (brew / apt / dnf / apk / pacman / winget; apt-style needs passwordless sudo), and otherwise installs [`uv`](https://astral.sh/uv) and a standalone CPython 3.12 into `~/.local` with no admin rights. Manual equivalent: `python3 -m pip install -r scripts/requirements.txt` into any Python ≥ 3.9 — but prefer the bootstrap, it also sidesteps PEP 668 "externally-managed-environment" pip errors.

**Why Python/curl_cffi and not curl or node:** `prod-api.fomo.family` is behind Cloudflare bot management that blocks on TLS/JA3 fingerprint. Plain curl, `requests`, and Node `fetch` get `HTTP 430 {"error":"unauthorized"}` **even with a perfectly valid token** — the block is at the edge, before auth. `curl_cffi` impersonates Chrome's TLS fingerprint, which passes. This is verified: identical token → 430 from curl/node, 200 from curl_cffi. `fomo.py` handles this automatically; never fall back to raw curl for fomo endpoints.

## Auth (required for EVERYTHING — no token → 431; wrong TLS fingerprint → 430)

Auth is a Privy **customer access token** (localStorage `privy:token`) sent as `Authorization: Bearer <token>`. It's a JWT that expires ~1 hour after issuance. The user pastes their tokens from a logged-in browser session once; the script then auto-refreshes via Privy.

Token model (verified against the `@privy-io/react-auth` 3.34.0 bundle):
- `privy:token` — the customer access token; **this is the bearer fomo's API validates**. Refresh returns a new one as the `token` field.
- `privy:refresh_token` — long-lived; exchanged for new access tokens. Lifetime is app-configured and does eventually expire → user must re-paste.
- `privy:pat` — Privy's own access token (`privy_access_token`); not used by fomo's API, stored for completeness.
- Refresh call: `POST https://auth.privy.io/api/v1/sessions` with body `{"refresh_token": "<token>"}` and headers `privy-app-id`, `privy-client-id`, `privy-client`, plus `Authorization: Bearer <current access token>`. Response is the AuthenticatedUser object `{user, token, privy_access_token, refresh_token, session_update_action}`; `session_update_action: "clear"` means the session is dead (re-paste needed).

**Setup (automated, preferred)** — run `python3 scripts/login.py`; a browser opens, the user logs in once, and it writes the Privy tokens into `.env` automatically (persistent profile → later `login.py --headless` refreshes them). Needs `playwright` (`pip install playwright && playwright install chromium`). Falls back to the manual paste below if Playwright isn't available. If the headed poll doesn't capture within ~20s after the user logs in, stop it and run `python3 scripts/login.py --headless` — it harvests from the now-logged-in persistent profile.

**On every login, the agent MUST relay to the user (login.py prints all of this):**
1. **The account handle and balance.**
2. **If the account is empty → the deposit addresses** (Solana for SOL/USDC, EVM for the rest). Tell the user to deposit before trading; funds convert to Solana USDC. Re-check with `python3 scripts/fomo.py balances`.

Keep using this account indefinitely; only when the user explicitly asks to log out run `python3 scripts/fomo.py logout` to wipe `.env` values, the cached session, and the browser profile.

**Setup (manual)** — ask the user to open fomo.family (logged in), run this in the DevTools console, and paste the result back:

```js
copy(JSON.stringify({version:2,accessToken:localStorage.getItem('privy:token'),refreshToken:localStorage.getItem('privy:refresh_token'),privyAccessToken:localStorage.getItem('privy:pat')}))
```

Then:

```bash
python3 scripts/fomo.py auth '<pasted json>'   # stores to ~/.config/fomo-sapiens/auth.json (chmod 600)
python3 scripts/fomo.py whoami                 # resolves userId + wallet addresses, caches them
```

- The paste snippet's values are JSON-quoted (`"\"eyJ...\""`); `fomo.py auth` unwraps them.
- **The skill works with any account** — it's not tied to one. Each account authenticates with its own pasted tokens; `whoami` resolves that account's identity/wallets dynamically. You can only use an account you can log into (to grab its tokens) and, for trading, whose keys you can export.

### Multiple accounts (profiles)

Set `FOMO_PROFILE=<name>` to keep accounts side by side — each gets its own `~/.config/fomo-sapiens/<name>.json` (chmod 600). Set trading keys per shell for the active account.

```bash
FOMO_PROFILE=alice python3 scripts/fomo.py auth '<alice tokens>'
FOMO_PROFILE=alice python3 scripts/fomo.py whoami
FOMO_PROFILE=alice FOMO_WALLET_KEY=<alice sol key> python3 scripts/swap.py execute ...
FOMO_PROFILE=bob   python3 scripts/fomo.py auth '<bob tokens>'   # separate account
```

No `FOMO_PROFILE` → the default `auth.json`. (`FOMO_AUTH_FILE=<path>` overrides both if you want an explicit location.)
- Tokens auto-refresh via Privy on expiry/401/403/430/431. If refresh fails (refresh tokens do expire), ask the user to re-run the console snippet and re-run `auth`.
- `whoami` output (`userId`, `solAddress`, `evmAddress`) is needed for portfolio endpoints.

## Making API calls

```bash
python3 scripts/fomo.py api GET /watchlist
python3 scripts/fomo.py api POST /proxy/trendingTokens '{"resolution":"1D"}'
python3 scripts/fomo.py api GET '/v2/users/<userId>/balances'
```

Responses wrap payloads as `{success, message, responseObject, statusCode}`. Token identifiers are `"<address>:<chainId>"`; chain ids: solana `1399811149`, ethereum `1`, base `8453`, bsc `56`, monad `143`, robinhood-chain `4663`. USDC (solana, the app's cash balance): `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (6 decimals).

**Resolving a token / getting decimals** (needed for amount math): there is no free-text symbol search in the captured API. To turn a token into an `address:chainId` + `decimals`, use `POST /proxy/cryptoTokens` (curated majors — BTC/ETH/SOL/etc., each with `token.decimals`), `POST /proxy/trendingTokens`, `GET /tokenAllowList/detailed`, or `POST /proxy/filterTokens` (pass an array of `"address:chainId"` ids → returns `token.decimals`, price, mcap, liquidity). For tokens you already hold, `GET /v2/users/{userId}/balances` gives raw `balance` + human `shiftedBalance` + `token.decimals`. `POST /proxy/tokenDetails` returns trading stats only — **no decimals**. Never hardcode decimals; always look them up.

Key endpoints (details + exact shapes in `references/endpoints.md`):

- **Discovery**: `POST /proxy/trendingTokens`, `POST /proxy/filterTokens`, `POST /proxy/tokenDetails`, `POST /proxy/tokenWarnings` (rug/risk flags), `POST /proxy/mostHeld`, `GET /tokenAllowList/detailed`
- **Thesis / social**: `GET /feed/token/thesis` and `/feed/token/sortedThesis` (`?tokenAddress=&networkId=&threshold=` — written theses by holders), `GET /feed/token` (buy/sell activity feed), `GET /hodlers/top`, `GET /hodlers/devs`, `POST /hodlers/friends`, `GET /trades?userId=&tokenAddress=`, `GET /trades/{id}` + `/comments`, `GET /v2/leaderboard[/24h|/7d|/30d]`
- **Portfolio**: `GET /v2/users/{userId}/balances`, `GET /v2/users/{userId}/swaps`, `GET /watchlist`, `GET /v2/userTokens/aggregatedSnapshotById?userId=&snapshotId=`
- **Charts**: `GET https://fomo-api.mobula.io/api/2/token/ohlcv-history` (separate host; see reference for params)

## Thesis analysis playbook

To analyze a token ("what's the thesis on X?"), combine:

1. `POST /proxy/tokenDetails` — price, mcap, liquidity, volume; `POST /proxy/tokenWarnings` — risk flags. Do this first; mention warnings prominently.
2. `GET /feed/token/sortedThesis` — the actual written theses. Requires a time window: `afterTime` + `beforeTime` (epoch ms) + `limit` (e.g. last 7 days), else HTTP 400. `GET /feed/token/thesis` works without a window. Note author conviction: each thesis links a `tradeId`; pull `GET /trades/{tradeId}` to see if the author is up/down and still holding (a thesis from someone who already exited is worth less).
3. `GET /hodlers/top` + `/hodlers/devs` — holder concentration, whether devs/insiders hold.
4. `GET /feed/token` — recent buy/sell flow (who is entering/exiting and at what size).
5. OHLCV history for price context.

Synthesize: bull/bear cases from theses weighted by author track record (leaderboard presence, trade PnL), holder quality, risk warnings, and flow direction.

## Trading (real money — be careful)

Flow (verified against the app's trade bundle + a live quote): `POST /swaps/v2` (`{inTokenId, outTokenId, amount, retry:0}`) returns `v1Swap` (same-chain solana) or `v2Swap` (cross-chain relay). The Solana tx already carries the fomo fee-payer signature at signer slot 0; the client signs the message with the user's wallet, fills the user's signer slot, and submits raw base64 as `text/plain` to Jito (`mainnet.hudson.jito.wtf/api/v1/sendTransactionWeb?mev_protection_default=true`). `swap.py execute` does exactly this (signing verified with `solders`). There's a $2.00 minimum swap value. (If a quote ever includes `jitoTipTx`, bundle submission is required — the script bails; use the app.)

```bash
python3 scripts/swap.py quote   EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149 <mint>:1399811149 3000000   # $3 USDC -> token
python3 scripts/swap.py execute EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149 <mint>:1399811149 3000000   # sign + submit
python3 scripts/swap.py status  <relaySwapId>                                                                        # cross-chain only
```

Rules:
- **Why a key is needed:** reads/quotes/thesis posting work with just the pasted token, but *executing* a trade requires signing a transaction. fomo signs inside the Privy iframe (key reconstructed from shares) and Privy's server signing API needs fomo's app secret (which we don't have) — so the only way to sign outside the browser is the raw key. Only `execute` needs it; `quote` never does.
- **Getting the keys:** run `python3 scripts/export_key.py` (captures **both** Solana and EVM keys — always both, never one). It drives the Privy export iframe itself in a **visible window** and stores each key **encrypted at rest** (Fernet), never in `.env` (masked; never printed). **Tell the user not to click anything in that window until it finishes or they're prompted** — a stray click can interrupt it. If automated capture fails 3 times (e.g. Privy throttles repeated exports) it prompts the user to click **Export key → Copy key** (the Solana address, then a Base address; they paste nothing). Keys don't expire — one-time per account. If a trade needs a key that isn't stored, run the export and then execute the trade without re-asking.
- Signing needs `FOMO_WALLET_KEY` (base58 solana secret key, exported by the user from fomo's wallet-export UI). It is stored encrypted at rest and decrypted just-in-time to sign; never echo or log it.
- **No confirmation step by default.** When the user asks to buy or sell, run `quote` and then `execute` in the same turn, and report `swapUsdValue`, `expectedOut`, `priceImpactPct`, and any warning **with the result**. Only pause for a go-ahead if the user explicitly asked to confirm first ("ask me before you execute", "quote only"), or if the quote carries a warning other than `NONE` / the token has `disableSelling`/`disableBuying` set / the amount is ambiguous (no amount given, or "sell some"). "Sell X" means sell the whole position; "sell N%" means that fraction of the raw balance.
- Amounts are raw base units (`3000000` = $3 USDC). Sanity-check magnitude before executing; never guess decimals — look them up (see token-resolution note above).
- Same-chain solana swaps confirm on-chain within seconds; verify via `GET /v2/users/{userId}/swaps` (newest first). Cross-chain (v2Swap) swaps: poll `swaps/v2/status?relaySwapId=` until `SUCCESS`.
- EVM-origin swaps (selling a token that lives on an EVM chain — Ethereum/Base/BSC/Monad/Robinhood) use `swap_evm.py` (ERC-4337 v0.8 userOp signed with the exported EVM key). See below.

## EVM sells (`swap_evm.py`)

Selling a token that lives on an EVM chain is EVM-origin (the token isn't on Solana), so it can't use `swap.py`. `swap_evm.py` builds and signs an ERC-4337 v0.8 userOperation. Buying an EVM token, or selling a Solana token, stays on `swap.py` (Solana-origin).

```bash
python3 scripts/swap_evm.py quote   <tokenAddress>:<chainId> <rawAmount>   # e.g. 0x…:1  9000000000000000
python3 scripts/swap_evm.py execute <tokenAddress>:<chainId> <rawAmount>   # build + sign + submit + poll
```

- Signing needs `FOMO_EVM_KEY` (the exported EVM private key, hex). For these EIP-7702 accounts the account address IS the signer, so this one key signs userOps and authorizes first-time delegate installs. Never log it; env only.
- Proceeds always convert to Solana USDC (the script hardcodes USDC:1399811149 as the output). Poll the bridge with `swap.py status <relaySwapId>`.
- **$5 minimum** on some chains (e.g. Ethereum), vs $2 on Solana; Robinhood accepted $2.39. Same no-confirmation rule as `swap.py`: quote → execute → report the numbers with the result.
- Gas is sponsored (fomo passes a grant via the `fomo-execution-context` header), so the user needs no native gas token.
- First sell on a chain the account hasn't used auto-attaches an EIP-7702 delegate install (`eip7702Auth`); subsequent sells skip it. Handled automatically.
- Verified: calldata/userOp-hash/7702-auth reproduce captured Robinhood+Base+Monad swaps byte-for-byte; **live key-signed sell executed 2026-09-03** (full BUWA position on Robinhood chain → 2.29 USDC on Solana, relay SUCCESS in ~1 min; ~3% bridge/relay cost on a $2.39 swap). Robinhood chain accepted a $2.39 sell with no minimum warning.

## Posting a thesis (ask after a buy)

**After a buy, ask the user whether they want you to write and post a thesis (do not post one automatically).** Only proceed if they say yes. A "thesis" is the top-level comment on your *own* trade — it's how fomo surfaces your rationale on the token's feed.

Endpoint: `POST /trades/comment` with `{"tradeId": "<your trade id>", "comment": "<thesis text>", "visibility": "public"}`. Same endpoint serves theses and comments; when the tradeId is your own trade it renders as a thesis.

Workflow:
1. **Buy** the token (`swap.py execute`).
2. **Resolve your trade id**: `python3 scripts/fomo.py resolve-trade <tokenAddress> <networkId>` (finds your active/most-recent trade for that token; also reports `hasThesis` so you don't double-post).
3. **Gather context first** — read the existing theses so yours is informed and fits the room, exactly as the research playbook does: `GET /feed/token/sortedThesis` (what other holders argue), `tokenDetails`, `tokenWarnings`, `hodlers/top`. Write a thesis grounded in that data (the actual bull case, catalysts, holder quality), not a generic "number go up."
4. **Post**: `python3 scripts/fomo.py post-thesis <tokenAddress> <networkId> "<thesis text>" [public|private]` (resolves the trade id and posts in one step), or the raw `api POST /trades/comment` call.

Rules:
- Post without waiting for approval (same no-confirmation default as trading), but always show the exact text you posted in the reply — it's public and tied to their handle. If the user asked to review theses before posting, show the draft and wait instead.
- **Verified working**: a Charles capture shows this exact request returning `200 {"success":true,"message":"Trade comment created successfully"}`. The endpoint intermittently returns `500 "Failed to create trade comment"` (seen in an earlier capture with an identical body) — it's transient, so `post-thesis` retries once on a 500. If it still fails, report that it didn't post rather than claiming success.
- Keep theses within `config.transferMessageMaxLength` context if unsure of the limit; fomo truncates long text into `shortCommentSegments`.

## Agent ledger (trade tracking — best-effort, opt-out)

Trades executed through this skill are reported to a companion API, the **agent ledger** (`LEDGER_URL`, default `https://fomo-skill-api.fly.dev`), which logs per-agent trades, computes realized PnL, and ranks agents. Full notes in `README.md` → "Agent ledger".

- **Registration is automatic**: `login.py` and `fomo.py auth` call `fomo.ledger_register()` after a successful login — `POST /agents/register` with the Privy access token as bearer (the API verifies it against Privy's JWKS; identity = the JWT subject). The agent's **name is the fomo profile handle**, kept in sync on every login. The returned key lands in `.env` as `LEDGER_AGENT_KEY`. Never call the admin `POST /agents` — the skill has no admin key and doesn't need one.
- **Reporting is automatic**: `swap.py execute` and `swap_evm.py execute` call `fomo.ledger_report()` after a successful swap (buy = USDC→token with `expectedOutHumanAmount`; sell = token→USDC with the human amount via decimals). If no agent key is stored yet it registers on the fly; on a 401 it re-registers once.
- **Non-breaking by design — never let the ledger block anything.** Every ledger call is wrapped, times out, and prints `[ledger] … (non-fatal)` on failure; a login or trade always completes regardless. Don't retry ledger failures, don't queue them, don't mention them beyond relaying the one-line note. A trade that didn't save is fine.
- **Opt-out at any time**: `python3 scripts/fomo.py ledger off` → `DELETE /me` (removes the agent and all its trades), clears the key, and writes `LEDGER_OPT_OUT=1` to `.env` (persists across `logout`). `ledger on` re-registers. `ledger status` shows enabled/agent/stats. Honor "stop tracking" / "opt out" / "don't report my trades" immediately, no confirmation.
- Read endpoints (public): `GET /leaderboard?sort=realized_pnl_usd|volume_usd|roi_pct|trade_count|win_rate`, `GET /agents/<handle>`, `GET /agents/<handle>/trades`. Use plain `curl` for these (not `fomo.py api`, which targets fomo's API).

## Deposits

There is no deposit API to call. Depositing = sending funds to the user's embedded wallets (from `whoami`): USDC/SOL to `solAddress`, or EVM assets to `evmAddress`. Fiat on-ramp is Crossmint inside the app (limits in `GET /config`: min $5, max $2500/day). To help with a deposit: show the addresses, then watch `GET /v2/users/{userId}/balances` for arrival.

## Examples (concrete commands)

```bash
# ── first-time setup ──
python3 scripts/login.py                       # log in; relay balance + deposit addr
python3 scripts/export_key.py                  # (to trade) capture BOTH keys in one session — always both
python3 scripts/fomo.py show-account           # balance + both keys
python3 scripts/fomo.py ledger status          # agent-ledger: registered name + PnL stats (auto-registered on login)
python3 scripts/fomo.py ledger off             # opt out of trade tracking (deletes server-side data)

# ── check state ──
python3 scripts/fomo.py balances               # portfolio value + holdings
python3 scripts/fomo.py api POST /proxy/trendingTokens '{}'          # trending
python3 scripts/fomo.py api GET  /v2/leaderboard/24h                 # leaderboard

# ── research the top 3 trending tokens: why are they going up? (verified 2026-09-03) ──
python3 scripts/fomo.py api POST /proxy/trendingTokens '{}'          # list of 50; take [:3]; each has token.address, token.networkId, priceUSD, marketCap, change24, volume24, holders
# then, per token (<addr>,<net> from the list above; NOW/WK = epoch ms now / 7 days ago):
python3 scripts/fomo.py api POST /proxy/tokenWarnings '{"address":"<addr>","networkId":<net>}'   # {"warnings":[], "disableBuying", "disableSelling"}
python3 scripts/fomo.py api GET '/hodlers/top?tokens=%5B%7B%22address%22%3A%22<addr>%22%2C%22networkId%22%3A<net>%7D%5D'   # NOTE: `tokens` = URL-encoded JSON array [{address,networkId}]; tokenAddress/networkId params → 400
python3 scripts/fomo.py api GET '/hodlers/devs?tokenAddress=<addr>&networkId=<net>'             # devHoldings[] — who the devs are and whether they still hold
python3 scripts/fomo.py api GET '/feed/token/sortedThesis?tokenAddress=<addr>&networkId=<net>&afterTime=<WK>&beforeTime=<NOW>&limit=20&threshold=0'
# sortedThesis → responseObject.items[]: comment.comment (text), comment.numLikes, userHandle, isDev,
#   authorTrade.{usdValue, percentageUnrealizedPnl, closedAt}  ← weight theses by position size + PnL; closedAt != null means the author already exited
# hodlers/top → responseObject[0].topHolders[]: user.{userHandle,followers}, value, pnl, averageEntryPrice, comment.comment (the holder's thesis)
# Synthesize per token: the concrete driver (revenue/buybacks, narrative/branding, cult mission…), holder quality/concentration, warnings, and who's exiting.

# ── research a token (Base example) ──
python3 scripts/fomo.py api POST /proxy/filterTokens  '["<addr>:8453"]'    # resolve + market data
python3 scripts/fomo.py api POST /proxy/tokenWarnings '{"address":"<addr>","networkId":8453}'
python3 scripts/fomo.py api GET '/feed/token/sortedThesis?tokenAddress=<addr>&networkId=8453&afterTime=<ms>&beforeTime=<ms>&limit=40&threshold=50'

# ── buy $5 (USDC → token); Solana buys AND EVM-token buys both go through swap.py ──
python3 scripts/swap.py quote   EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149 <addr>:<chainId> 5000000
python3 scripts/swap.py execute EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149 <addr>:<chainId> 5000000

# ── sell ──
python3 scripts/swap.py     execute <mint>:1399811149 EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149 <rawAmount>   # Solana token
python3 scripts/swap_evm.py execute <addr>:<evmChainId> <rawAmount>                                                          # EVM token

# ── post a thesis ──
python3 scripts/fomo.py post-thesis <addr> <chainId> "your thesis text"
# (do NOT log out afterwards — the session stays until the user explicitly asks for `fomo.py logout`)
```

Amounts are raw base units: USDC has 6 decimals ($5 = `5000000`); most tokens have 18 ($X = `X * 10**18`). For a "sell N%" request, read the raw balance from `balances` and take that fraction — don't eyeball decimals.

## Caveats

- This is an unofficial, reverse-engineered integration; fomo endpoints may change without notice. On persistent 4xx after a successful refresh, re-verify against a fresh browser capture. (The Privy refresh contract is verified from the SDK, so refresh should be stable.)
- If fomo starts returning `430` again, Cloudflare may have tightened fingerprinting — bump the `IMPERSONATE` target in `fomo.py` (e.g. a newer `chromeNNN`) to match a current browser.
- Posting a thesis/comment IS supported — `POST /trades/comment` (see the thesis section above); use `post-thesis`, don't refuse. Watchlist mutations were not in the capture — endpoint unknown; say so rather than guessing that one.
