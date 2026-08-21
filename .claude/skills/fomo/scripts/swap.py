#!/usr/bin/env python3
"""fomo.family trading — quote, sign (solana), submit via Jito, check status.

Signing key: FOMO_WALLET_KEY env var = base58-encoded solana secret key exported from the
fomo/Privy "export wallet" UI. Without it, only quoting works.

Usage:
    python3 swap.py quote   <inTokenId> <outTokenId> <rawAmount>
    python3 swap.py execute <inTokenId> <outTokenId> <rawAmount>     sign + submit
    python3 swap.py status  <relaySwapId>                            cross-chain swaps only

tokenId = "<address>:<chainId>"; solana chainId=1399811149. rawAmount is base units
(USDC has 6 decimals: $3 => 3000000). USDC(sol): EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
"""
import base64, json, os, sys

from curl_cffi import requests

import fomo  # reuse the authed, TLS-impersonating client

JITO = "https://mainnet.hudson.jito.wtf/api/v1/sendTransactionWeb?mev_protection_default=true"


def quote(in_id, out_id, amount):
    auth = fomo._ensure_fresh(fomo.load_auth())
    status, text = fomo.api_call(auth, "POST", "/swaps/v2",
                                 json.dumps({"inTokenId": in_id, "outTokenId": out_id,
                                             "amount": str(amount), "retry": 0}))
    body = json.loads(text)
    if status != 200:
        fomo.die(f"Quote failed ({status}): {body.get('message', text[:200])}")
    return body["responseObject"]


def summarize(q):
    s = q.get("v1Swap") or q.get("v2Swap")
    return {
        "kind": "same-chain (solana)" if q.get("v1Swap") else "cross-chain (relay)",
        "swapUsdValue": s.get("swapUsdValue"),
        "expectedOut": s.get("expectedOutHumanAmount"),
        "priceImpactPct": s.get("priceImpactPct"),
        "warning": (s.get("priceImpactWarningInfo") or {}).get("warningLevel"),
        "relaySwapId": q.get("v2Swap", {}).get("relaySwapId"),
    }


def sign_and_submit(q):
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solders.message import to_bytes_versioned
    from solders.signature import Signature
    from solders.pubkey import Pubkey

    key = fomo.get_key("FOMO_WALLET_KEY", "solana")
    if not key:
        fomo.die("No Solana key. Set env FOMO_WALLET_KEY or run: fomo.py set-key solana <key>")
    kp = Keypair.from_base58_string(key.strip())

    is_v1 = "v1Swap" in q
    relay = q.get("v2Swap", {}).get("relayTransaction")
    if not is_v1 and (not relay or relay.get("type") != "SOLANA"):
        fomo.die("Only solana-origin swaps can be signed here. EVM-origin needs ERC-4337 "
                 "userop signing (unsupported) — do those in the app.")
    src = q["v1Swap"] if is_v1 else relay
    if src.get("jitoTipTx"):
        fomo.die("Quote includes a jitoTipTx (bundle submission required) — unsupported; use the app.")

    raw = base64.b64decode(src["swapTransaction"] if is_v1 else src["tx"])
    tx = VersionedTransaction.from_bytes(raw)
    msg = tx.message
    msg_bytes = to_bytes_versioned(msg)
    n = msg.header.num_required_signatures
    keys = list(msg.account_keys)

    user_pub = kp.pubkey()
    fee_pub = Pubkey.from_string(src["feePayerAddress"])
    fee_sig = Signature.from_bytes(base64.b64decode(src["feePayerSignature"]))
    user_sig = kp.sign_message(msg_bytes)

    # Assemble signatures positionally: fee payer + user occupy the required-signer slots.
    sigs = []
    for i in range(n):
        if keys[i] == fee_pub:
            sigs.append(fee_sig)
        elif keys[i] == user_pub:
            sigs.append(user_sig)
        else:
            fomo.die(f"Unexpected required signer at index {i}: {keys[i]} "
                     f"(expected fee payer {fee_pub} or user {user_pub}).")
    signed = VersionedTransaction.populate(msg, sigs)
    b64 = base64.b64encode(bytes(signed)).decode()

    r = requests.post(JITO, headers={"content-type": "text/plain"}, data=b64,
                      impersonate=fomo.IMPERSONATE, timeout=20)
    res = {
        "submitted": r.ok, "httpStatus": r.status_code,
        "txSignature": str(signed.signatures[0]),  # base58 sig = on-chain tx hash
        "relaySwapId": q.get("v2Swap", {}).get("relaySwapId"),
        "lastValidBlockHeight": src.get("lastValidBlockHeight"),
        "note": ("cross-chain: poll `swap.py status <relaySwapId>` until SUCCESS"
                 if q.get("v2Swap") else
                 "same-chain: verify via GET /v2/users/{userId}/swaps (newest first)"),
        "body": r.text[:200],
    }
    print(json.dumps(res, indent=2))
    return res


def main():
    args = sys.argv[1:]
    if not args:
        fomo.die("Usage: swap.py quote|execute <in> <out> <rawAmount> | status <relaySwapId>")
    cmd = args[0]
    if cmd == "quote":
        print(json.dumps(summarize(quote(args[1], args[2], args[3])), indent=2))
    elif cmd == "execute":
        q = quote(args[1], args[2], args[3])
        print("Quote:", json.dumps(summarize(q)))
        sign_and_submit(q)
    elif cmd == "status":
        auth = fomo._ensure_fresh(fomo.load_auth())
        _, text = fomo.api_call(auth, "GET", f"/swaps/v2/status?relaySwapId={args[1]}")
        print(text)
    else:
        fomo.die("Usage: swap.py quote|execute <in> <out> <rawAmount> | status <relaySwapId>")


if __name__ == "__main__":
    main()
