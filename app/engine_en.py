"""English evidence wording around the shared numerical engine."""
import re
from i18n import country,metric_name,metric_note
from presentation import unit

def answer(data,question,selected,start,end):
 from engine import resolve_metric,normalize,index,number,period_summary,series
 code=resolve_metric(data,question,selected)
 def empty(text):return dict(code=code,answer=text,facts=[],evidence=[],needs_model=False)
 if code is None:return empty('The requested indicator was not recognized in the current dataset. Select an indicator or use its exact name.')
 m=next(x for x in data['catalog'] if x['code']==code);u=unit(m)
 requested=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',normalize(question))]
 if any(y<2005 or y>2024 for y in requested):return empty('This project covers 2005–2024 only. No value is reported outside that period.')
 if requested:start,end=min([start]+requested),max([end]+requested)
 facts=[];evidence=[];ix=index(data)
 def add(c,y):
  x=ix.get((c,code,y),{});v=x.get('value')
  e=dict(id=f'{c}|{code}|{y}',country=c,indicator=code,year=y,value=v,source_url=x.get('source_url',m['source_url']),status=x.get('status','missing'),is_estimated=x.get('is_estimated',False),source_is_estimated=x.get('source_is_estimated',False),original_value=x.get('original_value',v))
  evidence.append(e);return e
 if len(set(requested))==1:
  y=requested[0]
  for c in ['IRN','EGY']:
   e=add(c,y);v=e['value'];text=f'{country(c)} in {y}: {number(v)} {u}.' if v is not None else f'No source value is available for {country(c)} in {y}.'
   if e['is_estimated']:text+=' This is a project estimate; the published source value is unavailable.'
   elif e['source_is_estimated']:text+=' This is a published SWIID estimate, not an independent survey observation.'
   facts.append(dict(id=e['id'],text=text))
  a,b=(e['value'] for e in evidence)
  if a is not None and b is not None:
   relation='higher than' if a>b else 'lower than' if a<b else 'equal to'
   facts.append(dict(id=f'compare|{code}|{y}',text=f'In {y}, Iran’s value is {relation} Egypt’s. Iran minus Egypt is {number(a-b)} {u}. A higher value does not necessarily indicate better performance.'))
 else:
  if len(requested)>=2:start,end=min(requested),max(requested)
  s=period_summary(data,code,start,end);common=s['common_years']
  facts.append(dict(id=f'coverage|{code}|{start}|{end}',text=f'The period is {start}–{end}, with {len(common)} common years out of {end-start+1}.'))
  if common:
   a,b=common[0],common[-1]
   for c in ['IRN','EGY']:
    z=s['country'][c];text=f'{country(c)}: {number(z["first"])} in {a}, then {number(z["last"])} in {b}; change: {number(z["change"])} {u}.'
    if code!='GII.RANK':text+=f' Common-year mean: {number(z["mean_common"])}.'
    if any(r.get('is_estimated') for r in series(data,code,c,start,end) if r['year'] in common):text+=' This summary includes project estimates.'
    facts.append(dict(id=f'period|{c}|{code}|{a}|{b}',text=text))
    for y in sorted({a,b}):add(c,y)
  else:facts.append(dict(id='no_common_year',text='No common year is available for comparison in the selected period.'))
 facts.append(dict(id='method|'+code,text=metric_note(m)))
 if code=='GII.RANK':facts.append(dict(id='ordinal_rank',text='A lower rank is better. Rank changes do not measure equal-sized changes in innovation capacity.'))
 return dict(code=code,name_fa=metric_name(m),answer='\n\n'.join(f['text'] for f in facts),facts=facts,evidence=evidence,needs_model=bool(evidence),question=question,unit=u)
