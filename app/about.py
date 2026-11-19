"""Bilingual, self-contained project and course credits."""
from html import escape
from i18n import L,language
from presentation import data_url


def about_page():
 def image(file,alt,cls=''):
  return f'<img class="{cls}" src="{data_url("about/"+file)}" alt="{escape(alt)}">'
 def link(text,url):
  return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{escape(text)}</a>'
 def person(file,name,role,degree='',kind='',url=None):
  title=link(name,url) if url else escape(name)
  return f'<article class="about-person {kind}">{image(file,name,"about-portrait")}<div class="about-person-copy"><div class="about-role">{escape(role)}</div><div class="about-name">{title}</div>'+ (f'<div class="about-degree">{escape(degree)}</div>' if degree else '')+'</div></article>'
 faculty=L('دانشکده مدیریت، علم و فناوری','Faculty of Management, Science and Technology')
 university=L('دانشگاه صنعتی امیرکبیر (پلی‌تکنیک تهران)','Amirkabir University of Technology (Tehran Polytechnic)')
 css='''<style>
.about-page{direction:DIR;text-align:ALIGN;color:var(--text);margin-top:22px;--about-gold:#d9b86f}
.about-page *{box-sizing:border-box}
.about-hero{display:grid;grid-template-columns:1.65fr 1fr;border:1px solid var(--line);border-radius:24px;overflow:hidden;background:linear-gradient(125deg,var(--panel),var(--panel2));min-height:220px}
.about-intro{padding:28px 30px;align-self:center}.about-kicker{font-size:11px;letter-spacing:.7px;color:var(--accent);margin-bottom:12px;font-weight:700}
.about-title{font-family:"BTitr","Vazirmatn",sans-serif;font-size:25px;line-height:1.7;margin-bottom:10px;color:var(--text)}
.about-description{font-size:13px;color:var(--muted);line-height:2;max-width:640px}
.about-building{position:relative;min-height:220px;overflow:hidden}.about-building img{width:100%;height:100%;position:absolute;inset:0;object-fit:cover;object-position:center}.about-building:after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,#071a3055,transparent)}
.about-course{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:20px 0 14px;font-size:12px;color:var(--muted)}.about-course strong{color:var(--text);font-weight:600}.about-dot{width:4px;height:4px;border-radius:50%;background:var(--about-gold)}
.about-faculty{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:14px;align-items:stretch}
.about-person{border:1px solid var(--line);border-radius:20px;background:color-mix(in srgb,var(--panel) 92%,transparent);padding:24px 16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:15px;text-align:center}
.about-portrait{width:108px;height:108px;object-fit:cover;border-radius:50%;box-shadow:0 0 0 5px var(--panel2),0 0 0 6px var(--line);display:block;flex-shrink:0}
.about-person.professor{background:linear-gradient(145deg,var(--panel2),var(--panel));border-color:color-mix(in srgb,var(--about-gold) 55%,var(--line))}.professor .about-portrait{width:150px;height:150px;box-shadow:0 0 0 5px var(--panel),0 0 0 6px var(--about-gold)}
.about-role{font-size:11px;color:var(--accent);margin-bottom:6px}.professor .about-role{color:var(--about-gold)}.about-name{font-size:16px;line-height:1.9;font-weight:700}.about-degree{font-size:12px;line-height:1.9;color:var(--muted);margin-top:4px}.about-page a{color:inherit!important;text-decoration:none!important}.about-page a:hover{color:var(--accent)!important;text-decoration:underline!important;text-underline-offset:5px}.about-page a:focus-visible{outline:2px solid var(--accent);outline-offset:5px;border-radius:3px}
.about-section-label{font-size:12px;font-weight:700;margin:22px 0 12px;color:var(--muted)}
.about-creators{display:grid;grid-template-columns:1fr 1fr;gap:14px}.about-creators .about-person{flex-direction:row;justify-content:flex-start;padding:20px;gap:20px;text-align:ALIGN}.about-creators .about-portrait{width:76px;height:76px}.about-creators .about-name{font-size:15px}
.about-institution{padding:20px 8px 4px;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:9px 16px;font-size:12px;line-height:1.9;color:var(--muted)}
.about-page[lang="en"] .about-title{font-family:"Vazirmatn",Arial,sans-serif;font-size:23px;font-weight:700;line-height:1.5}
@media(max-width:1050px){.about-title{font-size:22px}.about-intro{padding:22px}.about-faculty{gap:10px}.about-person{padding:22px 10px}.about-name{font-size:14px}.about-creators .about-person{gap:14px;padding:16px}}
@media(max-width:650px){.about-hero{grid-template-columns:1fr}.about-building{min-height:145px;grid-row:1}.about-intro{padding:22px}.about-title{font-size:22px}.about-faculty{grid-template-columns:1fr 1fr;gap:12px}.about-person.professor{grid-column:1/-1;flex-direction:row;padding:24px 18px;gap:22px}.professor .about-portrait{width:132px;height:132px}.about-portrait{width:94px;height:94px}.about-person{padding:22px 10px}.about-name{font-size:13px}.professor .about-name{font-size:15px}.about-creators{grid-template-columns:1fr}.about-creators .about-person{padding:20px;gap:18px}.about-description{font-size:12px}.about-course{line-height:1.9}.about-institution{flex-direction:column;gap:4px}.about-institution .about-dot{display:none}}
@media(prefers-reduced-motion:no-preference){.about-person{transition:border-color .2s,box-shadow .2s}.about-person:hover{border-color:var(--accent);box-shadow:0 8px 24px #00000012}}
</style>'''.replace('DIR','rtl' if language()=='fa' else 'ltr').replace('ALIGN','right' if language()=='fa' else 'left')
 intro=L('این پروژه، نظام‌های نوآوری ایران و مصر را در بازهٔ ۲۰۰۵ تا ۲۰۲۴ بررسی می‌کند؛ با کنار هم گذاشتن داده‌های معتبر، روند شاخص‌ها و زمینه‌های تاریخی، تصویری مقایسه‌ای از مسیر فناوری و نوآوری دو کشور ارائه می‌دهد.','This project examines the innovation systems of Iran and Egypt from 2005 to 2024. It brings together credible data, indicator trends and historical context to compare how technology and innovation have evolved in the two countries.')
 title=L('بررسی نظام‌های نوآوری دو کشور ایران و مصر','A Comparative Study of the Innovation Systems of Iran and Egypt')
 professor=person('1.png',L('خانم دکتر سارا سلیمی نمین','Dr. Sara Salimi Namin'),L('استاد درس','Course instructor'),kind='professor')
 assistants=''.join([person('2.png',L('نازنین ناظم','Nazanin Nazem'),L('استادیار درس','Teaching assistant')),person('3.png',L('ارسلان جباری','Arsalan Jabbari'),L('استادیار درس','Teaching assistant'))])
 creators=''.join([person('4.png',L('نیما علاقه‌بند','Nima Alagheband'),L('طراحی و اجرای پروژه','Project design and implementation'),L('دانشجوی کارشناسی ارشد فناوری اطلاعات — گرایش تجارت الکترونیکی','M.Sc. student in Information Technology — E-Commerce'),url='https://alaghebandnima.ir'),person('5.png',L('امیرعباس عموزاده','Amirabbas Amouzadeh'),L('طراحی و اجرای پروژه','Project design and implementation'),L('دانشجوی کارشناسی ارشد مدیریت کسب‌وکار — گرایش فناوری','MBA student — Technology Management'))])
 return css+f'<section class="about-page" lang="{language()}" aria-label="{L("درباره ما","About us")}"><div class="about-hero"><div class="about-intro"><div class="about-kicker">{L("پروژهٔ درس مدیریت فناوری و نوآوری","TECHNOLOGY AND INNOVATION MANAGEMENT · COURSE PROJECT")}</div><div class="about-title" role="heading" aria-level="2">{title}</div><div class="about-description">{intro}</div></div><div class="about-building">{image("daneshkade.jpg",faculty)}</div></div><div class="about-course"><strong>{L("مدیریت فناوری و نوآوری","Technology and Innovation Management")}</strong><span class="about-dot" aria-hidden="true"></span><span>{L("استاد و همراهان آموزشی","Course instructor and teaching assistants")}</span></div><div class="about-faculty">{professor}{assistants}</div><div class="about-section-label">{L("اعضای پروژه","PROJECT TEAM")}</div><div class="about-creators">{creators}</div><div class="about-institution">{link(faculty,"https://mst.aut.ac.ir")}<span class="about-dot" aria-hidden="true"></span>{link(university,"https://aut.ac.ir")}</div></section>'
