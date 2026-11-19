"""Persian presentation, theme tokens and provenance-aware tables."""
import pathlib,base64,html,re
from functools import lru_cache
from i18n import L,language,country
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORDS={'Ollama':'اولاما','Python':'پایتون','Methodology':'متودولوژی','Streamlit':'استریم‌لیت','Plotly':'پلاتلی','Artificial Missingness Validation':'اعتبارسنجی با داده‌های عمداً پنهان‌شده','WIPO':'وایپو','IMF':'صندوق بین‌المللی پول','WDI':'شاخص‌های توسعهٔ جهانی','GDP':'تولید ناخالص داخلی','PPP':'برابری قدرت خرید','R&D':'تحقیق‌وتوسعه','ICT':'فناوری اطلاعات و ارتباطات','FDI':'سرمایه‌گذاری مستقیم خارجی','CAGR':'نرخ رشد مرکب','RMSE':'ریشهٔ میانگین مربع خطا','MAE':'میانگین قدرمطلق خطا','FTE':'معادل تمام‌وقت','GII':'شاخص جهانی نوآوری','CSV':'سی‌اس‌وی','JSON':'جیسون','API':'رابط برنامه‌نویسی','ISO':'ایزو','UNESCO':'یونسکو','OECD':'سازمان همکاری و توسعهٔ اقتصادی','ILO':'سازمان بین‌المللی کار','FTES':'معادل تمام‌وقت'}
UNITS={'applications':'درخواست','Fractional count':'شمارش کسری','% of GDP':'درصد تولید ناخالص داخلی','% GDP':'درصد تولید ناخالص داخلی','USD current':'دلار آمریکا، جاری','Current international $':'دلار بین‌المللی، جاری','Constant international $':'دلار بین‌المللی، ثابت','index 0–100':'شاخص صفر تا صد','rank (lower is better)':'رتبه؛ عدد کمتر بهتر','per million people':'به‌ازای یک میلیون نفر','per 100 people':'به‌ازای صد نفر','Per 100 people':'به‌ازای صد نفر','current US$':'دلار آمریکا، جاری','current US$ per person':'دلار آمریکا به‌ازای هر نفر','current international $ per person':'دلار بین‌المللی به‌ازای هر نفر','ratio':'نسبت','percentage points':'واحد درصد','people':'نفر','years':'سال','%':'درصد','number':'تعداد','Number':'تعداد','Percent':'درصد','Per million people':'به‌ازای یک میلیون نفر','% of population':'درصد جمعیت','% of total population':'درصد کل جمعیت','t CO2e/capita':'تن معادل دی‌اکسیدکربن به‌ازای هر نفر','kg oil equivalent':'کیلوگرم معادل نفت','LCU per US$':'واحد پول ملی به‌ازای دلار','design count':'شمار طرح','articles':'مقاله','Annual %':'درصد سالانه','Annual percent change':'درصد تغییر سالانه'}
GROUPS={'Knowledge and R&D':'دانش و تحقیق‌وتوسعه','Technology trade':'تجارت فناوری','Digital infrastructure':'زیرساخت دیجیتال','Education and inclusion':'آموزش و مشارکت','Economy and finance':'اقتصاد و تأمین مالی','Welfare and sustainability':'رفاه و پایداری','Derived':'شاخص‌های محاسبه‌شده'}
def fa(text):
 s=str(text)
 for a,b in sorted(WORDS.items(),key=lambda x:-len(x[0])):s=re.sub(r'(?<![A-Za-z])'+re.escape(a)+r'(?![A-Za-z])',lambda _:b,s,flags=re.I)
 return s
def unit(meta):
 if language()=='en':
  overrides={'IT.NET.BBND.P2':'subscriptions per 100 people','IT.CEL.SETS.P2':'subscriptions per 100 people','IT.MLT.MAIN.P2':'subscriptions per 100 people','IT.NET.SECR.P6':'servers per million people','SP.POP.TOTL':'people','CM.MKT.LCAP.GD.ZS':'% of GDP','SE.TER.ENRR.FE':'gross female tertiary enrollment, %','SE.TER.ENRR':'gross tertiary enrollment, %','SWIID.GINI.DISP':'Gini index, 0–100'}
  return overrides.get(meta['code'],meta.get('unit_display') or meta.get('unit',''))
 overrides={'IT.NET.BBND.P2': 'اشتراک به\u200cازای صد نفر', 'IT.CEL.SETS.P2': 'اشتراک به\u200cازای صد نفر', 'IT.MLT.MAIN.P2': 'اشتراک به\u200cازای صد نفر', 'EG.ELC.LOSS.ZS': 'درصد کل تولید برق', 'EG.ELC.ACCS.ZS': 'درصد جمعیت', 'IT.NET.SECR.P6': 'تعداد سرور', 'CM.MKT.LCAP.GD.ZS': 'درصد تولید ناخالص داخلی', 'SP.POP.TOTL': 'نفر', 'NY.GDP.TOTL.RT.ZS': 'درصد تولید ناخالص داخلی', 'SL.UEM.1524.ZS': 'درصد نیروی کار ۱۵ تا ۲۴ سال', 'SL.UEM.TOTL.ZS': 'درصد کل نیروی کار', 'SE.TER.ENRR.FE': 'درصد ناخالص ثبت\u200cنام زنان در آموزش عالی', 'SL.UEM.NEET.ZS': 'درصد جمعیت جوان', 'SL.TLF.CACT.FE.ZS': 'درصد زنان ۱۵ ساله و بیشتر', 'SL.TLF.CACT.ZS': 'درصد جمعیت ۱۵ ساله و بیشتر', 'SE.TER.ENRR': 'درصد ناخالص ثبت\u200cنام آموزش عالی', 'SL.EMP.TOTL.SP.ZS': 'درصد جمعیت ۱۵ ساله و بیشتر', 'SP.DYN.LE00.IN': 'سال', 'EG.FEC.RNEW.ZS': 'درصد مصرف نهایی انرژی', 'EG.ELC.RNEW.ZS': 'درصد تولید برق', 'SP.POP.1564.TO.ZS': 'درصد جمعیت', 'SP.URB.TOTL.IN.ZS': 'درصد جمعیت', 'SH.XPD.CHEX.GD.ZS': 'درصد تولید ناخالص داخلی', 'EG.USE.PCAP.KG.OE': 'کیلوگرم معادل نفت به\u200cازای هر نفر', 'SP.POP.DPND': 'نسبت جمعیت وابسته به جمعیت سن کار، درصد'}
 if meta.get('code') in overrides:return overrides[meta['code']]
 s=meta.get('unit_display') or meta.get('unit') or ''
 if s in UNITS:return UNITS[s]
 s=fa(s)
 substitutions={'current US$':'دلار آمریکا، جاری','constant 2021 international $':'دلار بین‌المللی ثابت ۲۰۲۱','current international $':'دلار بین‌المللی جاری','per person':'به‌ازای هر نفر','per million people':'به‌ازای یک میلیون نفر','% of':'درصدِ','population':'جمعیت','manufactured exports':'صادرات صنعتی','goods exports':'صادرات کالا','goods imports':'واردات کالا','total exports':'کل صادرات','Annual %':'درصد سالانه','LCU per US$':'پول ملی به‌ازای دلار','kg of oil equivalent per capita':'کیلوگرم معادل نفت به‌ازای هر نفر','metric tons per capita':'تن به‌ازای هر نفر','% of total':'درصد از کل','% of labor force':'درصد نیروی کار'}
 for a,b in sorted(substitutions.items(),key=lambda x:-len(x[0])):s=re.sub(re.escape(a),lambda _:b,s,flags=re.I)
 return s
def data_url(name):
 p=ROOT/'app/assets'/name;b=p.read_bytes();mime='image/svg+xml' if p.suffix=='.svg' else 'image/png' if b.startswith(b'\x89PNG') else 'image/jpeg'
 return 'data:'+mime+';base64,'+base64.b64encode(b).decode()
@lru_cache(maxsize=1)
def font_faces():
 definitions=[('Vazirmatn','Vazirmatn.woff2','font/woff2','woff2','100 900'),('BTitr','BTitr-Bold.ttf','font/ttf','truetype','700')]
 return ''.join('@font-face{font-family:"'+family+'";src:url("data:'+mime+';base64,'+base64.b64encode((ROOT/'app/assets/fonts'/name).read_bytes()).decode()+'") format("'+fmt+'");font-weight:'+weight+';font-style:normal;font-display:swap;}' for family,name,mime,fmt,weight in definitions if (ROOT/'app/assets/fonts'/name).is_file())

def theme_css(dark):
 tokens={'bg':'#101d30','panel':'#15263b','panel2':'#1b3048','text':'#edf3fb','muted':'#aebed2','line':'#334b67','accent':'#72c9f1','grid':'#2c4059','red':'#ff777e','redbg':'#402633','input':'#1b3048'} if dark else {'bg':'#f2f5fa','panel':'#ffffff','panel2':'#eaf0f7','text':'#1b314a','muted':'#526c85','line':'#d2ddeb','accent':'#086a9c','grid':'#dae4ef','red':'#bd243e','redbg':'#fff0f1','input':'#ffffff'}
 tokens['mode']='dark' if dark else 'light'
 variables=';'.join('--'+k+':'+v for k,v in tokens.items())
 css='''<style>
FONTFACES
:root{TOKENS;color-scheme:SCHEME}
html,body,.stApp{background:var(--bg)!important;color:var(--text)!important;font-family:"Vazirmatn",Tahoma,sans-serif!important}
.stMarkdown,[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"],[data-testid="stCaptionContainer"],.estimate-notice,.faculty-footer,.hero-lead,.eyebrow,.country-name,.kpi,.data-table,.answer-box,[data-baseweb="select"],[data-baseweb="popover"]{font-family:"Vazirmatn",Tahoma,sans-serif!important}
.stAppHeader{display:block!important;pointer-events:none!important;background:transparent!important;height:0!important}footer,[data-testid="stStatusWidget"],[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"],[data-testid="stMainMenu"]{display:none!important}
[data-testid="stToolbar"]{pointer-events:none!important;background:transparent!important}
[data-testid="stExpandSidebarButton"]{pointer-events:auto!important;position:fixed!important;right:16px!important;left:auto!important;top:20px!important;background:var(--panel)!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:10px!important;z-index:1005!important}
[data-testid="stExpandSidebarButton"] span{color:var(--text)!important}
[data-testid="stSidebarCollapsedControl"]{pointer-events:auto!important;position:fixed!important;top:20px!important}
[data-testid="stAppViewContainer"]{flex-direction:row-reverse!important;background:transparent!important}
[data-testid="stSidebar"]{direction:rtl;right:0!important;left:auto!important;background:var(--panel)!important;border-left:1px solid var(--line);border-right:0;z-index:50}
[data-testid="stSidebar"]>div{padding-top:1.8rem!important}
[data-testid="stSidebarCollapsedControl"]{left:auto!important;right:15px!important;background:var(--panel)!important;z-index:1000}
[data-testid="stMain"]{direction:rtl;position:relative;background:transparent!important}
[data-testid="stMainBlockContainer"]{padding:7rem 2.6rem 1rem!important;max-width:1550px;position:relative;z-index:2}
h1,h2,h3,p,label,button,summary,li,input,textarea,select{font-family:"Vazirmatn",Tahoma,sans-serif!important;color:var(--text);text-align:right}
h1,h2,h3,h4,h5,h6{font-family:"BTitr","Vazirmatn",Tahoma,sans-serif!important;font-weight:700!important;text-align:right!important;direction:rtl}
h1{font-size:2.45rem!important;font-weight:700!important;letter-spacing:0;line-height:1.6!important;margin:0!important}
h2{font-size:1.6rem!important}h3{font-size:1.15rem!important}
p,label,li,summary,[data-testid="stCaptionContainer"]{text-align:right!important;direction:rtl}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-size:12px!important;line-height:1.9}
.stMarkdown,.stMarkdown p{color:var(--text)!important;line-height:1.95}
input,textarea,[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]{background:var(--input)!important;color:var(--text)!important;border-color:var(--line)!important;direction:rtl}
[data-testid="InputInstructions"],[data-testid="stInputInstructions"]{display:none!important}
[data-baseweb="select"] svg,[data-baseweb="popover"] svg{fill:var(--muted)!important}
[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="popover"] li,[role="listbox"],[role="option"]{background:var(--panel)!important;color:var(--text)!important;text-align:right;direction:rtl}
[data-baseweb="select"] span{color:var(--text)!important}
[data-baseweb="slider"]{direction:ltr} [data-baseweb="slider"] div{color:var(--muted)}
[data-testid="stCheckbox"] label:has(input[role="switch"])>div:not([data-testid]){direction:ltr!important;position:relative!important;display:block!important;flex:0 0 36px!important;width:36px!important;min-width:36px!important;height:22px!important;padding:0!important;border:0!important;border-radius:20px!important;background:color-mix(in srgb,var(--muted) 65%,var(--panel))!important;overflow:hidden!important}
[data-testid="stCheckbox"] label:has(input[role="switch"])>div:not([data-testid])>div{position:absolute!important;left:2px!important;right:auto!important;top:2px!important;bottom:auto!important;width:18px!important;height:18px!important;margin:0!important;border:0!important;border-radius:50%!important;background:#fff!important;transform:none!important;transition:left .18s ease!important}
[data-testid="stCheckbox"] label[data-selected="true"]:has(input[role="switch"])>div:not([data-testid]){background:var(--accent)!important}
[data-testid="stCheckbox"] label[data-selected="true"]:has(input[role="switch"])>div:not([data-testid])>div{left:16px!important}
.stButton button,.stDownloadButton button,[data-testid="stBaseButton-secondary"]{background:var(--panel2)!important;border:1px solid var(--line)!important;color:var(--text)!important;border-radius:10px!important}
[data-testid="stBaseButton-primary"]{background:#187aa8!important;color:white!important;border-color:#187aa8!important}
[data-testid="stExpander"]{background:var(--panel)!important;border:1px solid var(--line)!important;border-radius:12px!important}
[data-testid="stExpander"] details,[data-testid="stExpander"] summary{background:var(--panel)!important;color:var(--text)!important}
[data-testid="stExpander"] summary:hover,[data-testid="stExpander"] summary:focus,[data-testid="stExpander"] summary:focus-visible,[data-testid="stExpander"] summary:active,[data-testid="stExpander"] details[open]>summary{background:var(--panel2)!important;color:var(--text)!important}
[data-testid="stExpander"] summary *{color:var(--text)!important}
.stTabs [data-baseweb="tab-list"]{gap:28px;background:transparent;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;padding:14px 0!important;white-space:nowrap;font-size:13px}
.stTabs [aria-selected="true"]{color:var(--accent)!important}
[data-testid="stPlotlyChart"]{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--panel)}
[data-testid="stAlert"]{background:var(--panel2)!important;color:var(--text)!important;border:1px solid var(--line)!important}
[data-testid="stAlert"] p{color:var(--text)!important}
.st-key-theme_control{position:fixed!important;top:24px;left:190px;z-index:1002;width:130px!important;background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:5px 12px!important;box-shadow:0 5px 22px #0002}
.st-key-theme_control label p{font-size:12px!important;white-space:nowrap}.st-key-theme_control>div{gap:0!important}
.brand-mark{position:fixed;left:24px;top:20px;width:140px;height:100px;border-radius:14px;background:#fff;overflow:hidden;box-shadow:0 5px 30px #0002;z-index:1001}
.brand-mark img{width:140px;height:140px;object-fit:contain;transform:translateY(-14px)}
.flag-layer{position:fixed;pointer-events:none;z-index:0;opacity:OPACITY;filter:saturate(.9);width:510px;mask-image:linear-gradient(135deg,#000,transparent 96%)}
.flag-layer img{width:100%;height:auto}.flag-iran{top:75px;left:-80px;transform:rotate(-17deg)}.flag-egypt{top:220px;left:48%;transform:rotate(13deg);width:460px;opacity:EGYPTOPACITY}
.eyebrow{font-size:11px;letter-spacing:1px;color:var(--accent);font-weight:700;margin-bottom:6px}
.hero-lead{font-size:14px;color:var(--muted);margin:9px 0 22px}
.country-row{display:flex;gap:12px;align-items:center;justify-content:flex-start;direction:rtl;margin:13px 0 18px}
.country-name{display:flex;gap:8px;align-items:center;padding:5px 12px;border:1px solid var(--line);border-radius:30px;background:var(--panel);font-size:12px}.country-name img{width:25px;height:17px;object-fit:cover;border-radius:3px}
.estimate-notice{background:var(--redbg);border:1px solid color-mix(in srgb,var(--red) 35%,transparent);border-right:4px solid var(--red);border-radius:12px;padding:13px 17px;color:var(--text);font-size:13px;line-height:1.95;margin:16px 0 24px;text-align:right!important;direction:rtl!important}.estimate-notice strong,.estimated{color:var(--red)!important;font-weight:700!important}
.kpi{border:1px solid var(--line);background:var(--panel);border-radius:14px;padding:17px 18px;min-height:110px;margin:8px 0 15px}.kpi .label{font-size:11px;color:var(--muted);margin-bottom:10px}.kpi .value{font-size:25px;font-weight:700;direction:ltr;text-align:right;color:var(--text)}.kpi .sub{font-size:10px;color:var(--muted);margin-top:7px}
.table-scroll{overflow:auto;max-height:460px;border:1px solid var(--line);border-radius:12px;margin:12px 0 20px;background:var(--panel)}
.data-table{width:100%;border-collapse:collapse;direction:rtl;font-size:12px;white-space:nowrap}.data-table th{background:var(--panel2);color:var(--muted);padding:13px 15px;text-align:right;position:sticky;top:0;z-index:1;border-bottom:1px solid var(--line)}.data-table td{padding:12px 15px;text-align:right;border-bottom:1px solid var(--line);color:var(--text)}.data-table tr:last-child td{border-bottom:0}.data-table tr:hover{background:var(--panel2)}.data-table bdi{unicode-bidi:isolate}
.answer-box{padding:17px 20px;border:1px solid var(--line);border-right:3px solid var(--accent);border-radius:12px;background:var(--panel);line-height:2;font-size:14px;white-space:pre-line;margin:12px 0}
.faculty-footer{border-top:1px solid var(--line);margin:42px 0 0;padding:23px 0 10px;text-align:center;font-size:15px;line-height:2.1;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px 18px;direction:rtl}.faculty-footer a{color:var(--muted)!important;text-decoration:none;font-weight:500}.faculty-footer a:hover{color:var(--accent)!important}.footer-credit{font-size:14px;color:var(--muted)}.footer-divider{height:18px;border-left:1px solid var(--line)}
a{color:var(--accent)!important} code{direction:ltr;unicode-bidi:isolate}
@media(max-width:800px){[data-testid="stMainBlockContainer"]{padding:8.5rem 1rem 1rem!important}h1{font-size:1.8rem!important}.brand-mark{width:112px;height:82px;top:-99px}.brand-mark img{width:112px;height:112px;transform:translateY(-10px)}.st-key-theme_control{left:144px;top:20px;width:125px!important}.flag-layer{width:310px}.flag-egypt{left:40%;top:250px}.stTabs [data-baseweb="tab-list"]{gap:19px}.kpi{min-height:95px}.data-table{font-size:11px}}
.eyebrow,.hero-lead,.kpi .label,.kpi .sub{text-align:right}
.faculty-footer .footer-credit{font-family:"Vazirmatn",Tahoma,sans-serif!important}
.footer-credit a{text-decoration:underline!important;text-decoration-style:dotted!important;text-underline-offset:4px}
@media(max-width:800px){.faculty-footer{gap:8px}.footer-divider{display:none}.footer-credit{width:100%}}
[data-baseweb="select"]>div>div{background:var(--input)!important}
@media(max-width:800px){[data-testid="stSidebar"][data-collapsed="true"]{display:none!important}[data-testid="stSidebar"][data-collapsed="false"]{position:fixed!important;right:0!important;left:auto!important;transform:none!important;width:300px!important;max-width:85vw!important}.brand-mark{top:20px!important;left:16px!important}.brand-mark img{width:112px!important;height:112px!important}}
</style>'''
 css=css.replace('FONTFACES',font_faces()).replace('TOKENS',variables).replace('SCHEME','dark' if dark else 'light').replace('EGYPTOPACITY','.25' if dark else '.14').replace('OPACITY','.30' if dark else '.18')
 direction='rtl' if language()=='fa' else 'ltr';align='right' if language()=='fa' else 'left'
 override='''
.st-key-theme_control{width:265px!important;border-radius:16px}
.st-key-theme_control [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:12px!important;direction:ltr}
.st-key-theme_control [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important}
[data-testid="stMain"], [data-testid="stSidebar"],.data-table,.country-row,.faculty-footer{direction:DIR!important}
h1,h2,h3,h4,h5,h6,p,label,li,summary,input,textarea,select,[data-testid="stCaptionContainer"],.eyebrow,.hero-lead,.kpi .label,.kpi .sub,.kpi .value,.data-table th,.data-table td,.estimate-notice,[role="option"]{text-align:ALIGN!important}
h1,h2,h3,h4,h5,h6,p,label,li,summary,input,textarea,select{direction:DIR!important}
.estimate-notice,[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"],[data-testid="stCaptionContainer"],input,textarea,[data-baseweb="select"]>div,[role="option"]{direction:DIR!important}
.answer-box{direction:DIR!important;text-align:ALIGN!important}
[data-baseweb="slider"]{direction:ltr!important}
[data-testid="stCheckbox"] label:has(input[role="switch"])>div:not([data-testid]){direction:ltr!important}
.faculty-footer,.faculty-footer p{text-align:center!important}
@media(max-width:800px){.st-key-theme_control{left:144px!important;right:auto!important;width:236px!important;padding:5px 8px!important}.st-key-theme_control label p{font-size:11px!important}.st-key-theme_control [data-testid="stColumn"]:first-child{flex:1.25 1 0!important}}
'''.replace('DIR',direction).replace('ALIGN',align)
 if language()=='en':override+='''
[data-testid="stAppViewContainer"]{flex-direction:row!important}
[data-testid="stSidebar"]{left:0!important;right:auto!important;border-left:0;border-right:1px solid var(--line)}
[data-testid="stSidebar"]>div{padding-top:9rem!important}
h1,h2,h3,h4,h5,h6{font-family:"Vazirmatn",Arial,sans-serif!important;direction:ltr!important;line-height:1.4!important}
.st-key-theme_control{left:auto!important;right:24px!important}
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"]{left:16px!important;right:auto!important}
.estimate-notice,.answer-box{border-right:1px solid var(--line);border-left:4px solid var(--red)}
@media(max-width:800px){[data-testid="stSidebar"][data-collapsed="false"]{left:0!important;right:auto!important}.st-key-theme_control{left:144px!important;right:auto!important}}
'''
 override+='''
[data-testid="stMainBlockContainer"]{padding-top:1.8rem!important}
.st-key-topbar{position:relative!important;height:122px!important;min-height:122px!important;margin-bottom:4px!important;gap:0!important}
.st-key-theme_control{position:absolute!important;top:0!important;left:156px!important;right:auto!important;width:165px!important;padding:8px 12px!important;z-index:10!important;border-radius:16px!important}
.st-key-theme_control>div{gap:6px!important}
.brand-mark{position:absolute!important;top:0!important;left:0!important;right:auto!important;z-index:10!important}
[data-testid="stSidebar"]>div{padding-top:1.8rem!important}
@media(max-width:800px){[data-testid="stMainBlockContainer"]{padding-top:16px!important}.st-key-topbar{height:108px!important;min-height:108px!important}.st-key-theme_control{left:128px!important;right:auto!important;width:150px!important;padding:6px 8px!important}.brand-mark{top:0!important;left:0!important;right:auto!important}}
'''
 if language()=='en':override+='''
.brand-mark{left:auto!important;right:0!important}
.st-key-theme_control{left:auto!important;right:156px!important}
@media(max-width:800px){.brand-mark{left:auto!important;right:0!important}.st-key-theme_control{left:auto!important;right:128px!important}}
'''
 override+='''
.st-key-country_actions{direction:COUNTRYDIR!important;justify-content:flex-start!important;gap:12px!important;margin:13px 0 18px!important}
.st-key-country_actions>[data-testid="stElementContainer"]{width:auto!important;flex:0 1 auto!important;max-width:100%!important}
.st-key-country_actions>[data-testid="stElementContainer"]:first-child{min-height:36px!important}
.st-key-country_actions .country-row{margin:0!important}
.st-key-country_actions [data-testid="stDownloadButton"] button{border-radius:30px!important;min-height:34px!important;padding:5px 13px!important;background:var(--panel)!important;font-size:12px!important}
@media(max-width:600px){.st-key-country_actions>[data-testid="stElementContainer"]:first-child{flex-basis:100%!important}.st-key-country_actions [data-testid="stDownloadButton"] button{white-space:normal!important;max-width:100%!important}}
'''.replace('COUNTRYDIR','rtl' if language()=='fa' else 'ltr')
 css=css.replace('</style>',override+'</style>')
 return css,tokens
def decorate():return f'<div class="flag-layer flag-iran"><img src="{data_url("ir.svg")}" alt=""></div><div class="flag-layer flag-egypt"><img src="{data_url("eg.svg")}" alt=""></div><div class="brand-mark"><a href="https://mst.aut.ac.ir" target="_blank" rel="noopener noreferrer"><img src="{data_url("university_logo.jpg")}" alt="لوگوی دانشکده مدیریت، علم و فناوری دانشگاه صنعتی امیرکبیر"></a></div>'
def countries():return '<div class="country-row">'+''.join(f'<span class="country-name"><img src="{data_url(c+".svg")}" alt="{n}">{n}</span>' for c,n in [('ir',country('IRN')),('eg',country('EGY'))])+'</div>'
def table(headers,rows,red_cells=None):
 red_cells=red_cells or set();parts=['<div class="table-scroll"><table class="data-table"><thead><tr>']
 display=lambda v:fa(v) if language()=='fa' else str(v)
 parts+=['<th>'+html.escape(display(h))+'</th>' for h in headers];parts.append('</tr></thead><tbody>')
 for i,row in enumerate(rows):
  parts.append('<tr>')
  for j,v in enumerate(row):parts.append('<td'+(' class="estimated"' if (i,j) in red_cells else '')+'><bdi>'+html.escape(display('—' if v is None else v))+'</bdi></td>')
  parts.append('</tr>')
 parts.append('</tbody></table></div>');return ''.join(parts)
def kpi(label,value,sub='',estimated=False):return f'<div class="kpi"><div class="label">{html.escape(label)}</div><div class="value {"estimated" if estimated else ""}">{html.escape(str(value))}</div><div class="sub">{html.escape(sub)}</div></div>'
def footer():
 faculty=L('دانشکده مدیریت، علم و فناوری، دانشگاه صنعتی امیرکبیر','Faculty of Management, Science and Technology, Amirkabir University of Technology')
 credit=L('طراحی و پیاده‌سازی توسط','Designed and implemented by');nima=L('نیما علاقه‌بند','Nima Alagheband');amir=L('و امیرعباس عموزاده','and Amirabbas Amouzadeh')
 return f'<div class="faculty-footer"><a href="https://mst.aut.ac.ir" target="_blank" rel="noopener noreferrer">{faculty}</a><span class="footer-divider" aria-hidden="true"></span><span class="footer-credit">{credit} <a href="https://alaghebandnima.ir" target="_blank" rel="noopener noreferrer">{nima}</a> {amir}</span></div>'
