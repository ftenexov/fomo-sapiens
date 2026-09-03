#!/usr/bin/env python3
"""Automated token capture — no DevTools copy-paste.

Opens fomo.family in a real browser, waits for you to log in (Google OAuth, done by
a human once), then reads the Privy tokens from localStorage and stores them for the
skill. Uses a PERSISTENT browser profile, so after the first login later runs can
refresh tokens headlessly.

    python3 login.py             # headed: a window opens — log in when prompted
    python3 login.py --headless  # reuse the saved session (must have logged in once)
    python3 login.py --verbose   # print what each poll sees per tab (debugging capture)
    FOMO_PROFILE=alice python3 login.py   # per-account (separate browser profile)

Requires (optional dep — only for this script):
    pip install playwright && playwright install chromium
"""
import os
import sys
import time

import _deps  # noqa: F401
import fomo  # reuse profile-aware AUTH_FILE, save_auth, _unquote, whoami

FOMO_URL = "https://fomo.family"
# Persistent browser profile lives next to the account's token cache, keyed by profile.
_stem = os.path.splitext(os.path.basename(fomo.AUTH_FILE))[0]  # 'auth' or profile name
PROFILE_DIR = os.path.join(os.path.dirname(fomo.AUTH_FILE), "browser", _stem)


_HARVEST_JS = (
    "() => ({"
    "  token: localStorage.getItem('privy:token'),"
    "  refresh: localStorage.getItem('privy:refresh_token'),"
    "  pat: localStorage.getItem('privy:pat')"
    "})"
)


def _harvest(ctx, helper=None, verbose=False):
    """Read tokens from the helper tab first (a background fomo.family tab we never
    navigate, so its URL can't go stale during the OAuth hop — localStorage is shared
    across same-origin tabs), then any other fomo.family tab as a fallback.
    Every per-page call is bounded (2s) — a hung tab must never stall the poll loop."""
    pages = ([helper] if helper else []) + [pg for pg in ctx.pages if pg is not helper]
    for pg in pages:
        url = ""
        try:
            url = pg.url or ""
            if "fomo.family" not in url:
                if verbose:
                    print(f"   [skip] {url[:60]}")
                continue  # tokens live only on the fomo.family origin, not google's
            # wait_for_function is client-timed: it returns/raises within `timeout`
            # even if the renderer is unresponsive (plain evaluate() has no timeout).
            handle = pg.wait_for_function(_HARVEST_JS, timeout=2000, polling=250)
            t = handle.json_value()
            if verbose:
                live = t.get("token") and t["token"] not in ("null", '"deprecated"')
                print(f"   [page] {url[:60]} token={'yes' if live else 'no'}")
            if t and t.get("token"):
                return t
        except Exception as e:
            if verbose:
                print(f"   [err ] {url[:60]} {type(e).__name__}")
            continue  # mid-navigation context destroyed / timed out — try again next poll
    return {}


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fomo.die("Playwright not installed. Run the bootstrap once (installs it + Chromium):\n"
                 "  bash scripts/bootstrap.sh   (Windows: powershell -ExecutionPolicy Bypass -File scripts\\bootstrap.ps1)\n"
                 "or: python3 -m pip install playwright && playwright install chromium")

    headless = "--headless" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    os.makedirs(PROFILE_DIR, exist_ok=True)
    # Hide automation so Google's OAuth doesn't refuse with "this browser may not be secure".
    launch = dict(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
        ignore_default_args=["--enable-automation"],
    )
    tokens = None
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(PROFILE_DIR, channel="chrome", **launch)
        except Exception:
            ctx = p.chromium.launch_persistent_context(PROFILE_DIR, **launch)  # fallback: bundled chromium
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(FOMO_URL, wait_until="domcontentloaded")
        helper = None
        if not headless:
            # Background helper tab on the fomo origin: the login tab hops to Google and
            # back (Playwright's page.url can lag behind), so we poll this one instead.
            helper = ctx.new_page()
            helper.goto(FOMO_URL, wait_until="domcontentloaded")
            page.bring_to_front()
            print("Log in to fomo.family in the browser window… capturing automatically the moment you're in.")
        deadline = time.time() + (30 if headless else 300)
        ticks = 0
        while time.time() < deadline:
            tokens = _harvest(ctx, helper, verbose=verbose and ticks % 5 == 0)
            if tokens.get("token") and tokens["token"] not in ("null", '"deprecated"'):
                break
            ticks += 1
            if not headless and ticks % 5 == 0:
                print(f"…waiting for login ({len(ctx.pages)} tab(s) open; captures within ~1s of finishing)", flush=True)
            time.sleep(1)   # poll every 1s so capture is near-instant after login
        ctx.close()

    if not (tokens and tokens.get("token") and tokens.get("refresh")):
        fomo.die("No tokens captured. "
                 + ("Run without --headless and log in first." if headless
                    else "Login didn't complete — try again."))

    unq = fomo._unquote
    access, refresh = unq(tokens["token"]), unq(tokens["refresh"])
    pat = unq(tokens["pat"]) if tokens.get("pat") else None
    # Fill .env (the source of truth the user manages) and seed the live cache.
    fomo.write_env_tokens(access, refresh, pat)
    fomo.save_auth({"accessToken": access, "refreshToken": refresh, "privyAccessToken": pat})
    print(fomo.DISCLAIMER)
    try:
        s = fomo.account_summary()
    except Exception as e:
        print(f"Tokens captured & written to {fomo.ENV_FILE}, but couldn't load balances "
              f"({str(e)[:50]}); try `python3 fomo.py balances`.")
        return
    print(f"Logged in as {s['handle']} — tokens written to {fomo.ENV_FILE}")
    fomo.ledger_register()   # best-effort: agent named after the fomo handle; opt out with `fomo.py ledger off`
    if s["empty"]:
        print("\n💸 This account is EMPTY — deposit before trading. Send funds to:")
        print(f"   Solana (SOL / USDC):  {s['solAddress']}")
        print(f"   EVM (Base/ETH/…):     {s['evmAddress']}")
        print("   fomo converts deposits to Solana USDC, which all buys spend.")
    else:
        top = ", ".join(f"{h['amount']:g} {h['symbol']} (${h['usd']})" for h in s["holdings"][:5])
        print(f"Balance: ${s['usdTotal']} — {top}")
    print("\nRun `python3 fomo.py logout` when done to wipe all account state.")


if __name__ == "__main__":
    main()
