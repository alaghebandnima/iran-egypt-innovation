"""Audit every generated data store against the sole active catalog."""
import pathlib,json,csv,zipfile,io,re
R=pathlib.Path(__file__).resolve().parents[1];P=R/'data/panel_2005_2024';d=json.loads((P/'dashboard_data.json').read_text('utf8'));codes={m['code'] for m in d['catalog']}
def check(obj):
 if isinstance(obj,dict):
  for key in ['indicator','code']:
   if key in obj and isinstance(obj[key],str):assert obj[key] in codes,(key,obj[key])
  for value in obj.values():check(value)
 elif isinstance(obj,list):
  for value in obj:check(value)
files=0
for p in (R/'data').rglob('*'):
 if not p.is_file():continue
 if p.suffix=='.json':check(json.loads(p.read_text('utf8')))
 elif p.suffix=='.csv':
  with p.open(encoding='utf-8-sig',newline='') as f:check(list(csv.DictReader(f)))
 else:raise AssertionError('Unexpected data warehouse artifact: '+str(p))
 files+=1
assert set(json.loads((P/'labels_fa.json').read_text('utf8')))==codes
for m in d['catalog']:
 for c in ['IRN','EGY']:
  rows=[r for r in d['panel'] if r['indicator']==m['code'] and r['country']==c];assert len(rows)==20
  if m['code'] not in d['coverage_policy']['exceptions']:assert sum(r['value'] is None for r in rows)<=5
 if m['kind']=='derived':assert set(re.findall(r'[A-Z][A-Z0-9.]+',m['formula']))<=codes
pattern=re.compile(r'(?<![A-Z0-9])(?:[A-Z]{2,}\.[A-Z0-9]+(?:\.[A-Z0-9]+)*|GGX[A-Z_]+)(?![A-Z0-9])')
def scan_workbook(content):
 with zipfile.ZipFile(io.BytesIO(content)) as z:
  for name in z.namelist():
   if name.endswith('.xml'):
    for code in pattern.findall(z.read(name).decode('utf8')):assert code in codes,code
for p in (R/'outputs/iran_egypt_2005_2024').glob('*.xlsx'):scan_workbook(p.read_bytes())
bundle=R/'outputs/iran_egypt_2005_2024/Iran_Egypt_2005_2024_Dashboard.zip'
if bundle.exists():
 with zipfile.ZipFile(bundle) as z:
  assert z.testzip() is None
  for name in z.namelist():
   if name.endswith('.xlsx'):scan_workbook(z.read(name))
   if name.startswith('data/') and name.endswith('.json'):check(json.loads(z.read(name).decode('utf8')))
print(json.dumps(dict(active_metrics=len(codes),source_metrics=d['summary']['source_metrics'],derived_metrics=d['summary']['derived_metrics'],data_files_audited=files,coverage_policy_valid=True,workbook_codes_valid=True,bundle_valid=True)))
