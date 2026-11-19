import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from selection import valid_group,indicator_options,valid_indicator
class SelectionTests(unittest.TestCase):
 def setUp(self):self.catalog=[dict(code='A',group='Group A'),dict(code='B',group='Group B')]
 def test_empty_frontend_selection_has_valid_fallback(self):
  self.assertEqual(valid_group(self.catalog,None),'ALL')
  self.assertEqual(valid_indicator(indicator_options(self.catalog,'ALL'),None),'A')
 def test_filtered_option_cannot_use_previous_group_code(self):
  self.assertEqual(valid_indicator(indicator_options(self.catalog,'Group B'),'A'),'B')
 def test_code_survives_language_changes(self):
  for _ in range(6):self.assertEqual(valid_indicator(indicator_options(self.catalog,'ALL'),'B'),'B')
 def test_empty_series_validation_is_nonfatal(self):
  from estimation import select_method
  self.assertEqual(select_method({},'internal',1,'SWIID.GINI.DISP')['scores'],[])
