---
name: fomo
description: Interact with fomo.family (social crypto trading app) — market/token research, thesis analysis, portfolio, watchlist, deposits, and live trading (solana swaps). Use when the user mentions fomo, fomo.family, trading memecoins, thesis feeds, or their fomo portfolio.
---

# fomo.family integration

Reverse-engineered client for the fomo.family private API (captured & verified live 2026-09-01). Python scripts live in `scripts/`; full endpoint catalog with request/response shapes in `references/endpoints.md` — **read it before calling unfamiliar endpoints**.

## Onboarding — guide the user through these steps, in order

Walk a new user through setup one step at a time; relay each result in chat before moving on.

1. **Install deps** (once): `python3 -m pip install -r scripts/requirements.txt` and, for automated login/key export, `python3 -m pip install playwright && playwright install chromium`.
2. **Log in**: `python3 scripts/login.py` → a browser opens; tell the user to log in with Google. If it doesn't capture within ~20s after they log in, stop it and run `python3 scripts/login.py --headless`.
3. **Relay in chat** (login.py prints all of it): the **disclaimer** (don't use your main account — plaintext secrets), the **account handle**, and the **balance**. **If the account is empty, show the deposit addresses** (Solana + EVM) and tell them to deposit ≥ their intended trade size (funds convert to Solana USDC).
4. **For trading, capture keys — do the two chains as SEPARATE steps:**
   - 4a. `python3 scripts/export_key.py solana` → browser opens to the export screen; tell the user to click **Export key → Copy key** on the **Solana address**. It captures and closes. Confirm it succeeded.
   - 4b. Then `python3 scripts/export_key.py evm` → browser opens the export screen again; tell the user to click **Export key → Copy key** on a **Base (EVM) address** (Base/Monad/BNB/Robinhood share one key). It captures and closes.
   - Always say **"Copy key"** — the plain **"Copy"** button only copies the public address.
5. **Show the account in chat**: run `python3 scripts/fomo.py show-account` and display to the user the **balance** and **both signing keys** (solanaKey, evmKey). ⚠️ These are private keys — surfacing them in chat is at the user's request; note the sensitivity once.
6. **Trade / research** as requested (see below). When the user is done, `python3 scripts/fomo.py logout` wipes `.env`, the cached session, and the browser profile.

## Setup: install deps first

```bash
python3 -m pip install -r scripts/requirements.txt   # curl_cffi + solders
```

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
1. **The disclaimer** — do NOT use your main fomo.family account; tokens and (if trading) the private key are stored in plaintext. Use a separate account with limited funds.
2. **The account handle and balance.**
3. **If the account is empty → the deposit addresses** (Solana for SOL/USDC, EVM for the rest). Tell the user to deposit before trading; funds convert to Solana USDC. Re-check with `python3 scripts/fomo.py balances`.

Keep using this account until the user asks to log out; then run `python3 scripts/fomo.py logout` to wipe `.env` values, the cached session, and the browser profile.

**Setup (manual)** — ask the user to open fomo.family (logged in), run this in the DevTools console, and paste the result back:

```js
copy(JSON.stringify({version:2,accessToken:localStorage.getItem('privy:token'),refreshToken:localStorage.getItem('privy:refresh_token'),privyAccessToken:localStorage.getItem('privy:pat')}))
```

Then:

```bash
python3 scripts/fomo.py auth '<pasted json>'   # stores to ~/.config/fomo-skill/auth.json (chmod 600)
python3 scripts/fomo.py whoami                 # resolves userId + wallet addresses, caches them
```

- The paste snippet's values are JSON-quoted (`"\"eyJ...\""`); `fomo.py auth` unwraps them.
- **The skill works with any account** — it's not tied to one. Each account authenticates with its own pasted tokens; `whoami` resolves that account's identity/wallets dynamically. You can only use an account you can log into (to grab its tokens) and, for trading, whose keys you can export.

### Multiple accounts (profiles)

Set `FOMO_PROFILE=<name>` to keep accounts side by side — each gets its own `~/.config/fomo-skill/<name>.json` (chmod 600). Set trading keys per shell for the active account.

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
- **Getting the key:** run `python3 scripts/export_key.py solana` then `python3 scripts/export_key.py evm` (one chain per run) — each opens the export screen; the user clicks **Export key → Copy key** for that address and it captures the key into `.env` (masked; never printed). Privy blocks fully-automated reveal, so that click is the user's. Keys don't expire — one-time per account.
- Signing needs `FOMO_WALLET_KEY` (base58 solana secret key, exported by the user from fomo's wallet-export UI). Never echo, log, or store this key; read it from env only.
- **Always run `quote` and show the user `swapUsdValue`, `expectedOut`, `priceImpactPct`, and any warning, and get explicit confirmation before `execute`** — unless they already gave a standing instruction with exact amounts.
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
- **$5 minimum** on some chains (e.g. Ethereum), vs $2 on Solana. Confirm `swapUsdValue`/`expectedOut`/`priceImpactPct` with the user before `execute`, same as `swap.py`.
- Gas is sponsored (fomo passes a grant via the `fomo-execution-context` header), so the user needs no native gas token.
- First sell on a chain the account hasn't used auto-attaches an EIP-7702 delegate install (`eip7702Auth`); subsequent sells skip it. Handled automatically.
- Verified: quote+parse live on Ethereum; calldata/userOp-hash/7702-auth reproduce captured Robinhood+Base+Monad swaps byte-for-byte. A live key-signed EVM sell has not yet been run.

## Posting a thesis (do this after every buy)

**When the user buys a token through this skill, post a thesis for it afterward by default** (unless they say not to). A "thesis" is the top-level comment on your *own* trade — it's how fomo surfaces your rationale on the token's feed.

Endpoint: `POST /trades/comment` with `{"tradeId": "<your trade id>", "comment": "<thesis text>", "visibility": "public"}`. Same endpoint serves theses and comments; when the tradeId is your own trade it renders as a thesis.

Workflow:
1. **Buy** the token (`swap.py execute`).
2. **Resolve your trade id**: `python3 scripts/fomo.py resolve-trade <tokenAddress> <networkId>` (finds your active/most-recent trade for that token; also reports `hasThesis` so you don't double-post).
3. **Gather context first** — read the existing theses so yours is informed and fits the room, exactly as the research playbook does: `GET /feed/token/sortedThesis` (what other holders argue), `tokenDetails`, `tokenWarnings`, `hodlers/top`. Write a thesis grounded in that data (the actual bull case, catalysts, holder quality), not a generic "number go up."
4. **Post**: `python3 scripts/fomo.py post-thesis <tokenAddress> <networkId> "<thesis text>" [public|private]` (resolves the trade id and posts in one step), or the raw `api POST /trades/comment` call.

Rules:
- Show the user the drafted thesis text and get confirmation before posting — it's public and tied to their handle.
- **Verified working**: a Charles capture shows this exact request returning `200 {"success":true,"message":"Trade comment created successfully"}`. The endpoint intermittently returns `500 "Failed to create trade comment"` (seen in an earlier capture with an identical body) — it's transient, so `post-thesis` retries once on a 500. If it still fails, report that it didn't post rather than claiming success.
- Keep theses within `config.transferMessageMaxLength` context if unsure of the limit; fomo truncates long text into `shortCommentSegments`.

## Deposits

There is no deposit API to call. Depositing = sending funds to the user's embedded wallets (from `whoami`): USDC/SOL to `solAddress`, or EVM assets to `evmAddress`. Fiat on-ramp is Crossmint inside the app (limits in `GET /config`: min $5, max $2500/day). To help with a deposit: show the addresses, then watch `GET /v2/users/{userId}/balances` for arrival.

## Caveats

- This is an unofficial, reverse-engineered integration; fomo endpoints may change without notice. On persistent 4xx after a successful refresh, re-verify against a fresh browser capture. (The Privy refresh contract is verified from the SDK, so refresh should be stable.)
- If fomo starts returning `430` again, Cloudflare may have tightened fingerprinting — bump the `IMPERSONATE` target in `fomo.py` (e.g. a newer `chromeNNN`) to match a current browser.
- Posting a thesis/comment IS supported — `POST /trades/comment` (see the thesis section above); use `post-thesis`, don't refuse. Watchlist mutations were not in the capture — endpoint unknown; say so rather than guessing that one.
