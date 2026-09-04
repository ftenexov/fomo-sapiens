#!/usr/bin/env python3
"""Automated signing-key export — visible window, drives itself.

Private keys are NOT in the page (Privy assembles them in a secure cross-origin iframe), but
we drive that iframe with Playwright: for each address the script clicks **Export key** in
fomo's modal, then **Copy key** inside the Privy iframe, and reads the revealed key from the
clipboard. The key is assembled inside Privy exactly as in the app — we just automate the
clicks — then it is encrypted at rest immediately (masked; never printed).

The browser window is **visible** (a minimized/hidden window proved unreliable for the Privy
reveal and clipboard). **The user must NOT click anything in it until it finishes or is
explicitly prompted** — a stray click can interrupt the automated capture. If the automated
attempts fail, it asks the user to click Export key -> Copy key themselves.

(fomo's app does not render its UI in a true-headless browser, so this uses a real window.)

    python3 export_key.py           # DEFAULT: both keys (Solana + EVM), automated
    python3 export_key.py solana    # only the Solana key
    python3 export_key.py evm       # only the EVM key (Base/Monad/BNB/Robinhood share one)

Needs the login profile (run login.py) + playwright.
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
ATTEMPTS = 3   # silent automated attempts before showing the window to the user


def classify(k):
    # Privy copies the EVM key as 64 hex WITHOUT a 0x prefix; Solana as ~88-char base58.
    if re.fullmatch(r"(0x)?[0-9a-fA-F]{64}", k):
        return "evm"
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{80,90}", k):
        return "solana"
    return None


def _norm(kind, k):
    return "0x" + k if kind == "evm" and not k.startswith("0x") else k


def _mask(k):
    return f"{k[:4]}…{k[-4:]} (len {len(k)})"


def _store(kind, key, captured):
    """Encrypt-and-store the moment a key is captured; record it as captured."""
    captured[kind] = _norm(kind, key)
    fomo.set_key(kind, captured[kind])   # encrypted at rest (Fernet); never printed


def open_export_screen(pg):
    """Navigate: account menu -> Manage account -> Export keys -> acknowledge -> Continue,
    landing on fomo's 'Choose an address to export' modal (one 'Export key' per address)."""
    pg.goto("https://fomo.family", wait_until="domcontentloaded")
    time.sleep(7)
    try:
        # Account menu trigger = the nav button wrapping the /profile/<handle> link.
        try:
            trig = pg.locator('button:has(a[href*="/profile/"])').first
            try:
                trig.hover(timeout=3000)
            except Exception:
                pass
            trig.click(timeout=6000)
        except Exception:
            pg.mouse.click(1410, 32)   # coordinate fallback if the selector changes
        time.sleep(2)
        pg.click("text=Manage account", timeout=6000); time.sleep(3)
        pg.click("text=Export keys", timeout=6000); time.sleep(3)
        try:
            pg.click("text=I acknowledge the risks", timeout=3000)
        except Exception:
            pg.mouse.click(548, 550)
        time.sleep(1)
        pg.click("text=Continue", timeout=6000); time.sleep(3)
    except Exception as e:
        print(f"(couldn't auto-open the export screen: {str(e)[:60]})", file=sys.stderr)


def _read_clip(pg):
    try:
        return (pg.evaluate("() => navigator.clipboard.readText()") or "").strip()
    except Exception:
        return ""


_KEY_RX = r"[1-9A-HJ-NP-Za-km-z]{80,90}|(?:0x)?[0-9a-fA-F]{64}"
_SCAN_JS = (
    "() => { const rx=/" + _KEY_RX + "/;"
    " for (const i of document.querySelectorAll('input,textarea')) { const m=(i.value||'').match(rx); if(m) return m[0]; }"
    " const m=(document.body?document.body.innerText:'').match(rx); return m?m[0]:''; }"
)

# Fixed modal order: Solana row 0, then the EVM rows (Base/Monad/BNB/Robinhood share one key).
ROW = {"solana": 0, "evm": 1}


def _click_copy_key(pg):
    """Click 'Copy key' inside the Privy export iframe (prefers the privy.io frame)."""
    for fr in sorted(pg.frames, key=lambda f: 0 if "privy" in (f.url or "") else 1):
        try:
            loc = fr.get_by_text("Copy key", exact=True)
            if loc.count():
                loc.first.click()
                return True
        except Exception:
            continue
    return False


def _scan_privy_dom(pg):
    """Fallback to reading the revealed key straight from the Privy iframe DOM (in case the
    clipboard is unavailable, e.g. an unfocused/minimized window)."""
    for fr in sorted(pg.frames, key=lambda f: 0 if "privy" in (f.url or "") else 1):
        try:
            v = (fr.evaluate(_SCAN_JS) or "").strip()
            if classify(v):
                return v
        except Exception:
            continue
    return ""


def _reveal_and_read(pg):
    """After 'Export key' is clicked: click 'Copy key' and read the clipboard; if that yields
    nothing (unfocused window), scan the Privy iframe DOM. Returns a key string or ''."""
    copied = False
    for _ in range(8):
        time.sleep(1)
        if _click_copy_key(pg):
            copied = True
            break
    for _ in range(5):
        time.sleep(1)
        cb = _read_clip(pg)
        if cb and cb != "__WAITING__" and classify(cb):
            return cb
    return _scan_privy_dom(pg) if copied or True else ""


def _auto_capture(pg, needed, captured):
    """One automated pass: for each needed chain, open the export modal, click its row's
    'Export key', then read the revealed key (Copy key -> clipboard, DOM fallback). Only the
    Solana (row 0) and EVM/Base (row 1) rows are visited — never brute-forced. Stores on
    capture; validates by key FORMAT so a wrong row can't be miswritten."""
    for kind in [k for k in needed if k not in captured]:
        open_export_screen(pg)
        try:
            pg.evaluate("() => navigator.clipboard.writeText('__WAITING__')")
            pg.get_by_text("Export key", exact=True).nth(ROW[kind]).click()
        except Exception:
            continue
        key = _reveal_and_read(pg)
        if key and classify(key) == kind:
            _store(kind, key, captured)


def _manual_capture(pg, needed, captured):
    """Shown only after automated attempts fail: reopen the screen and watch the clipboard so
    the user clicks Export key -> Copy key themselves for whatever is still missing."""
    open_export_screen(pg)

    def prompt():
        want = [k for k in needed if k not in captured]
        print(f"\n➡️  Couldn't grab the key automatically — in the browser window (now visible) "
              f"click **Export key** then **Copy key** for {PROMPTS[want[0]]}."
              + (f"  (then the same for {PROMPTS[want[1]]})" if len(want) > 1 else ""))
        print("   (the plain 'Copy' button only copies the public address — use 'Copy key')\n", flush=True)

    pg.evaluate("() => navigator.clipboard.writeText('__WAITING__')")
    prompt()
    deadline = time.time() + 300
    last = "__WAITING__"
    while time.time() < deadline and any(k not in captured for k in needed):
        cb = _read_clip(pg)
        if cb and cb != last:
            last = cb
            kind = classify(cb)
            if kind in needed and kind not in captured:
                _store(kind, cb, captured)
                print(f"✅ captured {kind} key {_mask(captured[kind])}", flush=True)
                if any(k not in captured for k in needed):
                    prompt()
            elif kind and kind not in needed:
                print(f"(that looks like the {kind} key — I still need the {needed[0]} key)")
        time.sleep(1)


def run(target="both", allow_manual=True):
    """Capture the needed key(s) into the encrypted store. Returns (captured, missing).

    Opens a VISIBLE browser window and drives the Privy export iframe itself (clicks Export
    key -> Copy key, reads the clipboard). The user must NOT click anything in the window until
    it finishes or is explicitly prompted — a stray click can interrupt the automated capture.
    allow_manual=True (CLI): if the automated attempts fail, prompt the user to click Export
    key -> Copy key themselves. allow_manual=False: never prompt, just report what's missing.
    Raises ImportError if Playwright is unavailable (callers guard)."""
    needed = ["solana", "evm"] if target == "both" else [target]
    from playwright.sync_api import sync_playwright

    launch = dict(headless=False, no_viewport=True,
                  args=["--disable-blink-features=AutomationControlled", "--window-size=1440,900"],
                  ignore_default_args=["--enable-automation"], chromium_sandbox=True)
    captured = {}

    print("🔑 A browser window will open to export your signing keys. DO NOT click anything in "
          "it — it drives itself and finishes on its own (it will prompt you only if it needs a "
          "manual click).", flush=True)

    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(PROFILE, channel="chrome", **launch)
        except Exception:
            ctx = p.chromium.launch_persistent_context(PROFILE, **launch)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()

        # The window stays VISIBLE the whole time — a minimized window proved unreliable for the
        # Privy reveal/clipboard. The user was told above not to click until we're done.
        for _ in range(ATTEMPTS):
            if not any(k not in captured for k in needed):
                break
            try:
                _auto_capture(pg, needed, captured)
            except Exception:
                pass

        # If automation couldn't get it, ask the user to click (the window is already visible).
        if allow_manual and any(k not in captured for k in needed):
            try:
                pg.bring_to_front()
            except Exception:
                pass
            print(f"Automated key export didn't succeed after {ATTEMPTS} tries — please click "
                  f"Export key -> Copy key in the browser window now.", file=sys.stderr)
            _manual_capture(pg, needed, captured)

        ctx.close()

    return captured, [k for k in needed if k not in captured]


def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    if target not in ("solana", "evm", "both"):
        fomo.die("Usage: export_key.py [both|solana|evm]   (default: both — hidden + automated)")
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        fomo.die("Playwright not installed. Run the bootstrap once (installs it + Chromium):\n"
                 "  bash scripts/bootstrap.sh\n"
                 "or: python3 -m pip install playwright && playwright install chromium")
    _, missing = run(target, allow_manual=True)
    if missing:
        fomo.die(f"Could not export {', '.join(missing)} key. Re-run `export_key.py "
                 f"{' '.join(missing) if len(missing) == 1 else 'both'}`.")


if __name__ == "__main__":
    main()
