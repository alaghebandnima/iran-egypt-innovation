import sys,pathlib,json,csv,time
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'app'))
from estimation import build_estimates
from presentation import unit
P=R/'data/panel_2005_2024';d=json.loads((P/'dashboard_data.json').read_text('utf-8'));t=time.monotonic();result=build_estimates(d)
for key in ['estimates','decisions','trials','scores','unresolved','nested_audit']:
 rows=result[key]
 if not rows:(P/f'estimation_{key}.csv').unlink(missing_ok=True)
 if rows:
  with (P/f'estimation_{key}.csv').open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'analysis_with_estimates.json').write_text(json.dumps(result['analysis'],ensure_ascii=False),encoding='utf-8')
(P/'estimation_details.json').write_text(json.dumps({k:v for k,v in result.items() if k!='analysis'},ensure_ascii=False),encoding='utf-8')
(P/'labels_fa.json').write_text(json.dumps({m['code']:unit(m) for m in d['catalog']},ensure_ascii=False),encoding='utf-8')
print(json.dumps(result['analysis']['estimation_summary'],indent=2));print('Build seconds',round(time.monotonic()-t,2))
