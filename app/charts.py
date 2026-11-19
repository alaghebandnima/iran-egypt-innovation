import plotly.graph_objects as go
from engine import series,NAMES
from i18n import L,country,method_name,language
def trend_figure(data,code,start,end,tokens,unit,world=False,events=True):
 fig=go.Figure();colors={'IRN':'#68c7ef','EGY':'#e8b264','WLD':'#9eacc0'}
 for co in ['IRN','EGY']+(['WLD'] if world else []):
  rows=series(data,code,co,start,end);ys=[r['year'] for r in rows]
  source_label=L('برآورد سوئید','SWIID estimate') if code=='SWIID.GINI.DISP' else L('مقدار منبع','source value')
  observed=[r.get('original_value',r['value']) if not r.get('is_estimated') else None for r in rows]
  if not any(v is not None for v in observed) and not any(r.get('is_estimated') for r in rows):continue
  symbol='circle' if co=='IRN' else 'diamond' if co=='EGY' else 'square'
  fig.add_trace(go.Scatter(x=ys,y=observed,name=country(co)+L('؛ ','; ')+source_label,mode='lines+markers',connectgaps=False,line=dict(color=colors[co],width=2.5),marker=dict(size=6,symbol=symbol),hovertemplate='%{x}<br>%{y:,.3f}<br>'+source_label+'<extra>%{fullData.name}</extra>'))
  predicted=[r['value'] if r.get('is_estimated') else None for r in rows]
  if any(v is not None for v in predicted):
   bx=[];by=[]
   for a,b in zip(rows,rows[1:]):
    if (a.get('is_estimated') or b.get('is_estimated')) and a['value'] is not None and b['value'] is not None:bx.extend([a['year'],b['year'],None]);by.extend([a['value'],b['value'],None])
   fig.add_trace(go.Scatter(x=bx,y=by,mode='lines',line=dict(color=tokens['red'],width=1.8,dash='dot'),showlegend=False,hoverinfo='skip',name=L('مسیر تخمینی','Estimated path')))
   fig.add_trace(go.Scatter(x=ys,y=predicted,name=country(co)+L('؛ تخمین پروژه','; project estimate'),mode='markers',marker=dict(color=tokens['red'],size=9,symbol=symbol,line=dict(width=1,color=tokens['panel'])),customdata=[method_name(r.get('estimation_method','')) for r in rows],hovertemplate='%{x}<br>%{y:,.3f}<br>'+L('تخمین پروژه: ','Project estimate: ')+'%{customdata}<extra>%{fullData.name}</extra>'))
 if events:
  for year in sorted(set(e['year'] for e in data['events'] if start<=e['year']<=end)):fig.add_vline(x=year,line_dash='dot',line_color=tokens['muted'],line_width=1,opacity=.38)
 fig.update_layout(template='plotly_dark' if tokens.get('mode')=='dark' else 'plotly_white',height=465,margin=dict(l=20,r=20,t=22,b=35),font=dict(family='Vazirmatn',size=11,color=tokens['text']),legend=dict(orientation='h',y=1.13,x=1,xanchor='right',font=dict(size=11)),xaxis=dict(title=L('سال','Year'),range=[start-.35,end+.35],tickmode='linear',dtick=2 if end-start>12 else 1,tickformat='d',gridcolor=tokens['grid'],zerolinecolor=tokens['line']),yaxis=dict(title=unit,gridcolor=tokens['grid'],zerolinecolor=tokens['line']),paper_bgcolor=tokens['panel'],plot_bgcolor=tokens['panel'],hovermode='x unified',hoverlabel=dict(bgcolor=tokens['panel2'],font=dict(color=tokens['text'],family='Vazirmatn')))
 if code=='GII.RANK':fig.update_yaxes(autorange='reversed')
 return fig
