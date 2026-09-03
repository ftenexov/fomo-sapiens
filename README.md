# 🧠 Fomo Sapiens

**An AI agent skill that researches, trades, and writes theses on [fomo.family](https://fomo.family) - driven entirely by natural language.**

Fomo Sapiens turns a coding/agent assistant into a hands-on trader for fomo.family (a social crypto trading app). You talk to it in plain English - *"research the top trending tokens,"* *"buy $5 of X,"* *"sell half my BUWA,"* *"post a thesis"* - and it does the work: pulling market data, reading the community's theses, executing swaps on Solana and EVM chains, and posting its own analysis.

> ⚠️ **Unofficial and use-at-your-own-risk.** It is not affiliated with or endorsed by fomo, can break at any time, and moves real money. Use a burner account with limited funds - never your main one.

---

## What it can do

| Capability | Needs | Status |
|---|---|---|
| Research a token - price, market cap, liquidity, risk/scam flags, holder distribution, OHLCV | login | ✅ verified live |
| Thesis analysis - read the community's theses and synthesize a view weighted by each author's real PnL | login | ✅ verified live |
| Portfolio, balances, deposit addresses | login | ✅ verified live |
| Swap quotes | login | ✅ verified live |
| **Buy** any token (Solana or EVM chain), spending Solana USDC | login + Solana key | ✅ verified live |
| **Sell** a Solana token | login + Solana key | ✅ verified live |
| **Sell** an EVM token (Base, Robinhood, BSC, Monad, Ethereum) via ERC-4337 | login + EVM key | ✅ verified live |
| **Post a thesis** after buying, grounded in the gathered data | login | ✅ verified live |
| Leaderboards, trending, holders, dev holdings | login | ✅ verified live |

Every trading path above has been executed end-to-end with real funds.

---

## How it works

A few problems had to be solved to talk to fomo.family outside the browser:

- **Cloudflare TLS fingerprinting.** fomo's API blocks non-browser clients (plain `curl`/`requests`/`node` get `HTTP 430` even with a valid token). Fomo Sapiens uses [`curl_cffi`](https://github.com/lexiforest/curl_cffi) to impersonate a real Chrome TLS fingerprint, which passes.
- **Privy auth.** Login is a Privy session token (captured from a real browser via Playwright) with automatic refresh. Keys never touch fomo's servers - they stay in a local `.env`.
- **Solana swaps.** `/swaps/v2` returns a fee-payer-co-signed transaction; the skill signs the user slot with the exported key ([`solders`](https://github.com/kevinheavey/solders)) and submits to Jito.
- **EVM swaps.** Buying an EVM token is a Solana-origin cross-chain swap. Selling one is a full **ERC-4337 v0.8 userOperation** signed with the EVM key, with an **EIP-7702** delegate auto-installed on first use of a chain, submitted to fomo's bundler.

Onboarding is a single browser login: Fomo Sapiens captures your session, shows your balance and deposit address, and (for trading) walks you through a one-click key export - then gets out of the way.

---

## Repo layout

```
.claude/skills/fomo-sapiens/
├── SKILL.md               # agent playbook: onboarding, endpoints, trading + thesis rules
├── README.md              # detailed setup guide + FAQ
├── references/
│   └── endpoints.md       # full API catalog with request/response shapes
└── scripts/
    ├── fomo.py            # API client: Privy auth, refresh, TLS bypass, balances, thesis posting
    ├── login.py           # automated browser login → tokens into .env
    ├── export_key.py      # semi-automated signing-key export (one chain per run)
    ├── swap.py            # Solana swap quote / execute (Jito)
    ├── swap_evm.py        # EVM-token sells (ERC-4337 v0.8 + EIP-7702)
    └── requirements.txt
```

It installs as a [Claude Code](https://claude.com/claude-code) skill - drop the folder under `.claude/skills/` and the agent loads it automatically when you mention fomo.

---

## Quick start

Fomo Sapiens runs *inside* your AI agent (e.g. [Claude Code](https://claude.com/claude-code)) — you don't run anything by hand, you just talk to it.

**What you need**
- A **fomo.family account** — you sign in with a **Google account**. Use a fresh/burner Google account, not your main one.
- A little **USDC** to trade with (optional — research, theses, and quotes work with no funds).

**Getting started — just tell your agent:**
- *"Set me up on fomo"* → it opens a browser, you log in with Google once, and it captures your session, then shows your **balance** and **deposit address**.
- Send some **USDC** to that address (deposits convert to Solana USDC, which trades spend).
- Then go: *"what's trending?"*, *"research \<token\>"*, *"buy $5 of \<token\>"* — see the examples below.

**Exporting your keys (only needed to place trades)**
Trading needs your wallet's signing keys, and for security they live in fomo's own vault — so there's one manual click. Your agent handles the rest: it opens fomo's **Export keys** screen and asks you to click **Export key → Copy key** for each chain (Solana, then an EVM one). It captures the key automatically. **The chat guides you through every step** — you never paste a key by hand.

For the full command reference see [`SKILL.md`](.claude/skills/fomo-sapiens/SKILL.md); for the detailed setup guide and FAQ see the skill [`README.md`](.claude/skills/fomo-sapiens/README.md).

---

## Usage examples

Once you're set up, just talk to your agent in plain language:

- *"Set me up on fomo"* — logs in, shows your balance and deposit address.
- *"What's my portfolio worth right now?"* — total value + every holding.
- *"Where do I deposit?"* — your Solana and EVM deposit addresses.
- *"What's trending on fomo?"* — the current trending tokens.
- *"Research BUWA — is it safe?"* — market cap, liquidity, holder distribution, and scam/risk flags.
- *"What's the community thesis on \<token\>?"* — pulls holders' theses and summarizes the bull/bear case, weighted by each author's real PnL.
- *"Research the top 5 trending tokens and tell me why they're pumping."*
- *"Buy $5 of \<token\>."* — resolves the chain, checks warnings, quotes, and executes.
- *"Buy $10 of \<token\> on Base."* — same, for an EVM-chain token.
- *"Sell half my \<token\>."* / *"Sell all my \<token\>."*
- *"Buy $5 of \<token\>, then research it and post a thesis based on the fundamentals."*
- *"Who's winning?"* — the 24h / 7d / 30d leaderboard.
- *"How much did that last trade cost me?"* — reads the fee/slippage from your balance delta.
- *"Log me out and wipe everything."* — clears tokens, keys, session, and browser profile.

Everything is a normal request — the agent picks the right action, shows you quotes and risk warnings before spending, and reports back.

---

## Security

- Session tokens and, if you trade, your exported private keys are stored **in plaintext** in a local `.env` (git-ignored). Anyone with read access to that machine can act as the account. Use a **separate account with limited funds**.
- Signing happens locally; keys are never sent to fomo. `logout` wipes the `.env`, cached session, and browser profile.
- This is an unofficial API on real money - start tiny.

---

*Not affiliated with fomo.family or Privy. For research and personal use.*
