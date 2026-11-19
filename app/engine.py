"""Deterministic calculations, retrospective validation and local model adapter."""
from __future__ import annotations
import os,json,pathlib,statistics,math,re,urllib.request,urllib.error,socket,unicodedata
from presentation import unit,fa
from i18n import L,language,NAMES_EN
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data/panel_2005_2024/dashboard_data.json'
NAMES={'IRN':'ایران','EGY':'مصر','WLD':'جهان'}
def load_data(path=DATA):
 return json.loads(pathlib.Path(path).read_text('utf-8'))
def index(data):return {(x['country'],x['indicator'],x['year']):x for x in data['panel']}
def number(v):
 if v is None:return L('موجود نیست','Unavailable')
 return f'{v:,.3f}'.rstrip('0').rstrip('.')
def normalize(s):return str(s).translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩يك','01234567890123456789یک'))
def series(data,code,country,start=2005,end=2024):
 ix=index(data)
 return [ix.get((country,code,y),dict(country=country,indicator=code,year=y,value=None,status='missing')) for y in range(start,end+1)]
def period_summary(data,code,start=2005,end=2024):
 ix=index(data);common=[y for y in range(start,end+1) if all(ix.get((c,code,y),{}).get('value') is not None for c in ['IRN','EGY'])]
 out=dict(start=start,end=end,common_years=common,common_count=len(common),country={})
 for c in ['IRN','EGY']:
  obs=[x for x in series(data,code,c,start,end) if x['value'] is not None]
  vals=[ix[(c,code,y)]['value'] for y in common]
  first,last=(vals[0],vals[-1]) if vals else (None,None)
  change=last-first if vals else None
  out['country'][c]=dict(observed=len(obs),missing=end-start+1-len(obs),coverage=len(obs)/(end-start+1)*100,first=first,last=last,change=change,mean_common=statistics.mean(vals) if vals and code!='GII.RANK' else None,cagr=100*((last/first)**(1/(common[-1]-common[0]))-1) if len(common)>1 and first>0 and last>0 and code!='GII.RANK' else None)
 return out
def annual_comparison(data,code,start=2005,end=2024):
 ix=index(data);rows=[]
 for y in range(start,end+1):
  a=ix.get(('IRN',code,y),{}).get('value');b=ix.get(('EGY',code,y),{}).get('value')
  rows.append(dict(year=y,IRN=a,EGY=b,difference=a-b if a is not None and b is not None else None,ratio=a/b if a is not None and b not in [None,0] and code!='GII.RANK' else None))
 return rows
ALIASES={'IP.PAT.RESD': ['پتنت', 'اختراع', 'patent'], 'IP.JRN.ARTC.SC': ['مقاله', 'مقالات', 'journal', 'article'], 'GGXWDG_NGDP': ['بدهی', 'debt'], 'NY.GDP.PCAP.PP.CD': ['سرانه ppp', 'gdp ppp', 'قدرت خرید'], 'IT.NET.USER.ZS': ['اینترنت', 'internet'], 'GII.RANK': ['رتبه نوآوری', 'gii']}
ALIASES.update({'SWIID.GINI.DISP':['جینی','ضریب جینی','gini','swiid'],'TX.VAL.TECH.CD':['صادرات فناوری','صادرات فناوری‌پیشرفته','high-tech','high technology exports','high-technology exports'],'GB.XPD.RSDV.GD.ZS':['تحقیق و توسعه','تحقیق‌وتوسعه','هزینه پژوهش','r&d','research and development']})
def resolve_metric(data,question,selected):
 q=normalize(question).lower();available={x['code'] for x in data['catalog']}
 explicit=[code for code in available if code.lower() in q]
 if explicit:return sorted(explicit,key=len,reverse=True)[0]
 names=[(len(n),m['code']) for m in data['catalog'] for n in [normalize(m['name_fa']).lower(),normalize(fa(m['name_fa'])).lower(),normalize(NAMES_EN.get(m['code'],m.get('name_en',m['code']))).lower()] if n in q]
 if names:return max(names)[1]
 hits=[(len(a),code) for code,aliases in ALIASES.items() if code in available for a in aliases if a.lower() in q]
 if hits:return max(hits)[1]
 if selected not in available or re.search(r'\b[A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)+\b',question):return None
 generic=set('این شاخص انتخاب شده در سال سالهای سال‌های بازه ایران مصر و برای از تا مقدار داده موجود است نیست چقدر چقدره بوده بود بیشتر کمتر تفاوت اختلاف مقایسه روند تغییر رشد میانگین جمع بندی جمع‌بندی کلی محدودیت محدودیتی دارد چه چگونه را عدد بنویس توضیح بده بررسی کن'.split())
 generic.update('محدودیتش چیه هست یعنی مفهومش تفسیرش دلیلش علتش محاسبه کاربردی داره به زبان ساده اینطور شده توضیحش'.split())
 generic.update('it mean means simply explain interpretation limitations'.split())
 generic.update('چند چرا علت دلیل افت کاهش افزایش داشته کرده بیشترین کمترین بالاترین کیفیت معنا مفهوم بهتر بدتر توضیحی محدودیت‌ها کاربرد تفسیر میشود می‌شود'.split())
 generic.update('why cause caused highest lowest maximum minimum peak meaning definition useful interpretation quality estimates estimated'.split())
 generic.update('this indicator selected in year years period iran egypt and for from to value values data available unavailable what are is were was how much many higher lower difference compare comparison trend change growth mean average summary overall limitations does have explain please the of a an show tell me between at'.split())
 words=re.findall(r'[\w‌]+',q)
 return selected if any(a in q for a in ['این شاخص','این نمودار','این روند','این داده','شاخص انتخاب','this indicator','this chart','these data','this trend','selected indicator']) or all(w.isdigit() or w in generic for w in words) else None
def grounded_answer(data,question,selected,start=2005,end=2024):
 if language()=='en':
  from engine_en import answer
  return add_assistant_context(data,answer(data,question,selected,start,end),start,end)
 code=resolve_metric(data,question,selected)
 if code is None:return dict(code=None,answer='شاخص درخواست‌شده در مجموعهٔ فعلی شناسایی نشد. یکی از شاخص‌های فهرست را انتخاب کنید یا نام دقیق آن را بنویسید.',facts=[],evidence=[],needs_model=False)
 meta=dict(next(x for x in data['catalog'] if x['code']==code));meta['unit_display']=unit(meta)
 requested=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',normalize(question))]
 if any(y<2005 or y>2024 for y in requested):
  return dict(code=code,answer='این پروژه فقط بازهٔ ۲۰۰۵ تا ۲۰۲۴ را پوشش می‌دهد. برای سال خارج از این بازه عددی گزارش نمی‌کنم.',facts=[],evidence=[],needs_model=False)
 if requested and any(y<start or y>end for y in requested):start,end=min([start]+requested),max([end]+requested)
 ix=index(data);facts=[];evidence=[]
 if len(set(requested))==1:
  y=requested[0]
  for c in ['IRN','EGY']:
   row=ix.get((c,code,y),{});v=row.get('value');eid=f'{c}|{code}|{y}'
   facts.append(dict(id=eid,text=f'{NAMES[c]} در {y}: {number(v)} {meta["unit_display"]}' if v is not None else f'برای {NAMES[c]} در {y} داده در منبع موجود نیست.'))
   evidence.append(dict(id=eid,country=c,indicator=code,year=y,value=v,source_url=row.get('source_url',meta['source_url']),status=row.get('status','missing'),is_estimated=row.get('is_estimated',False),source_is_estimated=row.get('source_is_estimated',False),original_value=row.get('original_value',v)))
   if row.get('is_estimated'):facts[-1]['text']+='؛ تخمینی است و مقدار اصلی در دسترس نیست.'
   elif row.get('source_is_estimated'):facts[-1]['text']+='؛ برآورد منتشرشدهٔ سوئید است، نه مشاهدهٔ پیمایشی مستقل.'
  iv,ev=evidence[0]['value'],evidence[1]['value']
  if iv is not None and ev is not None:
   relation='بیشتر از' if iv>ev else 'کمتر از' if iv<ev else 'برابر با'
   facts.append(dict(id=f'compare|{code}|{y}',text=f'در {y} مقدار این شاخص در ایران {relation} مصر است؛ اختلاف ایران منهای مصر {number(iv-ev)} {meta["unit_display"]} است. بیشتر بودن مقدار به‌تنهایی به معنی عملکرد بهتر نیست.'))
 else:
  if len(requested)>=2:start,end=min(requested),max(requested)
  s=period_summary(data,code,start,end);common=s['common_years']
  facts.append(dict(id=f'coverage|{code}|{start}|{end}',text=f'بازهٔ بررسی {start} تا {end} است؛ {s["common_count"]} سال دارای دادهٔ مشترک از {end-start+1} سال دارد.'))
  if common:
   a,b=common[0],common[-1]
   for c in ['IRN','EGY']:
    v=s['country'][c]
    text=f'{NAMES[c]}: مقدار {number(v["first"])} در {a} به {number(v["last"])} در {b} رسید؛ تغییر {number(v["change"])} {meta["unit_display"]}.'
    if code!='GII.RANK':text+=f' میانگین روی سال‌های مشترک {number(v["mean_common"])} است.'
    if any(r.get('is_estimated') for r in series(data,code,c,start,end) if r['year'] in common):text+=' این خلاصه شامل دادهٔ تخمینی است؛ تخمین مشاهدهٔ اصلی نیست.'
    facts.append(dict(id=f'period|{c}|{code}|{a}|{b}',text=text))
    for y in sorted({a,b}):
     x=ix[(c,code,y)];evidence.append(dict(id=f'{c}|{code}|{y}',country=c,indicator=code,year=y,value=x['value'],source_url=x['source_url'],status=x['status'],is_estimated=x.get('is_estimated',False),source_is_estimated=x.get('source_is_estimated',False),original_value=x.get('original_value',x['value'])))
  else:facts.append(dict(id='no_common_year',text='در محدودهٔ انتخاب‌شده سال مشترک برای مقایسه وجود ندارد.'))
 facts.append(dict(id='method|'+code,text=meta['note_fa']))
 if code=='GII.RANK':facts.append(dict(id='ordinal_rank',text='عدد رتبه هرچه کمتر باشد جایگاه بهتر است؛ تغییر رتبه به معنی تغییر هم‌اندازه در ظرفیت نوآوری نیست.'))
 answer='\n\n'.join(f['text'] for f in facts)
 return add_assistant_context(data,dict(code=code,name_fa=meta['name_fa'],answer=answer,facts=facts,evidence=evidence,needs_model=bool(evidence),question=question,unit=meta['unit_display']),start,end)
def add_assistant_context(data,result,start,end):
 if not result.get('needs_model'):return result
 facts=[]
 requested=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',normalize(result.get('question','')))]
 if requested:start,end=min(requested),max(requested)
 for code,label in [('IRN',L('ایران','Iran')),('EGY',L('مصر','Egypt'))]:
  rows=series(data,result['code'],code,start,end)
  published=sum(r['value'] is not None and not r.get('is_estimated',False) for r in rows)
  estimated=sum(bool(r.get('is_estimated',False)) for r in rows)
  missing=sum(r['value'] is None for r in rows)
  facts.append(dict(id='availability|'+code,text=L(f'{label}: در بازهٔ {start} تا {end}، {published} سال با مقدار منبع و {estimated} سال با تخمین پروژه و {missing} سال فاقد مقدار است.',f'{label}: {published} years with source values and {estimated} years with project estimates and {missing} unavailable years in {start}–{end}.')))
  q=normalize(result.get('question','')).lower();valid=[r for r in rows if r['value'] is not None]
  if valid:
   for kind,terms,operation in [('maximum',['بیشترین','بالاترین','اوج','maximum','highest','peak'],max),('minimum',['کمترین','پایین‌ترین','minimum','lowest'],min)]:
    if any(t in q for t in terms):
     value=operation(r['value'] for r in valid);years=', '.join(str(r['year']) for r in valid if r['value']==value)
     facts.append(dict(id=kind+'|'+code,text=L(f'{label}: '+('بیشترین' if kind=='maximum' else 'کمترین')+f' مقدار {number(value)} {result.get("unit","")} در سال‌های {years} است.',f'{label}: {kind} {number(value)} {result.get("unit","")} in {years}.')))

 facts.append(dict(id='definition',text=L('شاخص: '+result.get('name_fa',result['code'])+'؛ واحد: '+result.get('unit',''), 'Indicator: '+result.get('name_fa',result['code'])+'; unit: '+result.get('unit',''))))
 result['context_facts']=facts
 result['qualitative_facts']=qualitative_context(data,result,start,end)
 return result

def qualitative_context(data,result,start,end):
 def clean(text):
  text=unicodedata.normalize('NFKC',text).replace('CO2',L('دی اکسید کربن','carbon dioxide'))
  return re.sub(r'\s+',' ',re.sub(r'\S*\d\S*','',text)).strip()
 note=next((f['text'] for f in result['facts'] if f['id'].startswith('method|')),'')
 if result['code']=='IP.PAT.RESD':note=L('این شاخص فقط تعداد درخواست‌های ثبت اختراع مقیمان را می‌شمارد؛ کیفیت اختراع و تعداد پتنت‌های اعطاشده را اندازه نمی‌گیرد.','This indicator measures the number of resident patent applications, not the quality of inventions or the number of patents granted.')
 facts=[dict(id='method|'+result['code'],text=clean(note)),dict(id='definition',text=L('نام شاخص: ','Indicator: ')+clean(result.get('name_fa',result['code'])))]
 pairs={}
 for co,label in [('IRN',L('ایران','Iran')),('EGY',L('مصر','Egypt'))]:
  rows=series(data,result['code'],co,start,end);valid=[r for r in rows if r['value'] is not None];pairs[co]={r['year']:r for r in valid}
  estimated=any(r.get('is_estimated') for r in valid);missing=any(r['value'] is None for r in rows)
  if missing:coverage=L('پوشش این بازه ناقص است و برای بخشی از سال‌ها مقدار وجود ندارد.','Coverage of the selected period is incomplete; some values are unavailable.')
  elif estimated:coverage=L('مجموعهٔ تکمیل‌شده برای بازه مقدار دارد، اما پوشش منبع کامل نیست؛ بخشی از مقادیر تخمین پروژه‌اند و مشاهدهٔ منتشرشده نیستند.','The completed dataset has values across the selected period, but published-source coverage is incomplete; some values are project estimates rather than source observations.')
  else:coverage=L('برای سراسر بازهٔ انتخاب‌شده مقادیر منتشرشدهٔ منبع موجود است؛ در این بازه تخمین پروژه به کار نرفته است.','Published source values cover the selected period; this period uses no project estimates.')
  facts.append(dict(id='availability|'+co,text=label+': '+coverage))
  if any(r.get('source_is_estimated') for r in valid):facts.append(dict(id='source_estimate|'+co,text=label+': '+L('بخشی از مقادیر منتشرشده، برآورد خود منبع‌اند و پیمایش مستقل سالانه نیستند.','Some published values are estimates from the source, not independent annual survey observations.')))
  if len(valid)>1:
   delta=valid[-1]['value']-valid[0]['value'];direction=L('افزایش','increased') if delta>0 else L('کاهش','decreased') if delta<0 else L('بدون تغییر','unchanged')
   facts.append(dict(id='direction|'+co,text=L(f'{label}: مقایسهٔ ابتدا و انتهای بازه {direction} نشان می‌دهد؛ این نتیجه دربارهٔ تک‌تک تغییرات سالانه نیست.',f'{label}: the value {direction} between the first and last available year. This does not describe every annual change.')))
   diffs=[b['value']-a['value'] for a,b in zip(valid,valid[1:]) if b['year']==a['year']+1]
   if any(x>0 for x in diffs) and any(x<0 for x in diffs):facts.append(dict(id='variation|'+co,text=label+': '+L('در داخل بازه، هم افزایش و هم کاهش سالانه دیده می‌شود؛ افزایش کلی به معنی نبود افت مقطعی نیست.','Both annual increases and annual decreases occur within the period; an overall increase does not rule out a temporary decline.')))
 common=sorted(set(pairs['IRN'])&set(pairs['EGY']))
 if common:
  y=common[-1];a=pairs['IRN'][y]['value'];b=pairs['EGY'][y]['value']
  relation=L('بیشتر از','higher than') if a>b else L('کمتر از','lower than') if a<b else L('برابر با','equal to')
  facts.append(dict(id='compare',text=L(f'در آخرین سال مشترکِ بازهٔ انتخاب‌شده، مقدار ایران {relation} مصر است. بزرگ‌تر بودن مقدار به تنهایی به معنای عملکرد بهتر نیست.',f'In the latest common year of the selected period, Iran is {relation} Egypt. A higher value does not by itself imply better performance.')))
 return facts

def _request(path,payload=None,timeout=5):
 req=urllib.request.Request(os.environ.get('INNOVATION_OLLAMA_URL','http://127.0.0.1:11434')+path,data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def models():return [x['name'] for x in _request('/api/tags').get('models',[])]
def validate_model_output(output,grounded):
 if not isinstance(output,dict):raise ValueError('پاسخ مدل ساختار معتبر ندارد.')
 text=output.get('explanation_fa');ids=output.get('evidence_ids')
 if not isinstance(text,str) or not text.strip() or len(text)>4000:raise ValueError('متن پاسخ مدل معتبر نیست.')
 valid={x['id'] for x in grounded['evidence']}
 if not isinstance(ids,list) or not ids or not all(isinstance(i,str) and i in valid for i in ids):raise ValueError('ارجاع مدل با داده‌های انتخاب‌شده سازگار نیست.')
 # Never publish newly invented numeric claims. Punctuation/locale differences normalized.
 def tokens(s):return set(re.findall(r'\d+(?:\.\d+)?',normalize(s).replace(',','').replace('٬','').replace('٫','.')))
 allowed=tokens(json.dumps(dict(facts=grounded['facts'],evidence=grounded['evidence']),ensure_ascii=False))
 # Display rounding is allowed only at representations explicitly supplied to the model.
 if not tokens(text)<=allowed:raise ValueError('پاسخ مدل عددی خارج از شواهد دارد؛ توضیح قطعی داده‌ها نمایش داده می‌شود.')
 return dict(explanation_fa=text,evidence_ids=ids)
def explain_with_ollama(grounded,model='qwen3:4b-instruct',timeout=180):
 from assistant import explain
 return explain(grounded,model,timeout)
