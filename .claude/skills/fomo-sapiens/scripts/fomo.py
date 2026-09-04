#!/usr/bin/env python3
"""fomo.family API client — auth, token refresh, generic API calls.

Transport uses curl_cffi with a Chrome TLS fingerprint: prod-api.fomo.family sits behind
Cloudflare bot management that blocks non-browser TLS fingerprints (plain requests/curl/node
get HTTP 430 regardless of a valid token). curl_cffi impersonation is what makes it work.

Usage:
    python3 fomo.py auth '<json pasted from browser>'   store tokens
    python3 fomo.py refresh                             refresh the privy access token
    python3 fomo.py whoami                              resolve + cache fomo user profile
    python3 fomo.py api GET /watchlist                  authed API call
    python3 fomo.py api POST /proxy/trendingTokens '{}' authed API call with JSON body
    python3 fomo.py ledger [status|off|on|register]     agent ledger: stats / opt out / opt in
"""
import base64, json, os, re, sys, time

import _deps  # noqa: F401  — re-execs into the bootstrap venv if deps are missing
from curl_cffi import requests

IMPERSONATE = "chrome124"
API = "https://prod-api.fomo.family"
PRIVY = "https://auth.privy.io"

DISCLAIMER = (
    "\n⚠️  DISCLAIMER — do NOT use your main fomo.family account with this tool.\n"
    "   This is an unofficial integration. Session tokens are stored in plaintext on this\n"
    "   machine; exported signing keys go in your OS keychain. Use a separate account\n"
    "   holding only funds you can afford to lose. Run `fomo.py logout` to wipe it.\n"
)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.environ.get("FOMO_ENV") or os.path.join(SCRIPTS_DIR, ".env")
_MANAGED_ENV_KEYS = ["FOMO_ACCESS_TOKEN", "FOMO_REFRESH_TOKEN", "FOMO_PRIVY_ACCESS_TOKEN",
                     "FOMO_WALLET_KEY", "FOMO_EVM_KEY", "LEDGER_AGENT_KEY"]
LEDGER_DEFAULT_URL = "https://fomo-skill-api.fly.dev"   # internal agent ledger (trades/PnL/leaderboard)


def _load_dotenv():
    """Load a .env into the environment (without overriding already-set vars).
    Search: $FOMO_ENV, then <skill>/.env, then scripts/.env."""
    here = os.path.dirname(os.path.abspath(__file__))
    for p in filter(None, [os.environ.get("FOMO_ENV"),
                           os.path.join(os.path.dirname(here), ".env"),
                           os.path.join(here, ".env")]):
        if not os.path.isfile(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if v and v[0] not in "\"'" and " #" in v:
                    v = v.split(" #", 1)[0].strip()   # strip inline comment on unquoted values
                if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                    v = v[1:-1]
                os.environ.setdefault(k, v)
        break


_load_dotenv()


def _set_env_values(updates):
    """Insert/replace KEY=value lines in ENV_FILE, preserving comments and other lines.
    Creates the file (from .env.example if present) when missing. mode 600."""
    try:
        with open(ENV_FILE) as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        example = os.path.join(SCRIPTS_DIR, ".env.example")
        lines = open(example).read().splitlines() if os.path.exists(example) else []
    remaining = dict(updates)
    out = []
    for ln in lines:
        m = re.match(r"\s*([A-Z0-9_]+)\s*=", ln)
        if m and m.group(1) in remaining:
            out.append(f"{m.group(1)}={remaining.pop(m.group(1))}")
        else:
            out.append(ln)
    for k, v in remaining.items():
        out.append(f"{k}={v}")
    fd = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(out) + "\n")


def write_env_tokens(access, refresh, pat):
    _set_env_values({"FOMO_ACCESS_TOKEN": access, "FOMO_REFRESH_TOKEN": refresh,
                     "FOMO_PRIVY_ACCESS_TOKEN": pat or ""})


def logout():
    """Full logout: blank the managed .env values, delete the cached tokens/keys and the
    persistent browser profile, so no account state remains."""
    import shutil
    if os.path.exists(ENV_FILE):
        _set_env_values({k: "" for k in _MANAGED_ENV_KEYS})
    kr = _keyring()
    if kr is not None:
        for field in ("solana", "evm"):
            try: kr.delete_password(KEYRING_SERVICE, _key_username(field))
            except Exception: pass
    for path in (AUTH_FILE, keys_file(), _secret_key_file()):
        try: os.remove(path)
        except FileNotFoundError: pass
    stem = os.path.splitext(os.path.basename(AUTH_FILE))[0]
    shutil.rmtree(os.path.join(os.path.dirname(AUTH_FILE), "browser", stem), ignore_errors=True)


def _auth_file():
    """Which account's stored tokens to use. Precedence:
    FOMO_AUTH_FILE (explicit path) > FOMO_PROFILE (~/.config/fomo-sapiens/<profile>.json) > default.
    Set FOMO_PROFILE per shell to keep multiple accounts side by side."""
    if os.environ.get("FOMO_AUTH_FILE"):
        return os.environ["FOMO_AUTH_FILE"]
    base = os.path.expanduser("~/.config/fomo-sapiens")
    prof = os.environ.get("FOMO_PROFILE")
    return os.path.join(base, f"{prof}.json" if prof else "auth.json")


AUTH_FILE = _auth_file()
PRIVY_HEADERS = {
    "privy-app-id": "cm6h485o300n3zj9yl6vpedq7",
    "privy-client-id": "client-WY5gFSayQjxnQhG4rP6SnwPAyPZWZpNRhJ6b9rzMnYwqH",
    "privy-client": "react-auth:3.34.0",
    "origin": "https://fomo.family",       # Privy rejects the call without it (missing_origin)
    "referer": "https://fomo.family/",
}
BROWSER_HEADERS = {
    "origin": "https://fomo.family",
    "referer": "https://fomo.family/",
    "x-supported-chains": "1,56,143,4663,8453,1399811149",
}


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def _unquote(v):
    return json.loads(v) if isinstance(v, str) and len(v) >= 2 and v[0] == '"' and v[-1] == '"' else v


def _seed_from_env(force=False):
    """Seed auth.json from .env tokens (FOMO_ACCESS_TOKEN/FOMO_REFRESH_TOKEN). Runs only when
    auth.json is missing (or force=True), because auth.json is the live store that token refresh
    mutates — .env is just the bootstrap. Re-run `fomo.py reseed` after pasting fresh tokens."""
    at = os.environ.get("FOMO_ACCESS_TOKEN")
    rt = os.environ.get("FOMO_REFRESH_TOKEN")
    if not (at and rt):
        return False
    if os.path.exists(AUTH_FILE) and not force:
        return False
    pat = os.environ.get("FOMO_PRIVY_ACCESS_TOKEN")
    save_auth({"accessToken": _unquote(at), "refreshToken": _unquote(rt),
               "privyAccessToken": _unquote(pat) if pat else None})
    return True


def load_auth():
    try:
        with open(AUTH_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        if _seed_from_env():
            with open(AUTH_FILE) as f:
                return json.load(f)
        die(f"No auth at {AUTH_FILE}. Fill .env (FOMO_ACCESS_TOKEN/FOMO_REFRESH_TOKEN) or run: "
            f"python3 fomo.py auth '<pasted json>' (see README.md).")


def save_auth(a):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    fd = os.open(AUTH_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(a, f, indent=2)


def keys_file():
    """Where signing keys live for the active account: <profile>.keys.json next to auth."""
    base = os.path.dirname(AUTH_FILE)
    stem = os.path.splitext(os.path.basename(AUTH_FILE))[0]  # 'auth' or the profile name
    return os.path.join(base, f"{stem}.keys.json")


KEYRING_SERVICE = "fomo-sapiens"
ENC_PREFIX = "enc:"


def _key_username(field):
    """Keychain account name, per profile + chain, so multiple accounts don't collide."""
    stem = os.path.splitext(os.path.basename(AUTH_FILE))[0]  # 'auth' or the profile name
    return f"{stem}:{field}"


def _keyring():
    """The OS keychain backend (macOS Keychain / Windows Credential Manager / libsecret), or
    None if unavailable (e.g. a headless box with no backend). Best-effort; callers fall back."""
    try:
        import keyring
        from keyring.backends.fail import Keyring as _Fail
        if isinstance(keyring.get_keyring(), _Fail):
            return None
        return keyring
    except Exception:
        return None


# ── encrypted-file fallback (used ONLY when no OS keychain is available) ─────────────────────
def _secret_key_file():
    """Fallback Fernet key file, next to the auth cache (~/.config/fomo-sapiens/secret.key,
    chmod 600). Used only when the OS keychain is unavailable — the keychain is preferred."""
    return os.path.join(os.path.dirname(AUTH_FILE), "secret.key")


def _fernet():
    from cryptography.fernet import Fernet   # ImportError handled by callers
    p = _secret_key_file()
    try:
        with open(p, "rb") as f:
            k = f.read().strip()
        if k:
            return Fernet(k)
    except FileNotFoundError:
        pass
    k = Fernet.generate_key()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(k)
    return Fernet(k)


def encrypt_secret(plaintext):
    """Fallback-file encryption. NEVER stores plaintext: if cryptography is missing it fails
    loudly (run the bootstrap) rather than writing the key in the clear."""
    try:
        return ENC_PREFIX + _fernet().encrypt(plaintext.encode()).decode()
    except ImportError:
        die("Can't secure the signing key: no OS keychain is available and the cryptography "
            "package isn't installed. Run scripts/bootstrap.sh, then retry — keys are never "
            "written in plaintext.")


def decrypt_secret(value):
    """Inverse of encrypt_secret. Plaintext (no enc: prefix) passes through unchanged, so
    env-set keys keep working."""
    if not value or not value.startswith(ENC_PREFIX):
        return value
    try:
        from cryptography.fernet import InvalidToken
    except ImportError:
        die("This signing key is encrypted but the cryptography package is not installed. "
            "Run scripts/bootstrap.sh, then retry.")
    try:
        return _fernet().decrypt(value[len(ENC_PREFIX):].encode()).decode()
    except InvalidToken:
        die("Could not decrypt the stored signing key (secret.key missing or changed). "
            "Re-export it: python3 scripts/export_key.py")


def _file_load_keys():
    try:
        with open(keys_file()) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _file_write_keys(data):
    fd = os.open(keys_file(), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)


def get_key(env_name, field):
    """Resolve a signing key: env var wins (just-in-time), else the OS keychain, else the
    encrypted fallback file. field is 'solana' or 'evm'. Returns None if unset."""
    v = os.environ.get(env_name)
    if v:
        return decrypt_secret(v.strip())
    kr = _keyring()
    if kr is not None:
        try:
            got = kr.get_password(KEYRING_SERVICE, _key_username(field))
            if got:
                return got.strip()
        except Exception:
            pass
    raw = (_file_load_keys().get(field) or "").strip()
    return (decrypt_secret(raw) or None) if raw else None


def set_key(field, value):
    """Store a signing key in the OS keychain (macOS Keychain / Windows Credential Manager /
    libsecret). Falls back to a Fernet-encrypted file only when no keychain is available; never
    stores plaintext. Returns a short label for where it was stored."""
    value = value.strip()
    kr = _keyring()
    if kr is not None:
        try:
            kr.set_password(KEYRING_SERVICE, _key_username(field), value)
            data = _file_load_keys()        # migrate away from any older file entry
            if data.pop(field, None) is not None:
                _file_write_keys(data)
            return "OS keychain"
        except Exception:
            pass
    os.makedirs(os.path.dirname(keys_file()), exist_ok=True)
    data = _file_load_keys()
    data[field] = encrypt_secret(value)     # raises rather than store plaintext
    _file_write_keys(data)
    return keys_file()


def jwt_exp(token):
    try:
        p = token.split(".")[1]
        p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p))["exp"]
    except Exception:
        return 0


def privy_refresh(auth):
    """POST /api/v1/sessions {refresh_token} — verified against @privy-io/react-auth 3.34.0.
    Response is the AuthenticatedUser object; `token` is the customer access token = the bearer
    fomo's API expects. Also carries user.linked_accounts with the embedded wallet addresses."""
    r = requests.post(
        f"{PRIVY}/api/v1/sessions",
        headers={**PRIVY_HEADERS, "content-type": "application/json",
                 "accept": "application/json", "authorization": f"Bearer {auth['accessToken']}"},
        json={"refresh_token": auth["refreshToken"]},
        impersonate=IMPERSONATE, timeout=20,
    )
    body = {}
    try:
        body = r.json()
    except Exception:
        pass
    if r.status_code != 200 or body.get("session_update_action") == "clear" or not body.get("token"):
        die(f"Privy refresh failed ({r.status_code}, action={body.get('session_update_action')}): "
            f"{json.dumps(body)[:300]}\nRefresh token likely expired — re-paste fresh tokens (see SKILL.md).")
    auth["accessToken"] = body["token"]
    if body.get("refresh_token"):
        auth["refreshToken"] = body["refresh_token"]
    if body.get("privy_access_token"):
        auth["privyAccessToken"] = body["privy_access_token"]
    accounts = (body.get("user") or {}).get("linked_accounts", [])
    sol = next((a["address"] for a in accounts if a.get("type") == "wallet" and a.get("chain_type") == "solana"), None)
    evm = next((a["address"] for a in accounts if a.get("type") == "wallet" and a.get("chain_type") == "ethereum"), None)
    if sol:
        auth["_wallets"] = {"sol": sol, "evm": evm, "privyUserId": (body.get("user") or {}).get("id")}
    save_auth(auth)
    return auth


def _ensure_fresh(auth):
    if jwt_exp(auth["accessToken"]) < time.time() + 30:
        return privy_refresh(auth)
    return auth


def api_call(auth, method, path, body=None, _retried=False):
    headers = {**BROWSER_HEADERS, "authorization": f"Bearer {auth['accessToken']}"}
    if body is not None:
        headers["content-type"] = "application/json"
    r = requests.request(
        method, API + path, headers=headers,
        data=body if body is not None else None,
        impersonate=IMPERSONATE, timeout=30,
    )
    if r.status_code in (401, 403, 430, 431) and not _retried:
        auth = privy_refresh(auth)
        return api_call(auth, method, path, body, _retried=True)
    return r.status_code, r.text


def token_meta(auth, token_id):
    """(decimals, symbol) for a '<address>:<chainId>' token, via filterTokens.
    Best-effort: returns (None, "") if it can't be resolved, and never raises."""
    try:
        _, text = api_call(auth, "POST", "/proxy/filterTokens", json.dumps([token_id]))
        tok = json.loads(text)["responseObject"][0]["token"]
        dec = int(tok["decimals"]) if tok.get("decimals") is not None else None
        return dec, (tok.get("symbol") or "")
    except Exception:
        return None, ""


def token_decimals(auth, token_id):
    """Decimals for a '<address>:<chainId>' token, via filterTokens. None if not found."""
    return token_meta(auth, token_id)[0]


# ───────────────────────── agent ledger (best-effort, never blocks) ─────────────────────────
# Trades executed through this skill are reported to an internal ledger that tracks PnL and
# ranks agents. Every call here is best-effort: any failure prints a "[ledger] …" note and the
# login/trade continues. The user can opt out at any time: `fomo.py ledger off`.

def ledger_url():
    """Ledger base URL, or None when disabled. The ledger is **opt-in**: OFF until the user runs
    `fomo.py ledger on` (which sets LEDGER_OPT_IN=1). Also off if LEDGER_URL is blanked."""
    if os.environ.get("LEDGER_OPT_IN", "").strip().lower() not in ("1", "true", "yes"):
        return None
    if "LEDGER_URL" in os.environ and not os.environ["LEDGER_URL"].strip():
        return None
    return (os.environ.get("LEDGER_URL") or LEDGER_DEFAULT_URL).rstrip("/")


def _ledger_call(method, path, key=None, bearer=None, body=None, timeout=15):
    url = ledger_url()
    if not url:
        return None, ""
    headers = {"content-type": "application/json"}
    if key:
        headers["x-agent-key"] = key
    if bearer:
        headers["authorization"] = f"Bearer {bearer}"
    r = requests.request(method, url + path, headers=headers,
                         data=json.dumps(body) if body is not None else None, timeout=timeout)
    return r.status_code, r.text


def ledger_register(auth=None, quiet=False):
    """Register (or re-sync) this account as a ledger agent, keyed by the Solana wallet address
    and proven by an ed25519 signature over a fresh challenge — the Privy/fomo access token is
    NEVER sent to the ledger. Requires the Solana signing key (trading mode); skips silently
    without one. Stores LEDGER_AGENT_KEY. Best-effort — never raises."""
    if not ledger_url():
        return None
    key = get_key("FOMO_WALLET_KEY", "solana")
    if not key:
        return None   # analysis-only (no key to sign with — and nothing to report anyway)
    try:
        from solders.keypair import Keypair
        auth = _ensure_fresh(auth or load_auth())
        prof = whoami(auth)
        handle = prof.get("handle") or prof["userId"][:12]
        kp = Keypair.from_base58_string(key.strip())
        address = str(kp.pubkey())
        ts = int(time.time())
        msg = f"fomo-ledger:v1:register:{address}:{handle}:{ts}".encode()
        signature = str(kp.sign_message(msg))   # base58 ed25519 signature; no token involved
        status, text = _ledger_call("POST", "/agents/register",
                                    body={"handle": handle, "address": address, "ts": ts,
                                          "signature": signature, "fomo_user_id": prof["userId"]})
        if status != 200:
            if not quiet:
                print(f"[ledger] registration failed ({status}) — trades won't be tracked this session (non-fatal)")
            return None
        out = json.loads(text)
        _set_env_values({"LEDGER_AGENT_KEY": out["api_key"]})
        os.environ["LEDGER_AGENT_KEY"] = out["api_key"]
        if not quiet:
            print(f"[ledger] registered as agent '{out['name']}' (wallet-signed; no token sent) — "
                  f"trades tracked at {ledger_url()} (opt out any time: `fomo.py ledger off`)")
        return out["name"]
    except Exception as e:
        if not quiet:
            print(f"[ledger] registration failed (non-fatal): {str(e)[:80]}")
        return None


def ledger_report(side, token_address, network_id, token_amount, usd_value, tx_signature, token_symbol=""):
    """Report an executed trade to the agent ledger. No-op unless opted in. Registers on the fly
    if this account has no agent key yet. Never raises — reporting must not break a completed trade."""
    if not ledger_url():
        return
    try:
        key = os.environ.get("LEDGER_AGENT_KEY")
        if not key:
            if not ledger_register(quiet=True):
                print("[ledger] not registered — trade not tracked (non-fatal)")
                return
            key = os.environ["LEDGER_AGENT_KEY"]
        status, _ = _ledger_call("POST", "/trades", key=key,
                                 body={"side": side, "token_address": token_address, "network_id": str(network_id),
                                       "token_symbol": token_symbol, "token_amount": token_amount,
                                       "usd_value": usd_value, "tx_signature": tx_signature})
        if status == 401:   # stale key (e.g. rotated/deleted server-side) — re-register once
            if ledger_register(quiet=True):
                status, _ = _ledger_call("POST", "/trades", key=os.environ["LEDGER_AGENT_KEY"],
                                         body={"side": side, "token_address": token_address,
                                               "network_id": str(network_id), "token_symbol": token_symbol,
                                               "token_amount": token_amount, "usd_value": usd_value,
                                               "tx_signature": tx_signature})
        print(f"[ledger] reported {side} ({status})" if status == 200
              else f"[ledger] report failed ({status}) — trade is fine, just not tracked")
    except Exception as e:
        print(f"[ledger] report failed (non-fatal): {str(e)[:80]}")


def ledger_status():
    """{'enabled', 'url', 'agent', 'stats'} — stats from GET /me when registered."""
    url = ledger_url()
    out = {"enabled": bool(url), "url": url, "agent": None, "stats": None}
    key = os.environ.get("LEDGER_AGENT_KEY")
    if url and key:
        try:
            status, text = _ledger_call("GET", "/me", key=key)
            if status == 200:
                st = json.loads(text)
                out["agent"] = st.pop("agent", None)
                out["stats"] = st
            else:
                out["error"] = f"GET /me -> {status}"
        except Exception as e:
            out["error"] = str(e)[:80]
    return out


def ledger_opt_out():
    """Opt out: delete this agent + all its trades server-side (best-effort), forget the key,
    and set LEDGER_OPT_IN=0 so nothing is reported until `ledger on`."""
    key = os.environ.get("LEDGER_AGENT_KEY")
    deleted = None
    if ledger_url() and key:
        try:
            status, text = _ledger_call("DELETE", "/me", key=key)
            deleted = json.loads(text).get("deleted_trades") if status == 200 else f"HTTP {status}"
        except Exception as e:
            deleted = f"failed: {str(e)[:60]}"
    _set_env_values({"LEDGER_AGENT_KEY": "", "LEDGER_OPT_IN": "0"})
    os.environ["LEDGER_OPT_IN"] = "0"; os.environ.pop("LEDGER_AGENT_KEY", None)
    return deleted


def ledger_opt_in():
    """Opt in: enable trade tracking, then register (needs the signing key — otherwise it
    registers on the first trade)."""
    _set_env_values({"LEDGER_OPT_IN": "1"})
    os.environ["LEDGER_OPT_IN"] = "1"
    return ledger_register()


def whoami(auth):
    if auth.get("profile"):
        return auth["profile"]
    auth = privy_refresh(auth)  # session response carries the wallet addresses
    w = auth.get("_wallets") or {}
    if not w.get("sol"):
        die("No solana embedded wallet in the privy session response.")
    payload = {"address": w["sol"]}
    if w.get("evm"):
        payload["evmAddress"] = w["evm"]   # omit rather than send null when the EVM wallet isn't provisioned yet
    status, text = api_call(auth, "POST", "/v2/users", json.dumps(payload))
    if status != 200:
        die(f"fomo /v2/users failed ({status}): {text[:300]}")
    user = json.loads(text)["responseObject"]
    auth["profile"] = {"userId": user["id"], "solAddress": w["sol"],
                       "evmAddress": w.get("evm"), "handle": user.get("userHandle")}
    save_auth(auth)
    return auth["profile"]


def account_summary(auth=None):
    """Resolve the account + its balances into a friendly summary, incl. deposit addresses."""
    auth = auth or _ensure_fresh(load_auth())
    prof = whoami(auth)
    status, text = api_call(auth, "GET", f"/v2/users/{prof['userId']}/balances")
    bals = (json.loads(text).get("responseObject") or {}).get("balances", []) if status == 200 else []
    holdings, usd = [], 0.0
    for b in bals:
        bal = b.get("balance", {})
        amt = bal.get("shiftedBalance") or 0
        tfr = b.get("tokenFilterResult") or {}
        price = float(tfr.get("priceUSD") or 0)
        sym = (tfr.get("token") or {}).get("symbol") or (bal.get("tokenAddress", "") or "")[:6]
        if amt:
            holdings.append({"symbol": sym, "amount": amt, "usd": round(amt * price, 2)})
        usd += amt * price
    holdings.sort(key=lambda h: h["usd"], reverse=True)
    return {"handle": prof["handle"], "userId": prof["userId"], "solAddress": prof["solAddress"],
            "evmAddress": prof["evmAddress"], "usdTotal": round(usd, 2),
            "holdings": holdings, "empty": usd < 0.01}


def resolve_trade_id(auth, token_address, network_id=None):
    """Find the user's trade id for a token (needed to attach a thesis). Prefers an
    active/open trade, falls back to the most recent closed one."""
    uid = whoami(auth)["userId"]
    q = f"/trades?userId={uid}&tokenAddress={token_address}"
    if network_id:
        q += f"&networkId={network_id}"
    status, text = api_call(auth, "GET", q)
    if status != 200:
        die(f"resolve-trade failed ({status}): {text[:200]}")
    ro = json.loads(text)["responseObject"]
    trades = (ro.get("activeTrades") or []) + (ro.get("closedTrades") or [])
    if not trades:
        die(f"No trade found for {token_address} — buy the token first, then post the thesis.")
    tr = trades[0]["trade"]
    return {"tradeId": tr["id"], "hasThesis": bool(tr.get("commentId")), "closedAt": tr.get("closedAt")}


def post_thesis(auth, tradeId, text, visibility="public"):
    """POST /trades/comment — the endpoint fomo uses for both theses (top-level comment on
    your OWN trade) and comments. Route/body/success verified end-to-end from a Charles capture
    ("Trade comment created successfully", 200). This endpoint intermittently 500s, so retry once."""
    body = json.dumps({"tradeId": tradeId, "comment": text, "visibility": visibility})
    status, resp = api_call(auth, "POST", "/trades/comment", body)
    if status == 500:
        status, resp = api_call(auth, "POST", "/trades/comment", body)  # transient 500 seen in captures
    return status, resp


def main():
    args = sys.argv[1:]
    if not args:
        die("Commands: auth | logout | refresh | whoami | api | balances | show-account | set-key | resolve-trade | post-thesis")
    cmd = args[0]

    if cmd == "auth":
        pasted = json.loads(args[1])
        if not pasted.get("accessToken") or not pasted.get("refreshToken"):
            die("Expected JSON with accessToken and refreshToken.")
        # localStorage stores each token JSON-quoted ("\"eyJ...\""); unwrap to the bare value.
        unq = lambda v: json.loads(v) if isinstance(v, str) and v.startswith('"') and v.endswith('"') else v
        save_auth({"accessToken": unq(pasted["accessToken"]),
                   "refreshToken": unq(pasted["refreshToken"]),
                   "privyAccessToken": unq(pasted.get("privyAccessToken")) if pasted.get("privyAccessToken") else None})
        exp = jwt_exp(unq(pasted["accessToken"]))
        when = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(exp)) if exp > time.time() else "EXPIRED (will auto-refresh)"
        print(f"Saved to {AUTH_FILE}. Access token: {when}.")
        ledger_register()

    elif cmd == "refresh":
        a = privy_refresh(load_auth())
        print(f"Refreshed. New expiry: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(jwt_exp(a['accessToken'])))}")

    elif cmd == "whoami":
        print(json.dumps(whoami(load_auth()), indent=2))

    elif cmd == "api":
        method, path = args[1], args[2]
        body = args[3] if len(args) > 3 else None
        auth = _ensure_fresh(load_auth())
        status, text = api_call(auth, method.upper(), path, body)
        if status != 200:
            print(f"HTTP {status}", file=sys.stderr)
        print(text)
        sys.exit(0 if status == 200 else 1)

    elif cmd == "balances":
        print(json.dumps(account_summary(), indent=2))

    elif cmd == "show-account":
        # Everything the agent should relay to the user in chat: balance + signing keys.
        s = account_summary()
        s["solanaKey"] = get_key("FOMO_WALLET_KEY", "solana")
        s["evmKey"] = get_key("FOMO_EVM_KEY", "evm")
        print(json.dumps(s, indent=2))

    elif cmd == "ledger":
        sub = args[1] if len(args) > 1 else "status"
        if sub == "off":
            d = ledger_opt_out()
            print(f"Opted out of the agent ledger. Server-side data deleted: {d}. "
                  "Nothing will be reported until `fomo.py ledger on`.")
        elif sub == "on":
            name = ledger_opt_in()
            print("Opted in." if name else "Opted in, but registration failed (will retry on next login/trade).")
        elif sub == "register":
            ledger_register()
        else:
            print(json.dumps(ledger_status(), indent=2))

    elif cmd == "logout":
        logout()
        print("Logged out: cleared .env tokens/keys, cached session, and browser profile.")

    elif cmd == "reseed":
        # Force-refresh auth.json from the current .env tokens (after pasting fresh ones).
        if _seed_from_env(force=True):
            print(f"Reseeded {AUTH_FILE} from .env tokens.")
        else:
            die("No FOMO_ACCESS_TOKEN/FOMO_REFRESH_TOKEN in .env/env to seed from.")

    elif cmd == "set-key":
        # set-key <solana|evm> <key>  — stores to the active account's keys file (chmod 600)
        field, value = args[1], args[2]
        if field not in ("solana", "evm"):
            die("Usage: fomo.py set-key <solana|evm> <key>")
        path = set_key(field, value)
        print(f"Stored {field} key for this account at {path} (mode 600).")

    elif cmd == "resolve-trade":
        token = args[1]
        net = args[2] if len(args) > 2 else None
        print(json.dumps(resolve_trade_id(_ensure_fresh(load_auth()), token, net), indent=2))

    elif cmd == "post-thesis":
        # post-thesis <tokenAddress> <networkId> <text> [visibility]
        token, net, text = args[1], args[2], args[3]
        visibility = args[4] if len(args) > 4 else "public"
        auth = _ensure_fresh(load_auth())
        info = resolve_trade_id(auth, token, net)
        if info["hasThesis"]:
            print(f"Note: this trade already has a thesis (commentId set). Posting anyway would add another comment.", file=sys.stderr)
        status, resp = post_thesis(auth, info["tradeId"], text, visibility)
        print(f"tradeId={info['tradeId']} status={status}")
        print(resp)
        sys.exit(0 if status == 200 else 1)

    else:
        die("Commands: auth | logout | refresh | whoami | api | balances | show-account | set-key | resolve-trade | post-thesis")


if __name__ == "__main__":
    main()
