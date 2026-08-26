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


def _harvest(page):
    return page.evaluate(
        "() => ({"
        "  token: localStorage.getItem('privy:token'),"
        "  refresh: localStorage.getItem('privy:refresh_token'),"
        "  pat: localStorage.getItem('privy:pat')"
        "})"
    )


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fomo.die("Playwright not installed. Run:\n"
                 "  python3 -m pip install playwright && playwright install chromium")

    headless = "--headless" in sys.argv
    os.makedirs(PROFILE_DIR, exist_ok=True)
    tokens = None
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(PROFILE_DIR, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(FOMO_URL, wait_until="domcontentloaded")
        if not headless:
            print("Log in to fomo.family in the browser window… (waiting up to 4 min)")
        deadline = time.time() + (30 if headless else 240)
        while time.time() < deadline:
            tokens = _harvest(page)
            if tokens.get("token") and tokens["token"] not in ("null", '"deprecated"'):
                break
            time.sleep(2)
        ctx.close()

    if not (tokens and tokens.get("token") and tokens.get("refresh")):
        fomo.die("No tokens captured. "
                 + ("Run without --headless and log in first." if headless
                    else "Login didn't complete — try again."))

    unq = fomo._unquote
    fomo.save_auth({
        "accessToken": unq(tokens["token"]),
        "refreshToken": unq(tokens["refresh"]),
        "privyAccessToken": unq(tokens["pat"]) if tokens.get("pat") else None,
    })
    profile = fomo.whoami(fomo.load_auth())
    print(f"Logged in as {profile['handle']} — tokens saved to {fomo.AUTH_FILE}")


if __name__ == "__main__":
    main()
