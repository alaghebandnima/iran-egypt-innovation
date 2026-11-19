"""Responsive source-coverage cards; the desktop heatmap remains unchanged."""
import html
from i18n import L,language,country,metric_name


def badge_colors(count,total):
    fraction=max(0,min(1,count/total)) if total else 0
    rgb=tuple(round(a+(b-a)*fraction) for a,b in zip((239,247,251),(17,83,116)))
    def luminance(values):
        values=[v/255 for v in values]
        return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),values))
    lum=luminance(rgb)
    dark=(0,0,0)
    ink='#ffffff' if 1.05/(lum+.05)>=(lum+.05)/(luminance(dark)+.05) else '#000000'
    return '#%02x%02x%02x'%rgb,ink


def coverage_cards(catalog,counts,total=20):
    def digits(n):
        text=str(n)
        return text.translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')) if language()=='fa' else text
    pieces=['''<style>
.st-key-coverage_mobile{display:none!important}
@media(max-width:800px){
 .st-key-coverage_desktop{display:none!important}
 .st-key-coverage_mobile{display:flex!important;min-width:0!important}
 .coverage-cards{width:100%;min-width:0}
 .coverage-cards[lang="fa"] .coverage-guide{text-align:right!important;direction:rtl!important}
 .coverage-guide{color:var(--muted);font-size:12px;line-height:1.9;margin-bottom:14px}
 .coverage-card{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:15px;margin-bottom:12px;min-width:0}
 .coverage-card-name{font-size:13px;line-height:1.9;font-weight:700;color:var(--text);overflow-wrap:anywhere;margin-bottom:12px}
 .coverage-badges{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
 .coverage-badge{background:var(--coverage-bg);color:var(--coverage-ink);border-radius:11px;padding:11px 8px;display:flex;flex-direction:column;align-items:center;gap:5px;min-width:0;text-align:center}
 .coverage-country{font-size:12px;font-weight:600}
 .coverage-count{font-size:12px;font-weight:700;line-height:1.7;white-space:normal}
}
</style><div class="coverage-cards">''']
    pieces.append('<div class="coverage-guide">'+L('تعداد سال‌های دارای مقدار منبع، پیش از تخمین پروژه. رنگ پررنگ‌تر یعنی پوشش بیشتر.','Years with published source values, before project estimation. Darker blue means greater coverage.')+'</div>')
    pieces[0]=pieces[0].replace('<div class="coverage-cards">','<div class="coverage-cards" lang="'+language()+'">')
    for metric,row in zip(catalog,counts):
        pieces.append('<article class="coverage-card" data-indicator="'+html.escape(metric['code'],quote=True)+'"><div class="coverage-card-name">'+html.escape(metric_name(metric))+'</div><div class="coverage-badges">')
        for code,count in zip(('IRN','EGY'),row):
            background,ink=badge_colors(count,total)
            value=L(f'{digits(count)} از {digits(total)} سال',f'{count} of {total} years')
            label=country(code)+': '+value
            pieces.append(f'<div class="coverage-badge" data-country="{code}" data-years="{count}" style="--coverage-bg:{background};--coverage-ink:{ink}" aria-label="{html.escape(label,quote=True)}"><span class="coverage-country">{html.escape(country(code))}</span><span class="coverage-count">{value}</span></div>')
        pieces.append('</div></article>')
    pieces.append('</div>')
    return ''.join(pieces)
