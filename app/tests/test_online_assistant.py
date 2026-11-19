import unittest,json,pathlib,sys,tempfile,os
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import online_assistant as oa
from i18n import set_language
from engine import load_data,ROOT
class OnlineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load_data(ROOT/'data/panel_2005_2024/analysis_with_estimates.json')
 def setUp(self):set_language('fa')
 def test_exact_short_values(self):
  g=oa.prepare(self.data,'پتنت در ۲۰۲۴ چقدر است؟','IP.PAT.RESD',2005,2024)
  self.assertIn('8,314',g['compact_numeric']);self.assertIn('563',g['compact_numeric'])
  a=oa.short_answer(g,'این مقایسه کیفیت اختراع را نشان نمی‌دهد. تفاوت ساختارها هم قابل بحث است.')
  self.assertIn('8,314',a);self.assertNotIn('ساختارها',a)
 def test_source_coverage(self):
  g=oa.prepare(self.data,'داده موجود است؟','GB.XPD.RSDV.GD.ZS',2005,2024)
  self.assertIn('11 سال دادهٔ منبع، 9 سال تخمین پروژه',g['compact_numeric']);self.assertIn('20 سال دادهٔ منبع، 0 سال تخمین پروژه',g['compact_numeric'])
 def test_extrema_and_country(self):
  g=oa.prepare(self.data,'بیشترین پتنت ایران در کدام سال است؟','IP.PAT.RESD',2005,2024)
  self.assertIn('15,403',g['compact_numeric']);self.assertIn('2008',g['compact_numeric']);self.assertNotIn('مصر',g['compact_numeric'])
 def test_estimate_marker(self):
  g=oa.prepare(self.data,'مقالات در ۲۰۲۴ چقدر است؟','IP.JRN.ARTC.SC',2005,2024)
  self.assertTrue(g['compact_estimated']);self.assertIn('تخمین پروژه',g['compact_numeric'])
 def test_cause_caveat(self):
  g=oa.prepare(self.data,'چرا این شاخص افت کرده؟','IP.PAT.RESD',2005,2024)
  self.assertIn('به‌تنهایی علت',oa.short_answer(g,'در طول دوره نوسان وجود دارد. توضیح اضافی.'))
 def test_cause_keeps_relevant_trend(self):
  g=oa.prepare(self.data,'چرا این شاخص افت کرده؟','IP.PAT.RESD',2005,2024)
  result=oa.short_answer(g,'این شاخص تعداد درخواست‌ها را می‌شمارد. در داخل بازه افزایش و کاهش سالانه دیده می‌شود.')
  self.assertIn('سالانه',result);self.assertNotIn('می‌شمارد',result);self.assertIn('به‌تنهایی علت',result)
 def test_cache_is_shared_and_bounded(self):
  with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'INNOVATION_ASSISTANT_CACHE':str(pathlib.Path(t)/'cache.sqlite')}):
   g=oa.prepare(self.data,'این شاخص چه محدودیتی دارد؟','IP.PAT.RESD',2005,2024)
   with patch('engine.explain_with_ollama',return_value={'generated_analysis':'این شاخص تعداد درخواست‌ها را می‌شمارد و کیفیت اختراع را نشان نمی‌دهد.'}) as call:
    oa.answer(g);r=oa.answer(g);self.assertTrue(r['cache_hit']);self.assertEqual(call.call_count,1)
   with oa.connection() as c:
    for i in range(70):c.execute('INSERT OR REPLACE INTO answers VALUES (?,?,?)',(str(i),'{}',i))
   with patch('engine.explain_with_ollama',return_value={'generated_analysis':'این شاخص تعداد درخواست‌ها را می‌شمارد و کیفیت اختراع را نشان نمی‌دهد.'}):oa.answer(dict(g,question='محدودیت جدید'))
   with oa.connection() as c:self.assertEqual(c.execute('SELECT count(*) FROM answers').fetchone()[0],64)
if __name__=='__main__':unittest.main()
