# Validation

Recorded 2026-10-29 on Stable Studionet, chain **61999**, RPC **https://studio.genlayer.com/api**.

## Local tests: simulated semantics

- **12 unit tests passed**, including 9300 combinations of 2–4 caps from 0–4 and budgets 1–12. Exact rational conservation, cap compliance, common-level fairness, unused capacity and permutation symmetry passed.
- Signed member slots, one declaration/claim per address, all-signature readiness, budget withholding from model input, immutable records, digests, malformed outputs, uncertainty and independent validator disagreement passed.
- Official linter: 3 checks passed; SDK validation passed; 6 public methods (4 write, 2 view).
- Pinned official SDK Direct Mode passed storage/calldata, signed declarations, fractional allocations, validator acceptance/rejection and all three claims, with a mocked LLM.

These are local tests, not actual network consensus or proof of general model accuracy.

## Real network evidence

Contract: `0x42A506942589BCEf7C59e98A791cB610f9fEc244`.
Source SHA-256: `13da0b536538fa112a8eacac66e5b18a0d759052475e1cc89358366fc883a8e6`.

Nine distinct full-consensus transactions completed with **FINALIZED / MAJORITY_AGREE / SUCCESS** and `leader_only=false`. Zero-value writes; no cash funding, Appeal or transaction resend.

| Step | Transaction hash |
| --- | --- |
| deploy | `0x021f3d2fa1e722e93f46996ba92d39fa860ffcbd0e20c8432fa3206101462e5c` |
| open | `0xd7d846193708edd4323d90632414bdb3f0240ce96307363783f4fe4caa92489b` |
| declare_0 | `0x98f935f4c580c916869b875b49c8ec30ce1dc1eff0f4006418993a6622795b9c` |
| declare_1 | `0xe4db0c899e1248e2a2e2b372b77de528cad048b189b1e90fdb35f4ca30ac71f9` |
| declare_2 | `0xbaac25c601661fa4b6d91b1e55a2023dd2d84180c981f5196d671ae225c37052` |
| allocate | `0x4b1fa964d96af38e5b0b08f57c805279e07031d7ee430e78d4d1f34e61cd1752` |
| claim_0 | `0xa5ac43095d6b4b7042677b9abae3f5e58f7f800b136e16f3f34dec4ef551fee5` |
| claim_1 | `0xf16f02c237e7b50c7bca49e7927c3371f8eeddae387911d428329f837d24dcb2` |
| claim_2 | `0xa37c4c5472490aee5cae3a8f2f907c183611fd77653e5058073df8a595926a07` |

The synthetic archive-credit pool ended **CLAIMED**. Accepted caps were `[2,9,9]`, budget 11, water level `[9,2]`, shares `[[2,1],[9,2],[9,2]]`, used `[11,1]`, unallocated `[0,1]`. Every member signed and claimed its own slot. All three development wallets are controlled by one operator; this is not evidence of independent people, truthful need or real resource delivery.

Deployed source was compared byte-for-byte with the source file. [evidence/studionet.json](evidence/studionet.json) retains the complete final record, transaction arguments and public receipt projections including consensus votes and leader execution payloads. Node configuration, timing logs and redundant byte arrays are omitted.

Only the successful exact-cap fixture was tested on chain. Ambiguous caps, disagreement, malformed inputs, rejected claims and spare-budget cases are local tests; no live result is claimed for those paths. No token, payment or external resource was transferred.

`node scripts/read-live.mjs` fetches existing receipts and finalized state without signing. It checks chain ID, exact source, sender/target/method/arguments, full-consensus finality and execution, content digest, expected rational allocation and all member claims. It does not repeat transactions. A content digest alone cannot prove claim completion; the whole finalized record is checked.
