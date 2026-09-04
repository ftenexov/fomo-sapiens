#!/usr/bin/env python3
"""Semi-automated signing-key export — ONE chain per run.

Private keys are NOT in the page (Privy holds them in a secure enclave) and Privy blocks
fully-automated reveal, so the final click is yours. This drives the browser to fomo's export
screen and watches the clipboard; you click "Export key" then "Copy key" for the requested
address, and it stores the key ENCRYPTED on your machine (masked; the secret is never
printed). You never paste anything - just click "Copy key"; the script reads the clipboard.

    python3 export_key.py           # DEFAULT: both keys in one browser session (click Copy key twice)
    python3 export_key.py solana    # only the Solana key
    python3 export_key.py evm       # only the EVM key (Base/Monad/BNB/Robinhood share one)

Run it once per chain (Solana first, then EVM). Needs the login profile (run login.py) + playwright.
"""
import os
import re
import sys
import time

import _deps  # noqa: F401
import fomo

PROFILE = os.path.join(os.path.dirname(fomo.AUTH_FILE), "browser",
                       os.path.splitext(os.path.basename(fomo.AUTH_FILE))[0])
PROMPTS = {
    "solana": "the **Solana address**",
    "evm": "a **Base address** (any EVM row — Base/Monad/BNB/Robinhood share one key)",
}


def classify(k):
    # Privy copies the EVM key as 64 hex WITHOUT a 0x prefix; Solana as ~88-char base58.
    if re.fullmatch(r"(0x)?[0-9a-fA-F]{64}", k):
        return "evm"
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{80,90}", k):
        return "solana"
    return None


def _mask(k):
    return f"{k[:4]}…{k[-4:]} (len {len(k)})"


def open_export_screen(pg):
    """Navigate: avatar -> Manage account -> Export keys -> acknowledge risks -> Continue."""
    pg.goto("https://fomo.family", wait_until="domcontentloaded")
    time.sleep(7)
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


# signing keys are persisted via fomo.set_key() - encrypted at rest, one file per account


def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    if target not in ("solana", "evm", "both"):
        fomo.die("Usage: export_key.py [both|solana|evm]   (default: both — one browser session, both keys)")
    needed = ["solana", "evm"] if target == "both" else [target]
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fomo.die("Playwright not installed: python3 -m pip install playwright && playwright install chromium")

    launch = dict(headless=False, args=["--disable-blink-features=AutomationControlled"],
                  ignore_default_args=["--enable-automation"], chromium_sandbox=True)
    captured = {}

    def prompt():
        want = [k for k in needed if k not in captured]
        print(f"\n➡️  In the browser: click **Export key** then **Copy key** for {PROMPTS[want[0]]}."
              + (f"  (then the same for {PROMPTS[want[1]]})" if len(want) > 1 else ""))
        print("   (the plain 'Copy' button only copies the public address — use 'Copy key')\n", flush=True)

    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(PROFILE, channel="chrome", **launch)
        except Exception:
            ctx = p.chromium.launch_persistent_context(PROFILE, **launch)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.set_viewport_size({"width": 1440, "height": 900})
        open_export_screen(pg)
        pg.evaluate("() => navigator.clipboard.writeText('__WAITING__')")

        prompt()
        deadline = time.time() + 300   # 5 min
        last = "__WAITING__"
        while time.time() < deadline and any(k not in captured for k in needed):
            try:
                cb = (pg.evaluate("() => navigator.clipboard.readText()") or "").strip()
            except Exception:
                cb = ""
            if cb and cb != last:
                last = cb
                kind = classify(cb)
                if kind in needed and kind not in captured:
                    captured[kind] = "0x" + cb if kind == "evm" and not cb.startswith("0x") else cb
                    print(f"✅ captured {kind} key {_mask(captured[kind])}", flush=True)
                    if any(k not in captured for k in needed):
                        prompt()
                elif kind and kind not in needed:
                    print(f"(that looks like the {kind} key — I need the {needed[0]} key; "
                          f"click Export key → Copy key on {PROMPTS[needed[0]]})")
            time.sleep(1)
        ctx.close()

    missing = [k for k in needed if k not in captured]
    if captured:
        for k, v in captured.items():
            fomo.set_key(k, v)   # encrypted at rest (Fernet), never written to .env in plaintext
        print("🔒 stored (encrypted) " + ", ".join(f"{k} key {_mask(v)}" for k, v in captured.items())
              + f" -> {fomo.keys_file()}")
    if missing:
        fomo.die(f"No {', '.join(missing)} key captured. Re-run `export_key.py {' '.join(missing) if len(missing)==1 else 'both'}` "
                 f"and click Export key → Copy key for {' / '.join(PROMPTS[k] for k in missing)}.")


if __name__ == "__main__":
    main()
