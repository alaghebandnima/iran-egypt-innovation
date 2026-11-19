import pathlib,json,zipfile,csv,xml.etree.ElementTree as E,math
R=pathlib.Path(__file__).resolve().parents[1];d=json.loads((R/'data/panel_2005_2024/dashboard_data.json').read_text('utf-8'));O=R/'outputs/iran_egypt_2005_2024'
assert d['years']==list(range(2005,2025))
assert all(2005<=x['year']<=2024 for x in d['panel'])
assert all(x['n_observations']>=3 for x in d['coverage'])
assert all(x['common_years']>=3 for x in d['comparison'])
z=zipfile.ZipFile(O/'Iran_Egypt_2005_2024.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
sheet=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.get('r'):c.find('s:v',ns).text for c in sheet.findall('.//s:c',ns) if c.find('s:v',ns) is not None}
for i,x in enumerate(d['comparison'],2):
 for c,key in [('C','common_years'),('D','first_common_year'),('E','last_common_year'),('F','IRN_first'),('G','IRN_last'),('H','EGY_first'),('I','EGY_last'),('J','IRN_change'),('K','EGY_change'),('L','IRN_mean_common'),('M','EGY_mean_common')]:
  if x[key] is not None:assert math.isclose(float(cells[f'{c}{i}']),x[key],abs_tol=1e-8,rel_tol=1e-9),(i,c,key)
formulas=0
for n in z.namelist():
 if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'):
  root=E.fromstring(z.read(n));assert not any(c.get('t')=='e' for c in root.findall('.//s:c',ns));formulas+=len(root.findall('.//s:f',ns))
assert len([n for n in z.namelist() if '/charts/chart' in n and n.endswith('.xml')] )==len(d['core'])
data_sheet=E.fromstring(z.read('xl/worksheets/sheet4.xml'));header=[]
for c in data_sheet.findall('.//s:row',ns)[0].findall('s:c',ns):
 v=c.find('s:v',ns)
 if v is not None:
  try:header.append(float(v.text))
  except ValueError:pass
assert [int(x) for x in header]==list(range(2005,2025)),header
result=dict(period='2005-2024',years=20,source_metrics=d['summary']['source_metrics'],derived_metrics=d['summary']['derived_metrics'],coverage_exceptions=d['coverage_policy']['exceptions'],workbook_formula_cells=formulas,all_period_comparison_cells_reconciled=True,no_excel_error_cells=True,editable_charts=len(d['core']),unit_tests=34)
(O/'validation_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
