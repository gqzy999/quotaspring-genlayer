# QuotaSpring

**Deployed:** [0x42A506942589BCEf7C59e98A791cB610f9fEc244](https://explorer-studio.genlayer.com/address/0x42A506942589BCEf7C59e98A791cB610f9fEc244) · [Live evidence](VALIDATION.md) · [Design](DESIGN.md)

A standalone GenLayer primitive for **capped max-min fair allocation of a divisible resource** from individually signed demand statements. Consensus interprets each wallet's maximum demand. Deterministic rational arithmetic computes every quota, proves conservation and cap compliance, and allows each named wallet to claim its exact recorded share once.

## Example

A pool has 11 divisible archive processing credits. Three wallets independently declare maximum demands 2, 9 and 9. Progressive water filling gives exact shares `2`, `9/2`, `9/2`: the small demand saturates first and the others share the remainder equally. No rounding residue goes to the first wallet. A claim records these mathematical rights inside the contract; no physical resource or token is transferred.

## Consensus and allocation certificate

Only a listed wallet can submit its own immutable statement. All statements are required. Leader and validators independently extract EXACT/UNCLEAR plus a whole-number maximum cap for every signer in the fixed unit. They require agreement on the full vector, not just the final allocation. The model receives the unit and signed statements, **not the pool budget**, and never allocates. Source text is retained by code. A malformed response aborts; any accepted UNCLEAR blocks every claim with REVIEW.

For exact caps `c[i]` and budget `B`, code finds a common water level L and sets `a[i] = min(c[i], L)`. Progressive filling saturates smaller caps before dividing the remaining budget equally. Every number is a reduced `[numerator, denominator]` pair; no floating point, rounding or arbitrary remainder order is used. The certificate stores L, all shares, used budget and unallocated excess. Checks require nonnegative cap-respecting shares, `sum(a) = min(B, sum(c))`, and each share equal to its cap or the common level. Claims recompute the allocation before writing.

## State and calls

`COLLECTING → READY → ALLOCATED → CLAIMED`, or `READY → REVIEW`. ALLOCATED persists while some members have not claimed. Zero-cap members still claim `[0,1]`; all members are required for CLAIMED.

| Method | Arguments | Permission |
| --- | --- | --- |
| `open_pool` | pool_id, budget, unit, members_json | Caller fixes new pool |
| `declare` | owner, pool_id, statement | Named signer, once |
| `allocate` | owner, pool_id | Anyone; READY only |
| `claim` | owner, pool_id, allocation_digest | Named signer, once |
| `get_pool` | owner, pool_id | Public JSON snapshot |
| `get_protocol` | none | `quotaspring-1` |

Budget: integer 1–10000. Unit description: 5–120 characters. Members: 2–5 distinct nonzero wallet addresses, JSON 80–260 characters. Statements: 30–600 characters. Caps: exact whole numbers 0–10000 in the declared unit. Minimums, estimates, ranges, conflicting quantities, conditions, unrelated units and embedded commands require review. Text boundaries are trimmed. IDs use 1–40 ASCII letters/digits/underscore/hyphen. No member edits, replacement, cancellation or administrator override.

The allocation digest binds protocol, owner, ID, budget, unit, members, signed statements, accepted caps, allocation and the initial ALLOCATED/REVIEW status using SHA-256 of sorted compact Python JSON. Subsequent claims and the terminal CLAIMED state do not change that fixed content digest. A digest alone does not prove claims: verify the full finalized record.

See [examples/pool.json](examples/pool.json). Deploy `contracts/quota_spring.py` without constructor arguments. Open through `writeContract({address, functionName:'open_pool', args:[id, budget, unit, JSON.stringify(members)], value:0n, leaderOnly:false})`. Each named wallet signs `declare`; any wallet calls `allocate`; each member signs `claim` with the allocation digest. Reads use `get_pool(owner,id)` and `TransactionHashVariant.LATEST_FINAL`. The verification scripts are complete calling examples. No frontend is needed.

## Limits and trust

A wallet signature proves address control, not a unique person or honest need. The owner chooses membership and budget; one person can control several wallets or exaggerate demands. The allocation is equal-weight max-min fairness across the listed addresses, not a judgment of merit or economic strategy resistance. Independent models can share interpretation errors. Missing statements or uncertainty block the pool; missing claims prevent its terminal state. All data is public. This primitive neither holds funds nor releases real resources: a downstream resource service must authenticate the record and enforce the exact fraction and one-time claim. Do not silently round fractional quotas or use it for indivisible items. No employment, benefits or other high-stakes eligibility determination is intended.

## Run and verify

Node.js 22+ and Python 3.12+:

```sh
npm ci
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
genvm-lint check contracts/quota_spring.py
python scripts/prepare-sdk.py
python sdk-tests/check_sdk.py
node scripts/read-live.mjs
```

The unit suite executes the actual source through a mocked host/model. Direct Mode exercises the pinned official SDK, storage and calldata with mocked model responses. Neither is live consensus. The final command performs only network reads: chain identity, exact source equality, signer/target/method/argument binding, full-consensus finalized receipts, state and deterministic proof checks.

The optional `NEW_TEST=1 node scripts/verify-live.mjs` performs a **new zero-value development deployment and writes**, not a routine read check. Do not run it to recreate already recorded evidence. It generates disposable signing accounts, saves private state outside this repository with restrictive permissions, journals intent before sending, saves hashes before polling, and resumes existing hashes without resending. If a send has an unknown outcome or a transaction fails, inspect it first. There is no automatic Appeal or blind resend. Never fund disposable test accounts; use your own wallet for continuing real integrations without exporting private keys.

## Network and compatibility

Stable Studionet only: **61999**, RPC **https://studio.genlayer.com/api**. The official [network table](https://docs.genlayer.com/developers/networks), [custom equivalence guidance](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle) and installed Studionet preset were checked before deployment. The live script requires chain 61999 and zero gas price before any write intent. `genlayer-js` 1.1.8 and viem 2.57.8 are pinned. The Python runner hash is pinned in the source header. The linter suggests a newer runner; the declared pin is retained and its actual compatibility is recorded through SDK checks and live execution. No compatibility with other networks or future versions is implied.

[Validation and transaction hashes](VALIDATION.md) · [Deployment](deployment.json) · [Public receipts and state](evidence/studionet.json) · [ABI schema](schema.json). MIT licensed.
