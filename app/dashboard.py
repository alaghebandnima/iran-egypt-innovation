from __future__ import annotations
import sys,pathlib,json,html
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import streamlit as st
import pandas as pd
import time
import online_assistant
import plotly.graph_objects as go
from i18n import L,set_language,language,country,metric_name,metric_note,method_name,source_status,KIND_EN,EVENTS_EN
from engine import series,period_summary,annual_comparison,number,grounded_answer,explain_with_ollama
from estimation import select_method,KINDS
from presentation import fa,unit,GROUPS,theme_css,decorate,countries,table,kpi,footer
from charts import trend_figure
from about import about_page
from coverage_cards import coverage_cards
from selection import valid_group,indicator_options,valid_indicator
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'data/panel_2005_2024'
set_language('en' if st.session_state.get('language_en',False) else 'fa')
st.set_page_config(page_title=L('ایران و مصر | فناوری و نوآوری','Iran and Egypt | Technology and Innovation'),page_icon='📊',layout='wide',initial_sidebar_state='auto')
with st.container(key='topbar'):
 st.markdown(decorate(),unsafe_allow_html=True)
 with st.container(key='theme_control'):
  dark=st.toggle(L('حالت تیره','Dark mode'),value=True,key='dark_mode')
  english=st.toggle('English',value=False,key='language_en')
 set_language('en' if english else 'fa')
css,tokens=theme_css(dark);st.markdown(css,unsafe_allow_html=True)
@st.cache_data
def read_file(path,version):return json.loads(pathlib.Path(path).read_text('utf-8'))
def read(name):
 p=P/name;return read_file(str(p),p.stat().st_mtime_ns)
source=read('dashboard_data.json');analysis=read('analysis_with_estimates.json');details=read('estimation_details.json');meta={m['code']:m for m in source['catalog']}
def name(m):return fa(metric_name(m)) if language()=='fa' else metric_name(m)
def show(headers,rows,red=None):st.markdown(table(headers,rows,red),unsafe_allow_html=True)
def download_report(key):
 p=ROOT/'app/assets/estimation_methodology_fa.pdf'
 if p.exists():st.download_button(L('گزارش متودولوژی تخمین','Estimation methodology report'),p.read_bytes(),'گزارش متودولوژی تخمین.pdf','application/pdf',key=key,on_click='ignore')
def capture_group(key):
 st.session_state['selected_group_code']=valid_group(source['catalog'],st.session_state.get(key))
def capture_indicator(key):
 value=st.session_state.get(key)
 if value in meta:st.session_state['selected_metric_code']=value
with st.sidebar:
 st.markdown('### '+L('ایران × مصر','Iran × Egypt'));st.caption(L('مدیریت فناوری و نوآوری','Technology and innovation management'))
 st.markdown('**'+L('۲۰۰۵ تا ۲۰۲۴ · بیست سال','2005–2024 · Twenty years')+'**')
 group_key='metric_group_'+language();indicator_key='selected_indicator_'+language()
 st.session_state[group_key]=valid_group(source['catalog'],st.session_state.get('selected_group_code','ALL'))
 group=st.selectbox(L('گروه شاخص','Indicator group'),['ALL']+list(dict.fromkeys(m['group'] for m in source['catalog'])),format_func=lambda g:L('همهٔ گروه‌ها','All groups') if g=='ALL' else g if english else GROUPS.get(g,g),key=group_key,on_change=capture_group,args=(group_key,))
 group=valid_group(source['catalog'],group)
 options=indicator_options(source['catalog'],group)
 st.session_state[indicator_key]=valid_indicator(options,st.session_state.get('selected_metric_code'))
 code=st.selectbox(L('شاخص مورد بررسی','Selected indicator'),options,format_func=lambda c:name(meta[c]) if c in meta else '',key=indicator_key,on_change=capture_indicator,args=(indicator_key,))
 code=valid_indicator(options,code)
 st.session_state['selected_metric_code']=code
 start,end=st.slider(L('بازهٔ نمایش','Display period'),2005,2024,(2005,2024),key='display_period')
 estimates=st.toggle(L('تکمیل سال‌های ناموجود با تخمین','Fill missing years with project estimates'),True,key='include_estimates')
 events=st.toggle(L('نمایش رویدادهای خارجی و تاریخی','Show external and historical events'),True,key='show_events')
 world=st.toggle(L('نمایش مرجع جهانی، در صورت وجود','Show world reference, where available'),False,key='show_world')
 st.divider();st.caption(L('ایران: آبی · مصر: طلایی · تخمین پروژه: قرمز','Iran: blue · Egypt: gold · Project estimates: red'))
 with st.expander(L('دریافت داده‌ها و گزارش','Download data and reports')):
  for filename,label in [('estimation_estimates.csv',L('فهرست تخمین‌ها','Project estimates')),('estimation_scores.csv',L('خطای روش‌ها در اعتبارسنجی','Validation errors by method'))]:st.download_button(label,(P/filename).read_bytes(),filename,'text/csv',key=filename)
  for filename,label in [('Iran_Egypt_2005_2024.xlsx',L('اکسل داده‌های اصلی','Source-data Excel workbook')),('Iran_Egypt_With_Estimates.xlsx',L('اکسل همراه تخمین‌ها','Excel workbook with project estimates'))]:
   p=ROOT/'outputs/iran_egypt_2005_2024'/filename
   if p.exists():st.download_button(label,p.read_bytes(),filename,key=filename)
  download_report('sidebar_report')
data=analysis if estimates else source;m=meta[code];u=unit(m)
summary=period_summary(data,code,start,end);base=period_summary(source,code,start,end)
ir=series(data,code,'IRN',start,end);eg=series(data,code,'EGY',start,end)
st.markdown('<div class="eyebrow">'+L('رصد فناوری و نوآوری · ۲۰۰۵ تا ۲۰۲۴','TECHNOLOGY AND INNOVATION · 2005–2024')+'</div>',unsafe_allow_html=True)
st.title(L('دو کشور، بیست سال تحول','Two countries, twenty years of change'))
st.markdown('<div class="hero-lead">'+L(f'ایران و مصر در قاب داده‌ها؛ {source["summary"]["source_metrics"]} شاخص منبع و {source["summary"]["derived_metrics"]} شاخص محاسبه‌شده',f'Iran and Egypt through data: {source["summary"]["source_metrics"]} source indicators and {source["summary"]["derived_metrics"]} derived indicators')+'</div>',unsafe_allow_html=True)
with st.container(key='country_actions',horizontal=True,vertical_alignment='center'):
 st.markdown(countries(),unsafe_allow_html=True)
 pdf=ROOT/'app/assets/analytical_comparison_fa.pdf'
 st.download_button(L('پی دی اف مقایسه تحلیلی دو کشور','Analytical comparison of the two countries (PDF)'),pdf.read_bytes(),'مقایسه تحلیلی دو کشور.pdf','application/pdf',key='analytical_pdf_download',on_click='ignore')
st.markdown('<div class="estimate-notice"><strong>'+L('اعداد و نقاط قرمز تخمینی‌اند.','Red numbers and points are project estimates.')+'</strong> '+L('مقدار منتشرشدهٔ این سال‌ها در منبع در دسترس نبوده است. روش تخمین با آزمون پنهان‌سازی داده انتخاب شده است؛ خلاصه‌های متکی به تخمین نیز قرمزند.','Source values were unavailable for these years. Methods were selected using artificial missingness validation; summaries using project estimates are also red.')+'</div>',unsafe_allow_html=True)
tabs=st.tabs([L('مقایسهٔ بیست‌ساله','Twenty-year comparison'),L('پوشش داده‌ها','Data coverage'),L('آزمایش تخمین','Estimation experiment'),L('دستیار تحلیل','Analysis assistant'),L('متودولوژی تخمین','Estimation methodology'),L('درباره ما','About us')])
with tabs[0]:
 st.subheader(name(m));st.caption(L('واحد: ','Unit: ')+u)
 common=summary['common_years'];cols=st.columns(4)
 cols[0].markdown(kpi(L('سال‌های قابل مقایسه','Comparable years'),f'{len(common)} / {end-start+1}',L(f'با دادهٔ منبع: {len(base["common_years"])} سال',f'With source values: {len(base["common_years"])} years'),len(common)>len(base['common_years'])),unsafe_allow_html=True)
 original_span=base['common_years'][::max(1,len(base['common_years'])-1)];active_span=common[::max(1,len(common)-1)]
 cols[1].markdown(kpi(L('دورهٔ مقایسه','Comparison period'),f'{common[0]}–{common[-1]}' if common else L('موجود نیست','Unavailable'),estimated=original_span!=active_span),unsafe_allow_html=True)
 for co,col,rs in [('IRN',cols[2],ir),('EGY',cols[3],eg)]:
  flag=any(r.get('is_estimated') and r['year'] in ([common[0],common[-1]] if common else []) for r in rs)
  col.markdown(kpi(L('تغییر ','Change: ')+country(co),number(summary['country'][co]['change']),u,flag),unsafe_allow_html=True)
 if code=='GII.RANK':st.info(L('رتبهٔ نوآوری برای سال‌های منتشرنشده تخمین زده نمی‌شود؛ تغییر تعداد کشورها و روش رتبه‌بندی بازسازی تاریخی رتبه را نامعتبر می‌کند.','Unpublished innovation ranks are not estimated: changes in methodology and country coverage make historical reconstruction unreliable.'))
 st.plotly_chart(trend_figure(data,code,start,end,tokens,u,world,events),width='stretch',theme=None,config={'displaylogo':False})
 rows=[];red=set()
 for i,(co,rs) in enumerate([('IRN',ir),('EGY',eg)]):
  s=summary['country'][co];n=sum(r.get('is_estimated',False) for r in rs)
  rows.append([country(co),sum(r['value'] is not None and not r.get('is_estimated') for r in rs),n,number(s['first']),number(s['last']),number(s['mean_common'])])
  for j,y in [(3,common[0] if common else None),(4,common[-1] if common else None)]:
   if any(r['year']==y and r.get('is_estimated') for r in rs):red.add((i,j))
  if any(r.get('is_estimated') and r['year'] in common for r in rs):red.add((i,5))
 show(L(['کشور','سال با مقدار منتشرشدهٔ منبع','سال تخمین پروژه','ابتدای دورهٔ مشترک','انتهای دورهٔ مشترک','میانگین مشترک'],['Country','Years with source values','Project-estimated years','First common year value','Last common year value','Common-year mean']),rows,red)
 st.markdown('#### '+L('مقایسهٔ سال‌به‌سال','Year-by-year comparison'))
 annual=annual_comparison(data,code,start,end);rows=[];red=set();export=[]
 for i,(a,b,r) in enumerate(zip(ir,eg,annual)):
  af=a.get('is_estimated',False);bf=b.get('is_estimated',False)
  status=L('دارای تخمین پروژه','Includes project estimate') if af or bf else L('برآورد منتشرشدهٔ سوئید','Published SWIID estimates') if m.get('source_is_estimated') and r['IRN'] is not None and r['EGY'] is not None else L('منتشرشده در منبع','Published source values') if r['IRN'] is not None and r['EGY'] is not None else L('پوشش ناقص','Incomplete coverage')
  rows.append([r['year'],number(r['IRN']),number(r['EGY']),number(r['difference']),number(r['ratio']),status])
  if af:red.add((i,1))
  if bf:red.add((i,2))
  if af or bf:red.update([(i,3),(i,4)])
  export.append(dict(**r,IRN_estimated=af,EGY_estimated=bf,IRN_source_estimated=a.get('source_is_estimated',False),EGY_source_estimated=b.get('source_is_estimated',False)))
 show(L(['سال','ایران','مصر','اختلاف ایران − مصر','نسبت ایران به مصر','وضعیت'],['Year','Iran','Egypt','Iran − Egypt','Iran / Egypt','Status']),rows,red)
 st.download_button(L('دریافت جدول با برچسب تخمین','Download table with estimation flags'),pd.DataFrame(export).to_csv(index=False).encode('utf-8-sig'),'annual_comparison.csv','text/csv')
 with st.expander(L('روش تخمین همین شاخص','Estimation method for this indicator')):
  ds=[d for d in details['decisions'] if d['indicator']==code]
  show(L(['کشور','سال‌های تخمینی','روش منتخب','طول شکاف واقعی / آزمون','میانگین قدرمطلق خطا'],['Country','Project-estimated years','Selected method','Actual / validated gap length','Mean absolute error']),[[country(d['country']),d['target_years'],method_name(d['method']),f'{d["gap_length"]} / {d["validated_length"]}',number(d['validation_MAE'])] for d in ds])
  st.caption(L('اگر آزمون هم‌طول ممکن نباشد، شکاف کوتاه‌تر یا مشاهدهٔ منفرد آزموده می‌شود؛ تعمیم به شکاف بلندتر اطمینان کمتری دارد.','When a matched-length test is unavailable, shorter gaps or single observations are tested. Applying the result to a longer gap is less certain.'))
 with st.expander(L('رویدادهای خارجی و تاریخی','External and historical events')):
  for e in source['events']:
   if start<=e['year']<=end:
    title=EVENTS_EN[(e['country'],e['year'])] if english else fa(e['title_fa'])
    st.markdown(f'**{e["year"]} · {country(e["country"])}** — {title}')
    if e.get('source_url'):st.link_button(L('منبع رویداد','Event source'),e['source_url'],key='event_'+str(e['year'])+e['country'])
  st.caption(L('هم‌زمانی رویداد و تغییر شاخص به‌تنهایی رابطهٔ علّی را ثابت نمی‌کند.','An event occurring alongside an indicator change does not establish causation.'))
 with st.expander(L('تعریف و منبع شاخص','Indicator definition and source')):
  st.write(metric_note(m));st.code(code);st.link_button(L('صفحهٔ منبع','Source page'),m['source_url'])
  if m.get('formula'):st.code(m['formula'])
with tabs[1]:
 st.subheader(L('پوشش منبع، پیش از تخمین پروژه','Source coverage before project estimation'))
 st.caption(L('قاعدهٔ عمومی: حداکثر پنج سال مفقود در هر کشور. استثناها: رتبهٔ نوآوری، صادرات فناوری‌پیشرفته و هزینهٔ تحقیق‌وتوسعه.','General rule: at most five missing years per country. Exceptions: innovation rank, high-technology exports and R&D expenditure.'))
 z=[[sum(r['value'] is not None for r in series(source,x['code'],co)) for co in ['IRN','EGY']] for x in source['catalog']]
 with st.container(key='coverage_mobile'):
  st.markdown(coverage_cards(source['catalog'],z,len(source['years'])),unsafe_allow_html=True)
 with st.container(key='coverage_desktop'):
  fig=go.Figure(go.Heatmap(z=z,x=[country('IRN'),country('EGY')],y=[name(x) for x in source['catalog']],zmin=0,zmax=20,colorscale=[[0,tokens['panel2']],[1,'#2c91b5']],hovertemplate='%{y}<br>%{x}: %{z} '+L('سال','years')+'<extra></extra>'))
  fig.update_layout(height=1900,paper_bgcolor=tokens['panel'],plot_bgcolor=tokens['panel'],font=dict(color=tokens['text'],family='Vazirmatn'),margin=dict(l=380,r=25,t=25,b=25),yaxis=dict(autorange='reversed'))
  st.plotly_chart(fig,width='stretch',theme=None)
with tabs[2]:
 st.subheader(L('اعتبارسنجی با داده‌های عمداً پنهان‌شده','Artificial missingness validation'))
 st.write(L('مقادیر معلوم منبع را پنهان می‌کنیم؛ چهار روش فقط با سال‌های باقی‌مانده برازش می‌شوند. روش دارای کمترین میانگین قدرمطلق خطا انتخاب می‌شود.','Known source values are hidden. Four methods use only the remaining years; the method with the lowest mean absolute error is selected.'))
 co=st.radio(L('کشور آزمون','Test country'),['IRN','EGY'],format_func=country,horizontal=True,key='test_country_'+language()) or 'IRN'
 kind=st.selectbox(L('شکل شکاف','Gap pattern'),list(KINDS),format_func=lambda k:KIND_EN.get(k,k) if english else KINDS.get(k,k),key='gap_pattern_'+language()) or 'internal';length=st.slider(L('تعداد سال پنهان‌شده در هر پنجره','Years hidden in each window'),1,6,1,key='mask_length')
 if m['kind']=='derived' or code=='GII.RANK':st.info(L('یک شاخص منبع پیوسته انتخاب کنید. شاخص محاسبه‌شده از ورودی هم‌سال ساخته می‌شود و رتبه برون‌یابی نمی‌شود.','Select a continuous source indicator. Derived metrics use same-year inputs; ranks are not extrapolated.'))
 else:
  values={r['year']:r['value'] for r in series(source,code,co) if r['value'] is not None};v=select_method(values,kind,length,code)
  if not v['scores']:st.warning(L('دادهٔ کافی برای آزمون مستقل این الگو نیست.','Insufficient data for an independent test of this pattern.'))
  else:
   st.success(L('روش منتخب: ','Selected method: ')+method_name(v['method']))
   if v['match']!='matched':st.warning(L(f'آزمون دقیق این شکاف ممکن نیست؛ طول آزموده‌شده: {v["validated_length"]} سال. برای شکاف اصلی احتیاط بیشتری لازم است.',f'An exact match is unavailable. Validated length: {v["validated_length"]} year(s). Apply greater caution to the original gap.'))
   show(L(['روش','تعداد نقطهٔ آزمون','میانگین قدرمطلق خطا','ریشهٔ میانگین مربع خطا'],['Method','Validation points','Mean absolute error','Root mean squared error']),[[method_name(s['method']),s['validation_points'],number(s['MAE']),number(s['RMSE'])] for s in v['scores']])
   fold_options=sorted(set(r['fold'] for r in v['trials']));fold_key='mask_window_'+language()
   st.session_state[fold_key]=valid_indicator(fold_options,st.session_state.get(fold_key))
   fold=st.selectbox(L('پنجرهٔ پنهان‌سازی','Masking window'),fold_options,format_func=lambda n:L(f'پنجرهٔ {n+1}',f'Window {n+1}') if n is not None else '—',key=fold_key)
   fold=valid_indicator(fold_options,fold);tr=[r for r in v['trials'] if r['fold']==fold]
   show(L(['سال پنهان‌شده','روش','مقدار منبع','تخمین','خطای مطلق'],['Hidden year','Method','Source value','Prediction','Absolute error']),[[r['year'],method_name(r['method']),number(r['actual']),number(r['predicted']),number(r['absolute_error'])] for r in tr],{(i,3) for i in range(len(tr))})
   st.caption(L('سال‌های آموزش: ','Training years: ')+(tr[0]['training_years'] if tr else '—'))
with tabs[3]:
 st.subheader(L('دستیار تحلیل با اولاما','Analysis assistant with Ollama'))
 st.caption(L('پاسخ کوتاه بر پایهٔ داده‌های شاخص انتخاب‌شده.','A concise answer grounded in the selected indicator.'))
 question=st.text_input(L('پرسش شما','Your question'),value=L('این شاخص در ۲۰۲۴ در ایران و مصر چقدر است؟','What are the values of this indicator for Iran and Egypt in 2024?'),key='question_'+language(),max_chars=800)
 if st.button(L('بررسی و پاسخ','Analyze and answer'),type='primary'):
  result=online_assistant.prepare(data,question,code,start,end);model_result=None
  if not result['needs_model']:
   st.warning(result['fallback_short'])
  else:
   try:
    now=time.monotonic();previous=st.session_state.get('assistant_last_request',0)
    if now-previous<20 and not online_assistant.cached(result):
     raise RuntimeError(L('لطفاً برای پرسش بعدی چند لحظه صبر کنید.','Please wait briefly before submitting another question.'))
    st.session_state['assistant_last_request']=now
    with st.spinner(L('اولاما در حال تحلیل داده‌ها است…','Ollama is analyzing the evidence…')):model_result=online_assistant.answer(result)
   except Exception as exc:
    st.warning(L('پاسخ اولاما آماده نشد. ','Ollama could not produce an answer. ')+str(exc))
   if model_result:
    st.caption(L('تحلیل تولیدشده با اولاما','Analysis generated by Ollama'))
    st.markdown('<div class="answer-box '+('estimated' if result.get('compact_estimated') else '')+'">'+html.escape(model_result['short_answer'])+'</div>',unsafe_allow_html=True)
with tabs[4]:
 st.subheader(L('متودولوژی؛ دادهٔ منبع و تخمین پروژه','Methodology: source values and project estimates'));s=analysis['estimation_summary']
 source_count=sum(x['kind']=='source' for x in source['catalog']);derived_count=sum(x['kind']=='derived' for x in source['catalog'])
 st.write(L(f'مجموعهٔ فعلی شامل {len(source["catalog"])} شاخص است: {source_count} شاخص منبع و {derived_count} شاخص محاسبه‌شده. از مجموع {s["estimated_values"]} مقدار تکمیلی، {s["source_estimates"]} مقدار تخمین شاخص‌های منبع و {s["derived_estimates"]} مقدار محاسبه از ورودی تخمینی است.',f'The current dataset contains {len(source["catalog"])} indicators: {source_count} source indicators and {derived_count} derived indicators. Of {s["estimated_values"]} completed values, {s["source_estimates"]} are estimates of source indicators and {s["derived_estimates"]} are calculated from estimated inputs.'))
 st.write(L('بازهٔ ثابت ۲۰۰۵–۲۰۲۴ است. مقادیر منتشرشدهٔ منبع جدا از مقادیر تکمیلی نگهداری می‌شوند.','The fixed period is 2005–2024. Published source values are stored separately from completed values.'))
 for a,b in [('میانگین‌گیری وزنی: دو سر شکاف با وزن فاصله؛ در انتهای سری سه مشاهدهٔ نزدیک.','Weighted average: distance weights between observations; three nearby values at a series boundary.'),('روند محلی تعدیل‌شده: برازش خط با نزدیک‌ترین پنج مشاهده و جریمهٔ شیب.','Regularized local trend: a line fitted to the five nearest observations, with a slope penalty.'),('منحنی روند: منحنی درجهٔ دوم منظم‌شده پس از تبدیل مناسب مقادیر.','Trend curve: a regularized quadratic curve after an appropriate value transformation.'),('وضعیت پنهان: مدل سطح و شیب با فیلتر و هموارساز کالمن.','Latent state: a level-and-slope model using a Kalman filter and smoother.')]:st.write(L(a,b))
 st.write(L('برای هر کشور، شاخص، جهت و طول شکاف، مقادیر معلوم عمداً پنهان و روش دارای کمترین خطا انتخاب می‌شود. اگر آزمون هم‌طول ممکن نباشد، آزمون کوتاه‌تر صریحاً برچسب می‌خورد.','For each country, indicator, gap direction and length, known values are deliberately hidden and the lowest-error method is selected. Shorter validation gaps are explicitly identified when a matched test is unavailable.'))
 st.write(L(f'آزمون بیرونی مستقل: {s["outer_validation_patterns"]} الگو، {s["outer_validation_points"]} نقطه؛ میانگین خطای مطلق نرمال‌شده {s["nested_normalized_MAE"]*100:.2f}٪ از میانگین قدرمطلق آموزش. این عدد درصد دقت یا تضمین خطای هر تخمین نیست.',f'Independent outer validation: {s["outer_validation_patterns"]} patterns, {s["outer_validation_points"]} points; normalized mean absolute error {s["nested_normalized_MAE"]*100:.2f}% of the mean absolute training value. This is not an accuracy percentage or an error guarantee for each estimate.'))
 download_report('method_report')
with tabs[5]:
 st.markdown(about_page(),unsafe_allow_html=True)
st.markdown(footer(),unsafe_allow_html=True)
