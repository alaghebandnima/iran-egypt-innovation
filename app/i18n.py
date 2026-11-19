"""Session-local presentation language; source values and indicator codes never change."""
from contextvars import ContextVar

_language=ContextVar('dashboard_language',default='fa')
def set_language(language):_language.set('en' if language=='en' else 'fa')
def language():return _language.get()
def L(persian,english):return english if language()=='en' else persian
def country(code):return ({'IRN':'Iran','EGY':'Egypt','WLD':'World','BOTH':'Both countries'} if language()=='en' else {'IRN':'ایران','EGY':'مصر','WLD':'جهان','BOTH':'هر دو کشور'}).get(code,code)
METHOD_EN={'weighted':'Distance-weighted average','local_trend':'Regularized local trend','trend_curve':'Regularized trend curve','state_space':'Latent state: Kalman filter and smoother','derived':'Calculated from estimated inputs'}
KIND_EN={'internal':'Internal gap','leading':'Before the first available year','trailing':'After the last available year'}
NAMES_EN={'LF_GENDER_GAP':'Labor force participation gap: total minus female','ARTICLES_PM':'Scientific and technical articles per million people','PATENT_NR_R':'Nonresident-to-resident patent application ratio','PATENTS_PM':'Resident patent applications per million people'}
NOTES_EN={
 'IP.PAT.RESD':'Application counts do not measure patent quality or patents granted.',
 'IP.JRN.ARTC.SC':'Article counts do not directly measure quality, citations or commercialization.',
 'GGXWDG_NGDP':'IMF WEO October 2026. The API does not establish the exact boundary between actuals and estimates. Gross general government debt differs from net debt and external debt.',
 'NY.GDP.PCAP.PP.CD':'Suitable for level comparisons; inflation affects the time trend.',
 'LF_GENDER_GAP':'Total minus female participation is not a male–female participation gap.',
 'ARTICLES_PM':'Same-country, same-year inputs. A missing or zero denominator remains unavailable.',
 'PATENT_NR_R':'Same-country, same-year inputs. A missing or zero denominator remains unavailable.',
 'PATENTS_PM':'Same-country, same-year inputs. A missing or zero denominator remains unavailable.',
 'IT.NET.BBND.P2':'Subscriptions are not the same as individual subscribers.',
 'IT.CEL.SETS.P2':'Multiple SIM cards per person can produce values above 100.',
 'IT.NET.USER.ZS':'Measures digital adoption, not Internet quality or speed.',
 'EG.ELC.LOSS.ZS':'Includes some nontechnical losses as well as network losses.',
 'IT.MLT.MAIN.P2':'A traditional infrastructure measure without a universally desirable direction.',
 'EG.ELC.ACCS.ZS':'Access does not establish reliability or absence of outages.',
 'IT.NET.SECR.P6':'Hosting location and certificate registration affect this indicator.',
 'NY.GDP.MKTP.PP.CD':'International dollars are not the same unit as US dollars.',
 'NY.GDP.PCAP.PP.KD':'Constant 2021 international dollars; suitable for real trends.',
 'NY.GDP.PCAP.CD':'Average output per person, not the income of each individual.',
 'CM.MKT.LCAP.GD.ZS':'Market coverage and liquidity should also be considered.',
 'NV.SRV.TOTL.ZS':'Not all services are knowledge-intensive.',
 'NV.IND.MANF.ZS':'Measures the size of the manufacturing sector.',
 'NE.TRD.GNFS.ZS':'Exports plus imports; economic size also affects this openness measure.',
 'GGXCNL_NGDP':'IMF WEO October 2026. The exact actual/estimate boundary is not identified by the API. Positive values denote net lending; negative values denote net borrowing.',
 'NE.GDI.TOTL.ZS':'Total investment, not specifically technology investment.',
 'FP.CPI.TOTL.ZG':'Annual average inflation is different from year-end inflation.',
 'NY.GDP.MKTP.CD':'Affected by inflation and exchange rates; do not use it as real growth.',
 'SP.POP.TOTL':'Use the same year when constructing per-capita indicators.',
 'NY.GDP.TOTL.RT.ZS':'Provides context on resource dependence and economic structure.',
 'NY.GDP.MKTP.KD.ZG':'National accounts measure; fiscal calendars may differ between countries.',
 'NY.GDP.PCAP.KD.ZG':'Real per-capita growth differs from nominal growth.',
 'PA.NUS.FCRF':'The official exchange rate may differ from the rate actually available.',
 'BX.KLT.DINV.WD.GD.ZS':'Can be negative; inflows alone do not establish technology transfer.',
 'SL.UEM.1524.ZS':'Young people outside the labor force are excluded from the denominator.',
 'SL.UEM.TOTL.ZS':'The denominator is the labor force, not the total population.',
 'SE.TER.ENRR.FE':'Gross enrollment ratio, not the proportion of students who are female.',
 'SL.UEM.NEET.ZS':'Consult metadata for the definition and age coverage.',
 'SL.TLF.CACT.FE.ZS':'ILO modeled estimate; provides context on talent participation.',
 'SL.TLF.CACT.ZS':'ILO modeled estimate, not a direct survey observation.',
 'SE.TER.ENRR':'Gross enrollment ratios can exceed 100%.',
 'SL.EMP.TOTL.SP.ZS':'ILO modeled estimate; does not measure job quality.',
 'IP.PAT.NRES':'May reflect market attractiveness for foreign IP protection; does not measure domestic ownership.',
 'GII.RANK':'This dataset contains 2020–2024 only. Rank is ordinal and affected by changes in methodology and country coverage. Rank differs from score.',
 'TX.MNF.TECH.ZS.UN':'Broader than high-technology exports; the two measures must not be added.',
 'SP.DYN.LE00.IN':'Health outcome; does not isolate the effect of innovation.',
 'EN.GHG.CO2.PC.CE.AR5':'New emissions series; not automatically spliced to the discontinued series.',
 'EG.FEC.RNEW.ZS':'Final energy consumption, not electricity alone.',
 'EG.ELC.RNEW.ZS':'Includes hydropower; do not add it to final energy consumption.',
 'SP.POP.1564.TO.ZS':'A demographic opportunity does not guarantee employment.',
 'SP.URB.TOTL.IN.ZS':'National definitions of urban areas differ.',
 'SH.XPD.CHEX.GD.ZS':'Health input, not health quality or outcomes.',
 'EG.USE.PCAP.KG.OE':'An energy input measure; higher is not necessarily better.',
 'SP.POP.DPND':'Age-based ratio, not actual economic dependency.',
}
EVENTS_EN={
 ('IRN',2016):'Oil-led growth after restrictions eased; context for GDP changes',
 ('IRN',2018):'Reimposition of US sanctions',
 ('EGY',2016):'Change in Egypt’s exchange-rate regime',
 ('BOTH',2020):'Pandemic and disruption to the global economy',
 ('EGY',2024):'Renewed transition to a flexible exchange-rate regime',
}
def metric_name(m):return NAMES_EN.get(m['code'],m.get('name_en',m['code'])) if language()=='en' else m['name_fa']
def metric_note(m):return m.get('note_en',NOTES_EN.get(m['code'],m.get('definition',''))) if language()=='en' else m['note_fa']
def method_name(code):
 if language()=='en':return METHOD_EN.get(code,code)
 from estimation import METHOD_NAMES
 return METHOD_NAMES.get(code,code)
def source_status(row):
 if row.get('is_estimated'):return L('تخمین پروژه','Project estimate')
 if row['value'] is None:return L('موجود نیست','Unavailable')
 if row.get('source_is_estimated'):return L('برآورد منتشرشدهٔ سوئید','Published SWIID estimate')
 return L('منتشرشده در منبع','Published source value')
