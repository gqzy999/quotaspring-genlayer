"""Deployable source under a mocked host and model. Not network consensus."""
import importlib.util,itertools,json,sys,types,unittest
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1];A='0x'+'1'*40;B='0x'+'2'*40;C='0x'+'3'*40;D='0x'+'4'*40
class Return:
 def __init__(self,x):self.calldata=x
class Public:
 write=staticmethod(lambda f:f);view=staticmethod(lambda f:f)
gl=types.SimpleNamespace(Contract=object,public=Public(),message=types.SimpleNamespace(sender_address=A),vm=types.SimpleNamespace(Return=Return,UserError=ValueError),nondet=types.SimpleNamespace())
sys.modules['genlayer']=types.SimpleNamespace(gl=gl,TreeMap=dict)
spec=importlib.util.spec_from_file_location('p',ROOT/'contracts/quota_spring.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
EX=json.loads((ROOT/'examples/pool.json').read_text());MEMBERS=[A,B,C]
def answer():return {'caps':[{'member':m,'status':'EXACT','cap':c,'reason':'The signer explicitly states this maximum demand in the declared unit.'} for m,c in zip(MEMBERS,[2,9,9])]}
class Tests(unittest.TestCase):
 def setUp(self):
  gl.message.sender_address=A;self.c=p.QuotaSpring();self.answer=answer();self.second=None;self.calls=0
  def llm(*a,**kw):self.calls+=1;return self.second if self.calls>1 and self.second is not None else self.answer
  gl.nondet.exec_prompt=llm
  def run(l,v):
   x=l()
   if not v(Return(x)):raise ValueError('DISAGREE')
   return x
  gl.vm.run_nondet_unsafe=run;self.c.open_pool('p',EX['budget'],EX['unit'],json.dumps(MEMBERS))
 def ready(self):
  for m,s in zip(MEMBERS,EX['statements']):gl.message.sender_address=m;self.c.declare(A,'p',s)
 def test_fractional_lifecycle_and_all_claims(self):
  self.ready();r=json.loads(self.c.allocate(A,'p'));self.assertEqual(r['allocation']['allocation'],[[2,1],[9,2],[9,2]])
  for m in MEMBERS:gl.message.sender_address=m;r=json.loads(self.c.claim(A,'p',r['digest']))
  self.assertEqual(r['status'],'CLAIMED');self.assertEqual(len(r['claims']),3)
 def test_one_claim_cannot_finish_pool(self):
  self.ready();r=json.loads(self.c.allocate(A,'p'));gl.message.sender_address=A;r=json.loads(self.c.claim(A,'p',r['digest']));self.assertEqual(r['status'],'ALLOCATED')
 def test_no_duplicate_claim(self):
  self.ready();r=json.loads(self.c.allocate(A,'p'));self.c.claim(A,'p',r['digest'])
  with self.assertRaisesRegex(ValueError,'CLAIM_LOCKED'):self.c.claim(A,'p',r['digest'])
 def test_signer_and_duplicate_guards(self):
  gl.message.sender_address=D
  with self.assertRaisesRegex(ValueError,'NOT_MEMBER'):self.c.declare(A,'p',EX['statements'][0])
  gl.message.sender_address=A;self.c.declare(A,'p',EX['statements'][0])
  with self.assertRaisesRegex(ValueError,'DECLARATION_LOCKED'):self.c.declare(A,'p',EX['statements'][0])
 def test_all_signatures_required(self):
  with self.assertRaisesRegex(ValueError,'NOT_READY'):self.c.allocate(A,'p')
 def test_digest_and_nonmember_claim(self):
  self.ready();r=json.loads(self.c.allocate(A,'p'))
  with self.assertRaisesRegex(ValueError,'DIGEST_MISMATCH'):self.c.claim(A,'p','bad')
  gl.message.sender_address=D
  with self.assertRaisesRegex(ValueError,'CLAIM_LOCKED'):self.c.claim(A,'p',r['digest'])
 def test_unclear_blocks_all_claims(self):
  self.ready();self.answer['caps'][0].update(status='UNCLEAR',cap=None);r=json.loads(self.c.allocate(A,'p'));self.assertEqual(r['status'],'REVIEW')
  with self.assertRaisesRegex(ValueError,'NOT_ALLOCATED'):self.c.claim(A,'p',r['digest'])
 def test_independent_disagreement_atomic(self):
  self.ready();self.second=answer();self.second['caps'][1]['cap']=8
  with self.assertRaisesRegex(ValueError,'DISAGREE'):self.c.allocate(A,'p')
  self.assertEqual(json.loads(self.c.get_pool(A,'p'))['status'],'READY')
 def test_budget_not_in_model_prompt(self):
  self.ready();captured=[]
  def llm(prompt,**kw):captured.append(prompt);return self.answer
  gl.nondet.exec_prompt=llm;self.c.allocate(A,'p');self.assertTrue(all('"budget"' not in x for x in captured))
 def test_malformed_model(self):
  self.ready();self.answer['caps'][0]['cap']=True
  with self.assertRaisesRegex(ValueError,'CAP_BOUNDS'):self.c.allocate(A,'p')
 def test_no_overwrite_or_reallocate(self):
  with self.assertRaisesRegex(ValueError,'ID_USED'):self.c.open_pool('p',11,EX['unit'],json.dumps(MEMBERS))
  self.ready();self.c.allocate(A,'p')
  with self.assertRaisesRegex(ValueError,'NOT_READY'):self.c.allocate(A,'p')
 def test_exhaustive_waterfill_properties(self):
  for n in range(2,5):
   for caps in itertools.product(range(5),repeat=n):
    for budget in range(1,13):
     r=p.waterfill(budget,list(caps));alloc=[Fraction(*q) for q in r['allocation']];level=Fraction(*r['level'])
     self.assertEqual(sum(alloc),min(budget,sum(caps)));self.assertEqual(Fraction(*r['unallocated']),budget-sum(alloc))
     self.assertTrue(all(q==min(c,level) for q,c in zip(alloc,caps)))
     self.assertEqual(p.waterfill(budget,list(reversed(caps)))['allocation'],list(reversed(r['allocation'])))
if __name__=='__main__':unittest.main()
