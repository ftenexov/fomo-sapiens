#!/usr/bin/env python3
"""fomo.family EVM sells — ERC-4337 v0.8 userOp signed with the exported EVM key.

Use this ONLY for selling a token that lives on an EVM chain (origin = EVM). Buying an EVM
token, or selling a Solana token, is Solana-origin — use swap.py for those.

Every field/formula here was reverse-engineered and verified against real captures on
Robinhood (4663), Base (8453), and Monad (143): the userOp signature and the first-time
EIP-7702 delegate install both recover to the account address.

Signing key: FOMO_EVM_KEY env var = the exported EVM private key (hex, 0x-prefixed) of the
embedded wallet (Privy "export wallet"). For an EIP-7702 account the account address IS the
signer, so this key both signs userOps and authorizes the delegate install.

Usage:
    python3 swap_evm.py quote   <evmTokenId> <rawAmount>     # e.g. 0xToken:143  1189770004108731933966
    python3 swap_evm.py execute <evmTokenId> <rawAmount>     # build + sign + submit + poll

outTokenId is always Solana USDC (fomo converts all proceeds to SOL USDC). rawAmount is base
units of the token you're selling (get decimals from balances/filterTokens — see SKILL.md).
"""
import json, os, sys, time

from curl_cffi import requests
from eth_abi import encode
from eth_utils import keccak
from eth_account import Account
import rlp

import fomo  # authed, TLS-impersonating client + token refresh

USDC_SOL = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149"
ENTRYPOINT = "0x4337084D9E255Ff0702461CF8895CE9E3b5Ff108"  # v0.8 EntryPoint (all fomo EVM chains)
DELEGATE = "0xe6Cae83BdE06E4c305530e199D7217f42808555B"     # Pimlico Simple7702Account impl
EXECUTE_BATCH = bytes.fromhex("34fcd5be")                    # executeBatch((address,uint256,bytes)[])
# chainId -> fomo edge RPC path segment (node reads). Extend as fomo adds chains.
CHAIN_RPC = {1: "ethereum", 56: "bsc", 143: "monad", 4663: "robinhood", 8453: "base"}


def edge_rpc(auth, chain_id, method, params):
    name = CHAIN_RPC.get(chain_id)
    if not name:
        fomo.die(f"No edge RPC path known for chain {chain_id}; add it to CHAIN_RPC.")
    url = f"https://evm-data.prod-edge.fomo.family/{name}-mainnet/v2"
    r = requests.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                      headers={"content-type": "application/json", "origin": "https://fomo.family",
                               "referer": "https://fomo.family/", "authorization": f"Bearer {auth['accessToken']}"},
                      impersonate=fomo.IMPERSONATE, timeout=30)
    j = r.json()
    if "error" in j:
        fomo.die(f"edge RPC {method} failed: {j['error']}")
    return j["result"]


def bundler_rpc(auth, chain_id, method, params, exec_ctx=None):
    url = f"https://bundler.prod-edge.fomo.family/v2/{chain_id}/rpc"
    headers = {"content-type": "application/json", "origin": "https://fomo.family",
               "referer": "https://fomo.family/", "authorization": f"Bearer {auth['accessToken']}"}
    if exec_ctx:
        headers["fomo-execution-context"] = exec_ctx  # gas-sponsorship grant from /swaps/v2
    r = requests.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                      headers=headers, impersonate=fomo.IMPERSONATE, timeout=30)
    return r.json()


def _b(x):
    return bytes.fromhex(x[2:]) if x and x != "0x" else b""


def quote(auth, evm_token_id, amount):
    status, text = fomo.api_call(auth, "POST", "/swaps/v2",
                                 json.dumps({"inTokenId": evm_token_id, "outTokenId": USDC_SOL,
                                             "amount": str(amount), "retry": 0}))
    body = json.loads(text)
    if status != 200:
        fomo.die(f"Quote failed ({status}): {body.get('message', text[:200])}")
    v2 = body["responseObject"].get("v2Swap")
    if not v2 or v2.get("relayTransaction", {}).get("type") != "EVM":
        fomo.die("Not an EVM-origin sell (relayTransaction.type != EVM). Use swap.py for Solana-origin swaps.")
    return v2


def build_calldata(rt):
    ap, dp = rt["approvalTransaction"], rt["depositTransaction"]
    calls = [(ap["to"], int(ap.get("value", "0")), _b(ap["data"])),
             (dp["to"], int(dp.get("value", "0")), _b(dp["data"]))]
    return EXECUTE_BATCH + encode(["(address,uint256,bytes)[]"], [calls])


def userop_hash_v08(u, chain_id):
    agl = (int(u["verificationGasLimit"], 16) << 128 | int(u["callGasLimit"], 16)).to_bytes(32, "big")
    gf = (int(u["maxPriorityFeePerGas"], 16) << 128 | int(u["maxFeePerGas"], 16)).to_bytes(32, "big")
    th = keccak(text="PackedUserOperation(address sender,uint256 nonce,bytes initCode,bytes callData,"
                     "bytes32 accountGasLimits,uint256 preVerificationGas,bytes32 gasFees,bytes paymasterAndData)")
    struct_hash = keccak(encode(
        ["bytes32", "address", "uint256", "bytes32", "bytes32", "bytes32", "uint256", "bytes32", "bytes32"],
        [th, u["sender"], int(u["nonce"], 16), keccak(_b(u.get("initCode", "0x"))), keccak(_b(u["callData"])),
         agl, int(u["preVerificationGas"], 16), gf, keccak(_b(u.get("paymasterAndData", "0x")))]))
    dth = keccak(text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
    domain = keccak(encode(["bytes32", "bytes32", "bytes32", "uint256", "address"],
                           [dth, keccak(text="ERC4337"), keccak(text="1"), chain_id, ENTRYPOINT]))
    return keccak(b"\x19\x01" + domain + struct_hash)


def execute(auth, evm_token_id, amount):
    key = fomo.get_key("FOMO_EVM_KEY", "evm")
    if not key:
        fomo.die("No EVM key. Set env FOMO_EVM_KEY or run: fomo.py set-key evm <key>")
    acct = Account.from_key(key.strip())

    v2 = quote(auth, evm_token_id, amount)
    chain_id = v2["originChainId"]
    sender = v2["originAddress"]
    if acct.address.lower() != sender.lower():
        fomo.die(f"FOMO_EVM_KEY address {acct.address} != swap origin {sender}. Wrong key.")
    rt = v2["relayTransaction"]
    exec_ctx = v2["executionContext"]
    relay_swap_id = v2.get("relaySwapId")

    print("Quote:", json.dumps({"chain": chain_id, "inUsd": v2.get("inAmountUsd"),
                                "outUsd": v2.get("swapUsdValue"), "expectedOut": v2.get("expectedOutHumanAmount"),
                                "priceImpactPct": v2.get("priceImpactPct"),
                                "warning": (v2.get("priceImpactWarningInfo") or {}).get("warningLevel")}))

    call_data = "0x" + build_calldata(rt).hex()
    # Fresh 192-bit nonce key = current ms timestamp (matches fomo) -> seq 0.
    nonce = (int(time.time() * 1000) << 64)
    ap_gas = int(rt["approvalTransaction"].get("gas", "0"))
    dp_gas = int(rt["depositTransaction"].get("gas", "0"))
    call_gas = ap_gas + dp_gas + (ap_gas + dp_gas) // 2 + 200000  # generous; gas is sponsored (maxFee=0)

    uop = {
        "sender": sender,
        "nonce": hex(nonce),
        "callData": call_data,
        "callGasLimit": hex(call_gas),
        "verificationGasLimit": "0x3d090",
        "preVerificationGas": "0x0",
        "maxFeePerGas": "0x0",
        "maxPriorityFeePerGas": "0x0",
    }

    # First-time on this chain? If the account has no delegated code, attach an EIP-7702 auth.
    code = edge_rpc(auth, chain_id, "eth_getCode", [sender, "latest"])
    if not code.startswith("0xef0100"):
        eoa_nonce = int(edge_rpc(auth, chain_id, "eth_getTransactionCount", [sender, "latest"]), 16)
        auth_msg = keccak(b"\x05" + rlp.encode([chain_id, bytes.fromhex(DELEGATE[2:]), eoa_nonce]))
        s = acct.unsafe_sign_hash(auth_msg)
        uop["eip7702Auth"] = {"address": DELEGATE, "chainId": hex(chain_id), "nonce": hex(eoa_nonce),
                              "r": hex(s.r), "s": hex(s.s), "yParity": hex(s.v - 27 if s.v >= 27 else s.v)}
        print(f"Account not yet delegated on chain {chain_id} — attaching EIP-7702 install.")

    # Sign the v0.8 userOp digest with the exported key (recovers to the account itself).
    digest = userop_hash_v08(uop, chain_id)
    sig = acct.unsafe_sign_hash(digest)
    uop["signature"] = "0x" + sig.r.to_bytes(32, "big").hex() + sig.s.to_bytes(32, "big").hex() + \
                       (sig.v if sig.v >= 27 else sig.v + 27).to_bytes(1, "big").hex()

    res = bundler_rpc(auth, chain_id, "eth_sendUserOperation", [uop, ENTRYPOINT], exec_ctx=exec_ctx)
    if "error" in res:
        fomo.die(f"eth_sendUserOperation rejected: {json.dumps(res['error'])[:300]}")
    uo_hash = res["result"]
    print(f"Submitted userOp: {uo_hash}")

    # Poll for the on-chain receipt, then the relay bridge to Solana USDC.
    for _ in range(30):
        time.sleep(3)
        r = bundler_rpc(auth, chain_id, "eth_getUserOperationReceipt", [uo_hash])
        if r.get("result"):
            ok = r["result"].get("success")
            print(f"userOp mined: success={ok} txHash={r['result'].get('receipt', {}).get('transactionHash')}")
            break
    else:
        print("userOp not mined within timeout; check later with eth_getUserOperationReceipt.")

    if relay_swap_id:
        print(f"Relay bridging to USDC — poll: python3 swap.py status {relay_swap_id}")
    print(json.dumps({"userOpHash": uo_hash, "relaySwapId": relay_swap_id, "chain": chain_id}, indent=2))


def main():
    args = sys.argv[1:]
    if len(args) < 3 or args[0] not in ("quote", "execute"):
        fomo.die("Usage: swap_evm.py quote|execute <evmTokenId> <rawAmount>")
    auth = fomo._ensure_fresh(fomo.load_auth())
    if args[0] == "quote":
        v2 = quote(auth, args[1], args[2])
        s = {k: v2.get(k) for k in ("originChainId", "inAmountUsd", "swapUsdValue",
                                    "expectedOutHumanAmount", "priceImpactPct", "relaySwapId")}
        s["warning"] = (v2.get("priceImpactWarningInfo") or {}).get("warningLevel")
        print(json.dumps(s, indent=2))
    else:
        execute(auth, args[1], args[2])


if __name__ == "__main__":
    main()
