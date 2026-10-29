"""Pinned official SDK/storage; mocked LLM, not network consensus."""
import json
from pathlib import Path
from gltest.direct import VMContext,deploy_contract
root=Path(__file__).resolve().parents[1];ex=json.loads((root/'examples/pool.json').read_text());members=['0x'+str(i)*40 for i in [1,2,3]]
answer={'caps':[{'member':m,'status':'EXACT','cap':c,'reason':'The signer explicitly states this maximum demand in the declared unit.'} for m,c in zip(members,[2,9,9])]}
vm=VMContext();vm.sender=members[0];vm.mock_llm('^Extract each signers',json.dumps(answer))
with vm.activate():
 c=deploy_contract(root/'contracts/quota_spring.py',vm,sdk_version='v0.3.0-rc7');c.open_pool('sdk',ex['budget'],ex['unit'],json.dumps(members))
 for m,s in zip(members,ex['statements']):
  with vm.prank(m):c.declare(members[0],'sdk',s)
 r=json.loads(c.allocate(members[0],'sdk'));assert r['allocation']['allocation']==[[2,1],[9,2],[9,2]]
 assert vm.run_validator() is True
 vm.clear_mocks();answer['caps'][1]['cap']=8;vm.mock_llm('^Extract each signers',json.dumps(answer));assert vm.run_validator() is False
 for m in members:
  with vm.prank(m):r=json.loads(c.claim(members[0],'sdk',r['digest']))
 assert r['status']=='CLAIMED'
print('PASS: official SDK storage/calldata, exact fractions, signed declarations, validator acceptance/rejection and claims (mocked LLM).')
