import json,pathlib,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import assistant
from engine import grounded_answer,load_data,ROOT
from i18n import set_language


class AssistantTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load_data(ROOT/'data/panel_2005_2024/analysis_with_estimates.json')
 def setUp(self):set_language('fa')
 def tearDown(self):set_language('fa')
 def test_generated_prose_replaces_menu_selection(self):
  g=grounded_answer(self.data,'این شاخص چه محدودیتی دارد؟','IP.PAT.RESD')
  prose='تعداد درخواست‌های ثبت اختراع، فعالیت ثبت دارایی فکری را نشان می‌دهد؛ اما کیفیت اختراع یا موفقیت تجاری آن را مشخص نمی‌کند.'
  with patch('engine._request',return_value={'response':json.dumps(dict(analysis=prose,fact_ids=['F1']))}) as request:
   r=assistant.explain(g)
  self.assertEqual(r['generated_analysis'],prose);self.assertNotEqual(r['explanation_fa'],g['answer'])
  payload=request.call_args.args[1];self.assertNotIn('summary_id',payload['format']['properties']);self.assertIn('analysis',payload['format']['properties'])
 def test_numeric_claims_rejected_even_if_year_was_supplied(self):
  for text in ['در سال 2024 ایران بهتر بوده است و این نتیجه از همه شاخص‌ها تأیید می‌شود.','مقدار شاخص ۹۹۹۹۹۹ است و عملکردی کاملاً بی‌نقص را نشان می‌دهد.']:
   with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis=text,fact_ids=['F1']),{'F1':'fact'},'fa')
 def test_unknown_fact_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='This explanation refers to evidence outside the selected dataset.',fact_ids=['invented']),{'F1':'fact'},'en')
 def test_wrong_language_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='This is an English explanation that should not be published in Persian mode.',fact_ids=['F1']),{'F1':'fact'},'fa')
 def test_malformed_mixed_script_word_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='این شاخص کیفیت درخواست‌های ثبت اختراع را نمی‌ثبt و فقط تعداد درخواست‌ها را می‌شمارد.',fact_ids=['F1']),{'F1':'fact'},'fa')
 def test_unsupported_filing_outcomes_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='This indicator excludes applications that are later rejected or withdrawn.',fact_ids=['F1']),{'F1':'The indicator counts resident patent applications.'},'en')
 def test_estimate_warning_survives_generation(self):
  g=grounded_answer(self.data,'مقالات در ۲۰۲۴ چقدر است؟','IP.JRN.ARTC.SC')
  prose='در تفسیر تعداد مقالات باید به کیفیت پژوهش و ارتباط آن با کاربردهای صنعتی نیز توجه کرد؛ افزایش تعداد مقاله برای اثبات تجاری‌سازی کافی نیست.'
  with patch('engine._request',return_value={'response':json.dumps(dict(analysis=prose,fact_ids=['F1']))}):r=assistant.explain(g)
  self.assertIn('تخمینی',r['explanation_fa']);self.assertIn(g['facts'][0]['text'],r['explanation_fa'])
 def test_busy_request_is_not_reported_as_model_success(self):
  g=grounded_answer(self.data,'۲۰۲۴','IP.PAT.RESD');assistant._slot.acquire()
  try:
   with self.assertRaises(RuntimeError):assistant.explain(g)
  finally:assistant._slot.release()
 def test_timeout_releases_slot(self):
  g=grounded_answer(self.data,'۲۰۲۴','IP.PAT.RESD')
  with patch('engine._request',side_effect=TimeoutError):
   with self.assertRaises(RuntimeError):assistant.explain(g)
  self.assertTrue(assistant._slot.acquire(blocking=False));assistant._slot.release()
 def test_contextual_questions_and_out_of_scope(self):
  self.assertTrue(grounded_answer(self.data,'چرا این شاخص افت کرده؟','IP.PAT.RESD')['needs_model'])
  self.assertTrue(grounded_answer(self.data,'محدودیتش چیه؟','IP.PAT.RESD')['needs_model'])
  self.assertFalse(grounded_answer(self.data,'UNKNOWN.SERIES','IP.PAT.RESD')['needs_model'])
  self.assertFalse(grounded_answer(self.data,'پتنت در ۲۰۳۰ چقدر است؟','IP.PAT.RESD')['needs_model'])
 def test_source_coverage_is_not_filled_coverage(self):
  g=grounded_answer(self.data,'داده موجود است؟','GB.XPD.RSDV.GD.ZS');self.assertIn('11',g['context_facts'][0]['text']);self.assertIn('9',g['context_facts'][0]['text'])

 def test_maximum_is_computed_not_invented(self):
  g=grounded_answer(self.data,'بیشترین پتنت ایران در کدام سال است؟','IP.PAT.RESD')
  maximum=next(f['text'] for f in g['context_facts'] if f['id']=='maximum|IRN')
  self.assertIn('2008',maximum);self.assertIn('15,403',maximum)
 def test_context_uses_explicit_years_in_both_languages(self):
  for lang,q in [('fa','پتنت در ۲۰۱۰ تا ۲۰۱۵'),('en','patents from 2010 to 2015')]:
   set_language(lang);g=grounded_answer(self.data,q,'IP.PAT.RESD')
   self.assertIn('2010',g['context_facts'][0]['text']);self.assertIn('2015',g['context_facts'][0]['text']);self.assertNotIn('2024',g['context_facts'][0]['text'])
 def test_repetition_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis=('This is the same meaningless phrase. '*4),fact_ids=['F1']),{'F1':'fact'},'en')

 def test_unicode_digits_are_not_a_numeric_bypass(self):
  for digits in ['₂₀₂₄','２０２４','۲۰۲۴']:
   with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='The indicator changed during '+digits+' and this proves innovation improved.',fact_ids=['F1']),{'F1':'fact'},'en')
 def test_spelled_out_false_period_rejected(self):
  with self.assertRaises(ValueError):assistant.validate_generated(dict(analysis='این داده‌ها طی چهار دهه نشان می‌دهند که همهٔ اعداد منتشرشده، مشاهدهٔ واقعی هستند.',fact_ids=['F1']),{'F1':'fact'},'fa')
 def test_model_context_contains_no_quantitative_values(self):
  import re
  g=grounded_answer(self.data,'پتنت در ۲۰۲۴ چقدر است؟','IP.PAT.RESD')
  self.assertFalse(any(re.search(r'\d',f['text']) for f in g['qualitative_facts']))
 def test_overall_growth_does_not_hide_annual_declines(self):
  g=grounded_answer(self.data,'چرا این شاخص افت کرده؟','IP.PAT.RESD')
  self.assertTrue(any(f['id']=='variation|IRN' for f in g['qualitative_facts']))

if __name__=='__main__':unittest.main()
