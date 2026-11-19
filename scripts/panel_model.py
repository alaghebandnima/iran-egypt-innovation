"""Coverage policy and reproducible source-only comparison tables."""
import csv,json,pathlib,statistics,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'app'))
from i18n import NOTES_EN,NAMES_EN
R=pathlib.Path(__file__).resolve().parents[1];P=R/'data/panel_2005_2024';YEARS=list(range(2005,2025));COUNTRIES=['IRN','EGY'];EXCEPTIONS={'GII.RANK','TX.VAL.TECH.CD','GB.XPD.RSDV.GD.ZS'}
def save(name,rows,fields=None,folder=P):
 rows=list(rows);fields=fields or list(dict.fromkeys(k for r in rows for k in r));folder.mkdir(parents=True,exist_ok=True)
 with (folder/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def build():
 d=json.loads((P/'dashboard_data.json').read_text('utf8'));ix={(x['country'],x['indicator'],x['year']):x for x in d['panel']}
 def value(c,i,y):return ix.get((c,i,y),{}).get('value')
 keep={m['code'] for m in d['catalog'] if m['code'] in EXCEPTIONS or all(sum(value(c,m['code'],y) is None for y in YEARS)<=5 for c in COUNTRIES)}
 for m in d['catalog']:
  if m['kind']=='derived' and not set(re.findall(r'[A-Z][A-Z0-9.]+',m['formula']))<=keep:keep.discard(m['code'])
 d['catalog']=[m for m in d['catalog'] if m['code'] in keep];d['panel']=[r for r in d['panel'] if r['indicator'] in keep and r['year'] in YEARS];d['core']=[i for i in d['core'] if i in keep];d['excluded']=[];d['years']=YEARS;d['coverage']=[];d['comparison']=[];d['annual']=[]
 def provider(code):return 'SWIID' if code.startswith('SWIID.') else 'WIPO' if code=='GII.RANK' else 'IMF' if code.startswith('GGX') else 'WDI'
 for row in d['panel']:row['source_file']='panel_long.csv' if next(m for m in d['catalog'] if m['code']==row['indicator'])['kind']=='derived' else provider(row['indicator'])+'_values.csv'
 for m in d['catalog']:
  i=m['code']
  for c in COUNTRIES:
   ys=[y for y in YEARS if value(c,i,y) is not None];d['coverage'].append(dict(country=c,indicator=i,n_observations=len(ys),first_year=min(ys) if ys else None,last_year=max(ys) if ys else None,coverage_pct=5*len(ys),missing_years=';'.join(str(y) for y in YEARS if y not in ys)))
  common=[y for y in YEARS if all(value(c,i,y) is not None for c in COUNTRIES)];a,b=common[0],common[-1]
  out=dict(indicator=i,name_fa=m['name_fa'],unit=m['unit_display'],kind=m['kind'],common_years=len(common),first_common_year=a,last_common_year=b,years_used=';'.join(map(str,common)))
  for c in COUNTRIES:
   v=[value(c,i,y) for y in common];out.update({c+'_first':v[0],c+'_last':v[-1],c+'_change':v[-1]-v[0],c+'_mean_common':statistics.mean(v) if i!='GII.RANK' else None,c+'_CAGR':100*((v[-1]/v[0])**(1/(b-a))-1) if a<b and v[0]>0 and v[-1]>0 and i!='GII.RANK' else None})
  d['comparison'].append(out)
  for y in YEARS:
   x,z=value('IRN',i,y),value('EGY',i,y);d['annual'].append(dict(indicator=i,year=y,IRN=x,EGY=z,difference=x-z if x is not None and z is not None else None,ratio=x/z if x is not None and z not in [None,0] and i!='GII.RANK' else None))
 d['methods']=[dict(topic=t,method=v) for t,v in [
 ('بازه','۲۰۰۵ تا ۲۰۲۴، دقیقاً بیست سال؛ نبود مقدار با صفر متفاوت است.'),
 ('پوشش','حداکثر پنج سال مفقود برای هر کشور؛ رتبهٔ جهانی نوآوری، صادرات فناوری‌پیشرفته و هزینهٔ تحقیق‌وتوسعه به دلیل اهمیت تحلیلی استثنا هستند. پوشش بر پایهٔ مقادیر منتشرشدهٔ منبع است، نه تخمین پروژه.'),
 ('رتبهٔ نوآوری','در این مجموعه، رتبه‌های ۲۰۲۰ تا ۲۰۲۴ موجودند؛ آغاز پوشش این فایل به معنی آغاز انتشار شاخص نیست. رتبه‌های ناموجود تخمین زده نمی‌شوند.'),
 ('مقایسه','خلاصهٔ دو کشور فقط روی سال‌های مشترک محاسبه می‌شود؛ میانگین رتبه محاسبه نمی‌شود.'),
 ('فرمول','شاخص محاسبه‌شده تنها از ورودی‌های نگهداری‌شده و هم‌سال ساخته می‌شود؛ فرمول در واژه‌نامه است.'),
 ('تخمین','چهار روش با پنهان‌سازی بلوک‌های معلوم و حفظ جهت شکاف مقایسه می‌شوند؛ تخمین‌ها جدا و قرمزند و مقدار اولیه جایگزین نمی‌شود.'),
 ('بدهی','بدهی ناخالص دولت عمومی از صندوق بین‌المللی پول است؛ وضعیت رسمی واقعی/برآورد هر سال در رابط داده قطعی نیست.'),
 ('رویداد','هم‌زمانی رویداد و تغییر شاخص دلیل کافی برای رابطهٔ علّی نیست.'),
 ('دستیار','پایتون گزاره‌های عددی را محاسبه می‌کند و اولاما جمع‌بندی تأییدشده را با ارجاع به رکوردها انتخاب می‌کند.')]]
 for m in d['catalog']:
  if m['code'] in NOTES_EN:m['note_en']=NOTES_EN[m['code']]
  if m['code'] in NAMES_EN:m['name_en']=NAMES_EN[m['code']]
 d['coverage_policy']=dict(max_missing_years=5,exceptions=sorted(EXCEPTIONS),basis='original values; 2005-2024')
 source_codes={m['code'] for m in d['catalog'] if m['kind']=='source'}
 d['summary']=dict(start=2005,end=2024,years=20,source_metrics=len(source_codes),derived_metrics=len(keep)-len(source_codes),metrics=len(keep),source_values_two_countries=sum(r['value'] is not None and r['country'] in COUNTRIES and r['indicator'] in source_codes for r in d['panel']),source_published_estimates=sum(r['value'] is not None and r.get('source_is_estimated',False) and r['country'] in COUNTRIES for r in d['panel']),retrieved=max(r.get('retrieved','2026-11-12') for r in d['panel']),revision='Three explicitly retained coverage exceptions; SWIID disposable-income Gini replaces World Bank Gini')
 for name,key in [('panel_long.csv','panel'),('metric_dictionary.csv','catalog'),('coverage.csv','coverage'),('period_comparison.csv','comparison'),('annual_comparison.csv','annual'),('historical_events.csv','events'),('methodology.csv','methods')]:save(name,d[key])
 for c in COUNTRIES:save(c+'_2005_2024.csv',[r for r in d['panel'] if r['country']==c])
 for name,obj in [('dashboard_data.json',d),('summary.json',d['summary'])]:(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2 if name=='summary.json' else None),encoding='utf8')
 for name in ['WDI','IMF','WIPO','SWIID']:
  rows=[r for r in d['panel'] if r['indicator'] in source_codes and provider(r['indicator'])==name];save(name+'_values.csv',rows,folder=R/'data/raw')
 (R/'data/raw/source_dictionary.json').write_text(json.dumps([m for m in d['catalog'] if m['kind']=='source'],ensure_ascii=False),encoding='utf8')
 (R/'data/indicator_catalog.json').write_text(json.dumps(d['catalog'],ensure_ascii=False),encoding='utf8')
 print(json.dumps(d['summary'],indent=2))
if __name__=='__main__':build()
