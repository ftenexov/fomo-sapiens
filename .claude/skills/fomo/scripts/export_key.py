#!/usr/bin/env python3
"""Semi-automated signing-key export.

Private keys are NOT in the page (Privy holds them in a secure enclave) and Privy blocks
fully-automated key reveal, so the final click is yours. This script does everything else:
it drives the browser to fomo's key-export screen and then watches the clipboard — you click
"Export key" for a chain and hit Copy, and it captures the key and stores it via set-key
(masked; the secret is never printed).

    python3 export_key.py          # captures whatever chains you export, until you're done

Needs the persistent login profile (run login.py first) and playwright.
"""
import os
import re
import time

import fomo

PROFILE = os.path.join(os.path.dirname(fomo.AUTH_FILE), "browser",
                       os.path.splitext(os.path.basename(fomo.AUTH_FILE))[0])


def classify(k):
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{80,90}", k):
        return "solana"
    if re.fullmatch(r"0x[0-9a-fA-F]{64}", k):
        return "evm"
    return None


def _mask(k):
    return f"{k[:4]}…{k[-4:]} (len {len(k)})"


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fomo.die("Playwright not installed: python3 -m pip install playwright && playwright install chromium")

    launch = dict(headless=False, args=["--disable-blink-features=AutomationControlled"],
                  ignore_default_args=["--enable-automation"])
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(PROFILE, channel="chrome", **launch)
        except Exception:
            ctx = p.chromium.launch_persistent_context(PROFILE, **launch)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.set_viewport_size({"width": 1440, "height": 900})
        pg.goto("https://fomo.family", wait_until="domcontentloaded")
        time.sleep(7)
        # Navigate: avatar -> Manage account -> Export keys -> acknowledge -> Continue
        try:
            pg.mouse.click(1410, 32); time.sleep(2)
            pg.click("text=Manage account", timeout=6000); time.sleep(3)
            pg.click("text=Export keys", timeout=6000); time.sleep(3)
            try:
                pg.click("text=I acknowledge the risks", timeout=3000)
            except Exception:
                pg.mouse.click(548, 550)
            time.sleep(1)
            pg.click("text=Continue", timeout=6000); time.sleep(3)
        except Exception as e:
            print(f"(couldn't auto-open the export screen: {str(e)[:60]} — open it manually: "
                  f"avatar → Manage account → Export keys)")
        pg.evaluate("() => navigator.clipboard.writeText('__WAITING__')")

        print("\n➡️  In the browser: click **Export key** for a chain, then **Copy** the key.")
        print("   I'll capture it automatically. Do Solana and/or an EVM chain. (2 min timeout)\n")
        saved = {}
        deadline = time.time() + 120
        last = "__WAITING__"
        while time.time() < deadline and len(saved) < 2:
            try:
                cb = (pg.evaluate("() => navigator.clipboard.readText()") or "").strip()
            except Exception:
                cb = ""
            if cb and cb != last:
                last = cb
                kind = classify(cb)
                if kind and kind not in saved:
                    env_key = "FOMO_WALLET_KEY" if kind == "solana" else "FOMO_EVM_KEY"
                    fomo._set_env_values({env_key: cb})   # store in .env (single source of truth)
                    saved[kind] = _mask(cb)
                    print(f"✅ captured {kind} key {saved[kind]} → wrote {env_key} to .env")
            time.sleep(2)
        ctx.close()

    if saved:
        print("\nDone. Stored:", ", ".join(f"{k} {v}" for k, v in saved.items()))
    else:
        print("\nNo key captured (nothing valid copied). Re-run and click Export key → Copy.")


if __name__ == "__main__":
    main()
