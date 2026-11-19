# Data and methods

## Scope

Iran (`IRN`) and Egypt (`EGY`), 2005–2024 inclusive. The active catalog contains 51 source indicators and four calculated indicators. Definitions, units, original source URLs and formulas are in `data/panel_2005_2024/metric_dictionary.csv` and `dashboard_data.json`.

## Providers

- **World Bank WDI:** 47 source indicators. [World Bank Open Data](https://data.worldbank.org/). Consult indicator metadata and applicable provider terms.
- **IMF WEO:** gross general-government debt and the fiscal balance. Gross debt is not net debt or external debt. The release used by this project is documented in the indicator dictionary. [IMF DataMapper](https://www.imf.org/external/datamapper/).
- **WIPO:** historical Global Innovation Index rank. Rank is ordinal; a lower number is better, and changes do not represent equal-sized capacity changes. [Global Innovation Index](https://www.wipo.int/global_innovation_index/).
- **SWIID 9.92:** disposable-income Gini. Published SWIID values are themselves source estimates, not independent annual surveys. Project-filled years are separately flagged. Cite: Solt, Frederick. 2020. “Measuring Income Inequality Across Countries and Over Time: The Standardized World Income Inequality Database.” Social Science Quarterly 101(3):1183–1199. SWIID Version 9.92, April 2026. [Source](https://fsolt.org/swiid/) · [Dataset and CC0 terms](https://fsolt.org/swiid/swiid_downloads/).

`data/raw/` contains curated, active-series snapshots, not the providers' entire original databases. The included snapshot has a fixed release vintage; it is not a live feed.

## Missing values and validation

The general policy retains indicators with at most five missing years in each country. Historical innovation rank, high-technology exports and R&D expenditure are explicit exceptions. Unpublished innovation ranks remain unavailable.

Weighted interpolation, a regularized local trend, a regularized trend curve and a level/slope latent-state model are compared using artificial missingness. Known values are hidden, each candidate is fitted without those values, and errors are checked against the hidden truth. Selection depends on country, indicator, gap direction and length; unmatched shorter validation gaps are labelled. Nested/outer validation results are included. Error summaries are not accuracy percentages or guarantees for every gap.

The completed panel contains **69 project estimates of source-series values and six calculations using estimated inputs**. Original values are retained. The four calculated indicators are articles per million people, resident patent applications per million people, the nonresident-to-resident application ratio, and total-minus-female labor-force participation. The last is not a male-minus-female gap. Missing or zero denominators are not silently replaced.

## Ollama and numerical provenance

The 4B language model is pre-trained; it is not trained on the artificial-missingness windows. Python handles numerical calculations and the statistical estimator. Ollama writes an explanation from selected qualitative evidence; numeric claims, language, structure and evidence identifiers are checked. The displayed final answer combines computed values with the explanation. Rejected output produces a warning. The model does not browse the web, and checks cannot establish factual or causal correctness of every interpretation.

## Reproduction

Run the tests and active-data audit first. `scripts/build_panel20.py` rebuilds the active source snapshot; `scripts/build_estimates.py` recomputes filled values and validation records. `scripts/short_report.py` regenerates HTML reports. These modify generated artifacts in the checkout, so keep a clean version before rebuilding. Excel workbooks are included release snapshots.
