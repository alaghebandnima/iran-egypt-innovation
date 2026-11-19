"""Missing-value estimates with pattern-matched, leakage-free artificial masks.
No observed value is ever passed as a target's training value.
"""
from __future__ import annotations
import math,statistics,copy,re
import numpy as np

METHODS=['weighted','local_trend','trend_curve','state_space']
METHOD_NAMES={'weighted':'میانگین‌گیری وزنی','local_trend':'روند محلیِ تعدیل‌شده','trend_curve':'منحنی روند','state_space':'وضعیت پنهان؛ فیلتر و هموارساز کالمن','derived':'محاسبه از ورودی تخمینی'}
KINDS={'internal':'شکاف میان‌سری','leading':'پیش از نخستین مشاهده','trailing':'پس از آخرین مشاهده'}
BOUNDED={'SL.TLF.CACT.FE.ZS', 'SL.UEM.NEET.ZS', 'SH.XPD.CHEX.GD.ZS', 'EG.FEC.RNEW.ZS', 'EG.ELC.LOSS.ZS', 'IT.NET.USER.ZS', 'EG.ELC.ACCS.ZS', 'TX.MNF.TECH.ZS.UN', 'NV.SRV.TOTL.ZS', 'SL.UEM.1524.ZS', 'SL.UEM.TOTL.ZS', 'NV.IND.MANF.ZS', 'SP.URB.TOTL.IN.ZS', 'SL.EMP.TOTL.SP.ZS', 'SP.POP.1564.TO.ZS', 'SL.TLF.CACT.ZS', 'EG.ELC.RNEW.ZS'}
BOUNDED.update({'SWIID.GINI.DISP','GB.XPD.RSDV.GD.ZS'})
SIGNED={'GGXCNL_NGDP', 'BX.KLT.DINV.WD.GD.ZS', 'FP.CPI.TOTL.ZG', 'NY.GDP.MKTP.KD.ZG', 'LF_GENDER_GAP', 'NY.GDP.PCAP.KD.ZG'}
def constrain(value,code):
 if not math.isfinite(float(value)):raise ValueError('Nonfinite prediction')
 if code in BOUNDED:return max(0.,min(100.,float(value)))
 if code not in SIGNED:return max(0.,float(value))
 return float(value)
def _scale(v):return max(float(np.median(np.abs(list(v.values())))),float(np.max(np.abs(list(v.values()))))*1e-6,1e-9)
def _state_space(values,targets):
 """Local linear trend: x_t=F x_(t-1)+w, y_t=[1,0]x_t+v; RTS smoother."""
 scale=_scale(values);obs={y:v/scale for y,v in values.items()};ys=sorted(obs)
 diffs=np.array([(obs[b]-obs[a])/(b-a) for a,b in zip(ys,ys[1:])]);drift=float(np.median(diffs)) if len(diffs) else 0.
 spread=max(float(np.median(np.abs(diffs-np.median(diffs))))*1.4826 if len(diffs) else 0.,.015)
 q=spread**2;Q=np.diag([q*.25,q*.02]);R=max(q*.15,1e-5)
 F=np.array([[1.,1.],[0.,1.]]);H=np.array([1.,0.]);I=np.eye(2)
 lo=min(min(targets),ys[0]);hi=max(max(targets),ys[-1]);years=list(range(lo,hi+1))
 state=np.array([obs[ys[0]]+drift*(lo-ys[0]),drift]);P=np.diag([1e4,1e2]);filtered=[];predicted=[];cov=[];pcov=[]
 for y in years:
  if y!=lo:state=F@state;P=F@P@F.T+Q
  predicted.append(state.copy());pcov.append(P.copy())
  if y in obs:
   gain=(P@H)/(H@P@H+R);state=state+gain*(obs[y]-H@state);P=(I-np.outer(gain,H))@P
   P=(P+P.T)/2
  filtered.append(state.copy());cov.append(P.copy())
 smooth=[x.copy() for x in filtered]
 for k in range(len(years)-2,-1,-1):
  C=cov[k]@F.T@np.linalg.pinv(pcov[k+1]);smooth[k]=filtered[k]+C@(smooth[k+1]-predicted[k+1])
 return {y:float(smooth[y-lo][0]*scale) for y in targets}
def fit_predict(values,targets,method,code):
 values={int(y):float(v) for y,v in values.items() if v is not None};targets=list(targets)
 if len(values)<3:raise ValueError('At least three training values required')
 if not targets:return {}
 if method=='state_space':result=_state_space(values,targets)
 elif method=='weighted':
  result={};ys=sorted(values)
  for t in targets:
   left=[y for y in ys if y<t];right=[y for y in ys if y>t]
   if left and right:
    a,b=left[-1],right[0];result[t]=((b-t)*values[a]+(t-a)*values[b])/(b-a)
   else:
    near=sorted(ys,key=lambda y:abs(y-t))[:3];weights=[1/max(1,abs(y-t)) for y in near];result[t]=sum(w*values[y] for w,y in zip(weights,near))/sum(weights)
 elif method=='local_trend':
  result={};scale=_scale(values)
  for t in targets:
   ys=sorted(values,key=lambda y:abs(y-t))[:5];x=np.array([(y-t)/5 for y in ys]);y=np.array([values[a]/scale for a in ys]);w=1/(1+np.abs(x)*5)
   X=np.column_stack([np.ones(len(x)),x]);coef=np.linalg.solve(X.T@(w[:,None]*X)+np.diag([1e-9,.3]),X.T@(w*y));result[t]=float(coef[0]*scale)
 elif method=='trend_curve':
  scale=_scale(values);ys=sorted(values);center=statistics.mean(ys);x=np.array([(y-center)/10 for y in ys]);v=np.array([values[y]/scale for y in ys]);positive=all(z>=0 for z in v)
  z=np.log1p(v) if positive else np.arcsinh(v);X=np.column_stack([np.ones(len(x)),x,x*x]);coef=np.linalg.solve(X.T@X+np.diag([1e-9,.05,.5]),X.T@z);result={}
  for t in targets:
   tx=(t-center)/10;zz=float(np.clip(np.array([1,tx,tx*tx])@coef,-20,20));result[t]=float((np.expm1(zz) if positive else np.sinh(zz))*scale)
 else:raise ValueError('Unknown method')
 return {y:constrain(v,code) for y,v in result.items()}
def gaps(values,years):
 missing=[y for y in years if y not in values];runs=[]
 for y in missing:
  if not runs or y!=runs[-1][-1]+1:runs.append([y])
  else:runs[-1].append(y)
 lo,hi=min(values),max(values)
 return [(r,'leading' if r[-1]<lo else 'trailing' if r[0]>hi else 'internal') for r in runs]
def make_folds(values,kind,length,max_folds=8):
 if len(values)<4:return []
 ys=sorted(values);folds=[]
 for a in range(min(ys),max(ys)-length+2):
  target=list(range(a,a+length))
  if not all(y in values for y in target):continue
  if kind=='internal':
   if a-1 not in values or a+length not in values:continue
   train={y:v for y,v in values.items() if y not in target}
  elif kind=='leading':train={y:v for y,v in values.items() if y>a+length-1}
  else:train={y:v for y,v in values.items() if y<a}
  if len(train)>=3:folds.append((train,target))
 if len(folds)>max_folds:folds=[folds[i] for i in sorted(set(np.linspace(0,len(folds)-1,max_folds).round().astype(int)))]
 return folds
def validation_folds(values,kind,length,max_folds=8):
 exact=make_folds(values,kind,length,max_folds)
 if exact:return exact,'matched',length
 for k in range(min(length-1,3),0,-1):
  fs=make_folds(values,kind,k,max_folds)
  if fs:return fs,'shorter_gap_fallback',k
 # Sparse source years: hide a known observation but preserve direction.
 sparse=[]
 for t in sorted(values):
  train={y:v for y,v in values.items() if y!=t and (kind=='internal' or (kind=='leading' and y>t) or (kind=='trailing' and y<t))}
  if len(train)<3:continue
  if kind=='internal' and not (min(train)<t<max(train)):continue
  sparse.append((train,[t]))
 return sparse[:max_folds],'sparse_fallback' if sparse else 'unvalidated',1
def select_method(values,kind,length,code,max_folds=8):
 folds,match,validated_length=validation_folds(values,kind,length,max_folds);trials=[];scores=[]
 for method in METHODS:
  rows=[];failed=False
  for fold_id,(training,targets) in enumerate(folds):
   try:pred=fit_predict(training,targets,method,code)
   except (ValueError,np.linalg.LinAlgError,OverflowError):failed=True;break
   norm=max(statistics.mean(abs(v) for v in training.values()),1e-9)
   for t in targets:
    error=pred[t]-values[t];rows.append(dict(fold=fold_id,year=t,actual=values[t],predicted=pred[t],method=method,absolute_error=abs(error),squared_error=error*error,normalized_error=abs(error)/norm,training_years=';'.join(map(str,sorted(training))),masked_years=';'.join(map(str,targets))))
  if failed or not rows:continue
  trials.extend(rows);scores.append(dict(method=method,MAE=statistics.mean(r['absolute_error'] for r in rows),RMSE=math.sqrt(statistics.mean(r['squared_error'] for r in rows)),normalized_MAE=statistics.mean(r['normalized_error'] for r in rows),validation_points=len(rows),folds=len(folds)))
 chosen=min(scores,key=lambda x:(x['MAE'],METHODS.index(x['method'])))['method'] if scores else 'weighted'
 return dict(method=chosen,scores=scores,trials=trials,match=match,validated_length=validated_length,folds=len(folds))
def nested_audit(values,kind,length,code,max_outer=3):
 folds,match,_=validation_folds(values,kind,length,max_outer);result=[]
 for i,(train,targets) in enumerate(folds):
  inner=select_method(train,kind,length,code,max_folds=5);pred=fit_predict(train,targets,inner['method'],code);scale=max(statistics.mean(abs(v) for v in train.values()),1e-9)
  for t in targets:result.append(dict(outer_fold=i,year=t,actual=values[t],predicted=pred[t],method=inner['method'],absolute_error=abs(values[t]-pred[t]),normalized_error=abs(values[t]-pred[t])/scale,training_years=';'.join(map(str,sorted(train))),outer_masked_years=';'.join(map(str,targets)),inner_validation_points=sum(s['validation_points'] for s in inner['scores']),match=match))
 return result
def build_estimates(data):
 records={(r['country'],r['indicator'],r['year']):r for r in data['panel']};estimates=[];decisions=[];trials=[];scores=[];unresolved=[];audits=[];cache={};audit_count=0
 source_meta=[m for m in data['catalog'] if m['kind']=='source']
 for country in ['IRN','EGY']:
  for meta in source_meta:
   code=meta['code'];values={y:records[(country,code,y)]['value'] for y in data['years'] if records.get((country,code,y),{}).get('value') is not None}
   if not values:continue
   for missing,kind in gaps(values,data['years']):
    if code=='GII.RANK':
     for y in missing:unresolved.append(dict(country=country,indicator=code,year=y,reason='رتبهٔ ترتیبی با تغییر روش و تعداد کشورها؛ تخمین تاریخی معتبر از این پنج رتبه ممکن نیست.'))
     continue
    key=(country,code,kind,len(missing))
    if key not in cache:
     selected=select_method(values,kind,len(missing),code);cache[key]=selected
     stamp=dict(country=country,indicator=code,gap_kind=kind,gap_length=len(missing),match=selected['match'],validated_length=selected['validated_length'])
     trials.extend(dict(**stamp,**r) for r in selected['trials']);scores.extend(dict(**stamp,**r) for r in selected['scores'])
     if audit_count<12 and selected['folds']>=2:
      audits.extend(dict(country=country,indicator=code,gap_kind=kind,gap_length=len(missing),**r) for r in nested_audit(values,kind,len(missing),code));audit_count+=1
    selected=cache[key];pred=fit_predict(values,missing,selected['method'],code)
    es=[r['absolute_error'] for r in selected['trials'] if r['method']==selected['method']];q=float(np.quantile(es,.9)) if es else None
    score=next((s for s in selected['scores'] if s['method']==selected['method']),{})
    decisions.append(dict(country=country,indicator=code,gap_kind=kind,gap_length=len(missing),target_years=';'.join(map(str,missing)),method=selected['method'],method_fa=METHOD_NAMES[selected['method']],match=selected['match'],validated_length=selected['validated_length'],validation_points=score.get('validation_points',0),validation_MAE=score.get('MAE'),source_years=len(values)))
    for y in missing:
     inflation=math.sqrt(max(1,len(missing)/selected['validated_length'])) if selected['match']!='matched' else 1.
     band=q*inflation if q is not None else None
     estimates.append(dict(country=country,indicator=code,year=y,estimated_value=pred[y],method=selected['method'],method_fa=METHOD_NAMES[selected['method']],gap_kind=kind,gap_length=len(missing),match=selected['match'],validation_points=score.get('validation_points',0),validation_MAE=score.get('MAE'),diagnostic_lower=constrain(pred[y]-band,code) if band is not None else None,diagnostic_upper=constrain(pred[y]+band,code) if band is not None else None,status='estimated'))
 # Derived metrics inherit every input estimate; originally published calculations stay intact.
 em={(r['country'],r['indicator'],r['year']):r for r in estimates}
 for country in ['IRN','EGY']:
  for m in data['catalog']:
   if m['kind']!='derived':continue
   inputs=re.findall(r'[A-Z][A-Z0-9.]+',m['formula'])
   for y in data['years']:
    if records[(country,m['code'],y)]['value'] is not None:continue
    nums=[];flags=[]
    for inp in inputs:
     original=records.get((country,inp,y),{}).get('value');estimated=em.get((country,inp,y));nums.append(original if original is not None else estimated['estimated_value'] if estimated else None);flags.append(estimated)
    if any(v is None for v in nums) or not any(flags):continue
    a,b=nums[:2]
    if '/ 100' in m['formula']:v=a*b/100
    elif ' / ' in m['formula']:
     if b==0:continue
     v=float(m['formula'].split('*')[0].strip())*a/b
    else:v=a-b
    row=dict(country=country,indicator=m['code'],year=y,estimated_value=float(v),method='derived',method_fa=METHOD_NAMES['derived'],gap_kind='derived',gap_length=None,match='inherited',validation_points=None,validation_MAE=None,diagnostic_lower=None,diagnostic_upper=None,status='derived_from_estimate');estimates.append(row);em[(country,m['code'],y)]=row
 analysis=copy.deepcopy(data)
 for r in analysis['panel']:
  r['original_value']=r['value'];e=em.get((r['country'],r['indicator'],r['year']));r['is_estimated']=bool(e)
  if e:r.update(value=e['estimated_value'],status=e['status'],estimation_method=e['method'],estimation_match=e['match'],validation_MAE=e['validation_MAE'])
 analysis['estimation_summary']=dict(estimated_values=len(estimates),source_estimates=sum(e['method']!='derived' for e in estimates),derived_estimates=sum(e['method']=='derived' for e in estimates),unresolved=len(unresolved),validation_trials=len(trials),outer_validation_patterns=audit_count,outer_validation_points=len(audits),methods={m:sum(e['method']==m for e in estimates) for m in METHODS},nested_normalized_MAE=statistics.mean(r['normalized_error'] for r in audits) if audits else None)
 return dict(analysis=analysis,estimates=estimates,decisions=decisions,trials=trials,scores=scores,unresolved=unresolved,nested_audit=audits)
