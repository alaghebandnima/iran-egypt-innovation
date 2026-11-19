"""Short, numerically grounded online answers with a bounded shared cache."""
import json,hashlib,sqlite3,os,pathlib,re,time,contextlib
import engine
from i18n import L,language,country
from assistant import question_intent

def sentences(text,n=2):
 parts=re.split(r'(?<=[.!?؟])\s+',text.strip())
 return ' '.join(parts[:n]).strip()

def prepare(data,question,code,start,end):
 g=engine.grounded_answer(data,question,code,start,end)
 g['compact_numeric']='';g['compact_estimated']=False
 if not g['needs_model']:
  g['fallback_short']=sentences(g['answer']);return g
 q=engine.normalize(question).lower();intent=question_intent(q)
 years=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',q)]
 if years:start,end=min(years),max(years)
 cos=[co for co,names in [('IRN',['ایران','iran']),('EGY',['مصر','egypt'])] if any(n in q for n in names)] or ['IRN','EGY']
 rows={co:engine.series(data,g['code'],co,start,end) for co in ['IRN','EGY']}
 def value(row):
  if row.get('is_estimated'):g['compact_estimated']=True
  label=L(' (تخمین پروژه)',' (project estimate)') if row.get('is_estimated') else L(' (برآورد منبع)',' (source estimate)') if row.get('source_is_estimated') else ''
  return engine.number(row['value'])+label
 chunks=[];u=g.get('unit','')
 if intent=='coverage':
  for co in cos:
   p=sum(x['value'] is not None and not x.get('is_estimated') for x in rows[co]);e=sum(bool(x.get('is_estimated')) for x in rows[co]);m=sum(x['value'] is None for x in rows[co])
   chunks.append(L(f'{country(co)}: {p} سال دادهٔ منبع، {e} سال تخمین پروژه و {m} سال فاقد مقدار',f'{country(co)}: {p} source years, {e} project-estimated years and {m} unavailable years'))
 elif intent=='comparison' or (intent=='estimation' and any(t in q for t in ['چقدر','مقدار','value','how much'])):
  extrema=next(((operation,label) for operation,label,terms in [(max,L('بیشترین','maximum'),['بیشترین','بالاترین','اوج','maximum','highest','peak']),(min,L('کمترین','minimum'),['کمترین','پایین‌ترین','minimum','lowest'])] if any(t in q for t in terms)),None)
  if extrema:
   operation,label=extrema
   for co in cos:
    valid=[x for x in rows[co] if x['value'] is not None]
    if valid:
     v=operation(x['value'] for x in valid);matches=[x for x in valid if x['value']==v];r=next((x for x in matches if x.get('is_estimated')),matches[0]);ys='، '.join(str(x['year']) for x in matches)
     chunks.append(L(f'{country(co)}: {label} مقدار {value(r)} {u} در {ys}',f'{country(co)}: {label} {value(r)} {u} in {ys}'))
  elif any(t in q for t in ['میانگین','average','mean']) and g['code']!='GII.RANK':
   s=engine.period_summary(data,g['code'],start,end)
   for co in cos:
    v=s['country'][co]['mean_common'];estimated=any(r.get('is_estimated') for r in rows[co] if r['year'] in s['common_years']);g['compact_estimated']|=estimated
    mark=L(' (شامل تخمین پروژه)',' (includes project estimates)') if estimated else ''
    chunks.append(L(f'میانگین {country(co)} در سال‌های مشترک {start} تا {end}: {engine.number(v)} {u}{mark}',f'{country(co)} common-year mean in {start}–{end}: {engine.number(v)} {u}{mark}'))
  elif start==end:
   for co in cos:chunks.append(L(f'{country(co)} در {start}: {value(rows[co][0])} {u}',f'{country(co)} in {start}: {value(rows[co][0])} {u}'))
   if len(cos)==2 and all(rows[co][0]['value'] is not None for co in cos) and any(t in q for t in ['اختلاف','تفاوت','difference']):chunks.append(L('اختلاف ایران منهای مصر: ','Iran minus Egypt: ')+engine.number(rows['IRN'][0]['value']-rows['EGY'][0]['value'])+' '+u)
  else:
   common=set(x['year'] for x in rows['IRN'] if x['value'] is not None)&set(x['year'] for x in rows['EGY'] if x['value'] is not None)
   for co in cos:
    valid=[x for x in rows[co] if x['year'] in common]
    if valid:
     a,b=valid[0],valid[-1];estimated=any(x.get('is_estimated') for x in valid);g['compact_estimated']|=estimated
     mark=L(' (شامل تخمین پروژه)',' (includes project estimates)') if estimated else ''
     chunks.append(L(f'{country(co)}: از {value(a)} در {a["year"]} به {value(b)} {u} در {b["year"]}{mark}',f'{country(co)}: from {value(a)} in {a["year"]} to {value(b)} {u} in {b["year"]}{mark}'))
 if chunks:g['compact_numeric']='؛ '.join(chunks)+'.'
 note=next((f['text'] for f in g['facts'] if f['id'].startswith('method|')),'')
 g['fallback_short']=g['compact_numeric'] or sentences(note or g['answer'])
 if intent=='causality':g['fallback_short']=sentences(g['fallback_short'],1)+' '+L('این داده‌ها به‌تنهایی علت تغییر را ثابت نمی‌کنند.','These data alone cannot establish a cause.')
 return g

def short_answer(g,analysis):
 prefix=g.get('compact_numeric','');intent=question_intent(g.get('question',''))
 if intent=='causality':
  parts=re.split(r'(?<=[.!?؟])\s+',analysis.strip())
  terms=['افزایش','کاهش','نوسان','سالانه','روند','بازه','increase','decline','decrease','fluctuat','trend','period']
  relevant=next((part for part in parts if any(t in part.lower() for t in terms)),parts[0])
  return relevant+' '+L('این داده‌ها به‌تنهایی علت تغییر را ثابت نمی‌کنند.','These data alone cannot establish a cause.')
 return (prefix+' '+sentences(analysis,1 if prefix else 2)).strip()

def cache_key(g):return hashlib.sha256(json.dumps({'version':1,'language':language(),'grounded':g},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
@contextlib.contextmanager
def connection():
 default=pathlib.Path(__file__).resolve().parents[1]/'outputs/iran_egypt_2005_2024/assistant-cache.sqlite3'
 p=pathlib.Path(os.environ.get('INNOVATION_ASSISTANT_CACHE',str(default)))
 p.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(p,timeout=5)
 try:
  with c:
   c.execute('CREATE TABLE IF NOT EXISTS answers (key TEXT PRIMARY KEY, answer TEXT NOT NULL, created REAL NOT NULL)')
   yield c
 finally:c.close()

def cached(g):
 with connection() as c:r=c.execute('SELECT answer FROM answers WHERE key=?',(cache_key(g),)).fetchone()
 return json.loads(r[0]) if r else None

def answer(g):
 hit=cached(g)
 if hit:return dict(hit,short_answer=short_answer(g,hit['generated_analysis']),cache_hit=True)
 result=engine.explain_with_ollama(g);result['short_answer']=short_answer(g,result['generated_analysis']);result['cache_hit']=False
 with connection() as c:
  c.execute('INSERT OR REPLACE INTO answers VALUES (?,?,?)',(cache_key(g),json.dumps(result,ensure_ascii=False),time.time()))
  c.execute('DELETE FROM answers WHERE key NOT IN (SELECT key FROM answers ORDER BY created DESC LIMIT 64)')
 return result
