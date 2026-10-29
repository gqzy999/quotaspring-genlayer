// Read-only: no accounts, signatures, deployments or writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createClient,abi} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
const root=path.resolve(import.meta.dirname,'..');
const e=JSON.parse(fs.readFileSync(path.join(root,'evidence/studionet.json')));
const client=createClient({chain:studionet});assert.equal(Number(await client.getChainId()),61999);
const source=fs.readFileSync(path.join(root,'contracts/quota_spring.py'),'utf8');assert.equal(crypto.createHash('sha256').update(source).digest('hex'),e.sourceSha256);assert.equal(await client.getContractCode(e.address),source);
const r=JSON.parse(await client.readContract({address:e.address,functionName:'get_pool',args:[e.owner,'credits-demo'],transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));assert.deepEqual(r,e.record);assert.equal(r.status,'CLAIMED');
for(const [name,t] of Object.entries(e.transactions)){
 const tx=await client.getTransaction({hash:t.hash});
 assert.equal(tx.statusName,'FINALIZED');assert.equal(tx.resultName||tx.result_name,'MAJORITY_AGREE');assert.equal(tx.txExecutionResultName||tx.consensus_data?.leader_receipt?.find(x=>x.mode==='leader')?.execution_result,'SUCCESS');assert.equal(tx.leader_only,false);
 assert.equal(tx.from_address.toLowerCase(),t.signer.toLowerCase());assert.equal(tx.to_address.toLowerCase(),e.address.toLowerCase());
 if(t.method==='deploy')assert.equal(Buffer.from(tx.data.contract_code,'base64').toString(),source);
 else{const call=abi.calldata.decode(Buffer.from(tx.data.calldata.base64,'base64'));assert.equal(call.get('method'),t.method);assert.deepEqual(JSON.parse(JSON.stringify(call.get('args'),(_,v)=>typeof v==='bigint'?Number(v):v)),t.args);}
 console.log(name,t.hash,'FINALIZED');
}

function sorted(v){if(Array.isArray(v))return v.map(sorted);if(v!==null&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])]));return v;}
function fingerprint(v){const text=JSON.stringify(sorted(v)).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));return crypto.createHash('sha256').update(text).digest('hex');}
const binding=Object.fromEntries(['protocol','owner','id','budget','unit','members','statements','caps','allocation'].map(k=>[k,r[k]]));binding.status='ALLOCATED';assert.equal(fingerprint(binding),r.digest);
assert.deepEqual(r.allocation.allocation,[[2,1],[9,2],[9,2]]);assert.deepEqual(r.allocation.used,[11,1]);assert.deepEqual(r.allocation.unallocated,[0,1]);assert.deepEqual(r.allocation.level,[9,2]);
assert.equal(Object.keys(r.claims).length,3);
for(const [i,m] of r.members.entries()){const [n,d]=r.allocation.allocation[i],cap=r.caps[i].cap;assert.deepEqual(r.claims[m],[n,d]);assert.equal(r.caps[i].member,m);assert.equal(r.caps[i].source,r.statements[m]);assert.equal(r.caps[i].status,'EXACT');assert.ok(n<=cap*d);assert.ok(n*2===9*d||n===cap*d);}
console.log('VERIFIED: source, exact transactions, full consensus, final state, digest, rational quotas and every signed claim.');
