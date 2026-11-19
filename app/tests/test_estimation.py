import sys,pathlib,json,unittest,math
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from estimation import select_method,make_folds,fit_predict
from engine import grounded_answer
from presentation import theme_css
from charts import trend_figure
R=pathlib.Path(__file__).resolve().parents[2];P=R/'data/panel_2005_2024'
class EstimationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads((P/'dashboard_data.json').read_text('utf8'));cls.analysis=json.loads((P/'analysis_with_estimates.json').read_text('utf8'));cls.details=json.loads((P/'estimation_details.json').read_text('utf8'))
 def test_originals_unchanged(self):
  ix={(r['country'],r['indicator'],r['year']):r for r in self.analysis['panel']}
  for r in self.source['panel']:
   x=ix[r['country'],r['indicator'],r['year']];self.assertEqual(x['original_value'],r['value'])
   if r['value'] is not None:self.assertEqual(x['value'],r['value']);self.assertFalse(x['is_estimated'])
 def test_counts_finite(self):
  self.assertEqual(len(self.details['estimates']),self.analysis['estimation_summary']['estimated_values']);self.assertEqual(len(self.details['unresolved']),30)
  self.assertTrue(all(math.isfinite(x['estimated_value']) for x in self.details['estimates']))
  self.assertTrue(all(x['indicator']=='GII.RANK' for x in self.details['unresolved']))
 def test_masks_no_leakage(self):
  for r in self.details['trials']:
   train=set(map(int,r['training_years'].split(';')));masked=set(map(int,r['masked_years'].split(';')))
   self.assertFalse(train&masked)
   if r['gap_kind']=='trailing':self.assertLess(max(train),min(masked))
   if r['gap_kind']=='leading':self.assertGreater(min(train),max(masked))
 def test_minimum_error_selection(self):
  for d in self.details['decisions']:
   scores=[r for r in self.details['scores'] if all(r[k]==d[k] for k in ['country','indicator','gap_kind','gap_length'])]
   if scores:self.assertAlmostEqual(d['validation_MAE'],min(r['MAE'] for r in scores))
 def test_outer_masks_no_leakage(self):
  for r in self.details['nested_audit']:self.assertFalse(set(r['training_years'].split(';'))&set(r['outer_masked_years'].split(';')))
 def test_chart_red_points(self):
  _,tokens=theme_css(True);code=self.details['estimates'][0]['indicator'];fig=trend_figure(self.analysis,code,2005,2024,tokens,'درصد')
  count=sum(sum(y is not None for y in t.y) for t in fig.data if t.mode=='markers' and t.marker.color==tokens['red'])
  self.assertEqual(count,sum(r['is_estimated'] for r in self.analysis['panel'] if r['indicator']==code and r['country'] in ['IRN','EGY']))
 def test_assistant_estimate_warning(self):
  e=next(e for e in self.details['estimates'] if e['method']!='derived')
  r=grounded_answer(self.analysis,str(e['year']),e['indicator']);self.assertIn('تخمینی',r['answer']);self.assertTrue(any(x['is_estimated'] for x in r['evidence']))
if __name__=='__main__':unittest.main()
