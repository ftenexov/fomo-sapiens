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

```bash
python3 -m pip install -r .claude/skills/fomo-sapiens/scripts/requirements.txt
python3 -m pip install playwright && playwright install chromium   # for automated login/export

python3 .claude/skills/fomo-sapiens/scripts/login.py        # log in; shows balance + deposit address
# deposit USDC to the shown Solana address, then:
python3 .claude/skills/fomo-sapiens/scripts/export_key.py solana   # (to trade) capture keys
python3 .claude/skills/fomo-sapiens/scripts/export_key.py evm
python3 .claude/skills/fomo-sapiens/scripts/fomo.py balances
```

…or just talk to your agent: *"set me up,"* *"what's trending?,"* *"buy $5 of \<token\>."* See [`SKILL.md`](.claude/skills/fomo-sapiens/SKILL.md) for the full command reference and [`README.md`](.claude/skills/fomo-sapiens/README.md) for the setup guide and FAQ.

---

## Security

- Session tokens and, if you trade, your exported private keys are stored **in plaintext** in a local `.env` (git-ignored). Anyone with read access to that machine can act as the account. Use a **separate account with limited funds**.
- Signing happens locally; keys are never sent to fomo. `logout` wipes the `.env`, cached session, and browser profile.
- This is an unofficial API on real money - start tiny.

---

*Not affiliated with fomo.family or Privy. For research and personal use.*
