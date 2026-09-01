#!/usr/bin/env python3
"""Automated token capture — no DevTools copy-paste.

Opens fomo.family in a real browser, waits for you to log in (Google OAuth, done by
a human once), then reads the Privy tokens from localStorage and stores them for the
skill. Uses a PERSISTENT browser profile, so after the first login later runs can
refresh tokens headlessly.

    python3 login.py             # headed: a window opens — log in when prompted
    python3 login.py --headless  # reuse the saved session (must have logged in once)
    FOMO_PROFILE=alice python3 login.py   # per-account (separate browser profile)

Requires (optional dep — only for this script):
    pip install playwright && playwright install chromium
"""
import os
import sys
import time

import fomo  # reuse profile-aware AUTH_FILE, save_auth, _unquote, whoami

FOMO_URL = "https://fomo.family"
# Persistent browser profile lives next to the account's token cache, keyed by profile.
_stem = os.path.splitext(os.path.basename(fomo.AUTH_FILE))[0]  # 'auth' or profile name
PROFILE_DIR = os.path.join(os.path.dirname(fomo.AUTH_FILE), "browser", _stem)


def _harvest(ctx):
    """Read tokens from any open fomo.family page. Resilient to OAuth navigations
    (the page hops to accounts.google.com and back, which destroys eval contexts)."""
    for pg in ctx.pages:
        try:
            if "fomo.family" not in (pg.url or ""):
                continue  # tokens live only on the fomo.family origin, not google's
            t = pg.evaluate(
                "() => ({"
                "  token: localStorage.getItem('privy:token'),"
                "  refresh: localStorage.getItem('privy:refresh_token'),"
                "  pat: localStorage.getItem('privy:pat')"
                "})"
            )
            if t and t.get("token"):
                return t
        except Exception:
            continue  # mid-navigation context destroyed — try again next poll
    return {}


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fomo.die("Playwright not installed. Run:\n"
                 "  python3 -m pip install playwright && playwright install chromium")

    headless = "--headless" in sys.argv
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
        if not headless:
            print("Log in to fomo.family in the browser window… capturing automatically the moment you're in.")
        deadline = time.time() + (30 if headless else 300)
        ticks = 0
        while time.time() < deadline:
            tokens = _harvest(ctx)
            if tokens.get("token") and tokens["token"] not in ("null", '"deprecated"'):
                break
            ticks += 1
            if not headless and ticks % 5 == 0:
                print("…waiting for login (captures within ~1s of finishing)")
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
