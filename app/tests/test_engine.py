import unittest,pathlib,sys,json,statistics,re
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from engine import *
class DataTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=load_data();cls.ix=index(cls.d)
 def test_twenty_years(self):self.assertEqual(self.d['years'],list(range(2005,2025)))
 def test_unique_keys(self):self.assertEqual(len(self.ix),len(self.d['panel']))
 def test_coverage_policy(self):
  for x in self.d['coverage']:
   if x['indicator'] not in self.d['coverage_policy']['exceptions']:self.assertGreaterEqual(x['n_observations'],15)
 def test_exact_country_grid(self):
  for m in self.d['catalog']:
   for c in ['IRN','EGY']:self.assertEqual(len([x for x in self.d['panel'] if x['country']==c and x['indicator']==m['code']]),20)
 def test_only_active_codes(self):
  codes={m['code'] for m in self.d['catalog']};self.assertEqual({x['indicator'] for x in self.d['panel']},codes);self.assertTrue(set(self.d['core'])<=codes)
 def test_full_metric_names(self):
  for m in self.d['catalog']:self.assertEqual(resolve_metric(self.d,m['name_fa']+' در ۲۰۲۴','IP.PAT.RESD'),m['code'])
 def test_derived_inputs_active(self):
  codes={m['code'] for m in self.d['catalog']}
  for m in self.d['catalog']:
   if m['kind']=='derived':self.assertTrue(set(re.findall(r'[A-Z][A-Z0-9.]+',m['formula']))<=codes)
 def test_source_values(self):
  g=grounded_answer(self.d,'پتنت در ۲۰۲۴ چقدر بوده؟','IP.PAT.RESD');self.assertEqual([x['value'] for x in g['evidence']],[8314,563])
 def test_missing_preserved(self):
  self.assertIsNone(self.ix[('EGY','IP.PAT.RESD',2006)]['value']);self.assertIn('موجود نیست',grounded_answer(self.d,'۲۰۰۶','IP.PAT.RESD')['answer'])
 def test_shared_year_mean(self):
  s=period_summary(self.d,'IP.PAT.RESD');self.assertAlmostEqual(s['country']['EGY']['mean_common'],statistics.mean(self.ix[('EGY','IP.PAT.RESD',y)]['value'] for y in s['common_years']))
 def test_rank_exception(self):
  for c in ['IRN','EGY']:self.assertEqual(sum(x['value'] is not None for x in series(self.d,'GII.RANK',c)),5)
  self.assertTrue(all(x['ratio'] is None for x in annual_comparison(self.d,'GII.RANK')))
 def test_empty_subperiod(self):self.assertEqual(period_summary(self.d,'GII.RANK',2005,2010)['common_count'],0)
 def test_unavailable_metric_guard(self):self.assertFalse(grounded_answer(self.d,'UNKNOWN.SERIES','IP.PAT.RESD')['needs_model'])
 def test_unrecognized_name_guard(self):self.assertFalse(grounded_answer(self.d,'شاخص ساختگی ناشناخته چقدر است؟','IP.PAT.RESD')['needs_model'])
 def test_year_boundary(self):self.assertFalse(grounded_answer(self.d,'۲۰۲۶','IP.PAT.RESD')['needs_model'])
 def test_formula_reconciles(self):
  for c in ['IRN','EGY']:
   for y in range(2005,2025):
    a=self.ix[(c,'IP.PAT.RESD',y)]['value'];p=self.ix[(c,'SP.POP.TOTL',y)]['value'];v=self.ix[(c,'PATENTS_PM',y)]['value']
    if a is not None:self.assertAlmostEqual(v,a/p*1e6)
 def test_model_false_evidence(self):
  g=grounded_answer(self.d,'۲۰۲۴','IP.PAT.RESD')
  with self.assertRaises(ValueError):validate_model_output({'explanation_fa':'متن','evidence_ids':['fake']},g)
 def test_model_false_number(self):
  g=grounded_answer(self.d,'۲۰۲۴','IP.PAT.RESD')
  with self.assertRaises(ValueError):validate_model_output({'explanation_fa':'عدد 999999999','evidence_ids':[g['evidence'][0]['id']]},g)
 def test_valid_model(self):
  g=grounded_answer(self.d,'۲۰۲۴','IP.PAT.RESD');self.assertTrue(validate_model_output({'explanation_fa':'ایران مقدار بیشتری دارد.','evidence_ids':[g['evidence'][0]['id']]},g))
if __name__=='__main__':unittest.main()
