"""
The Price of Growth — Streamlit Data Story
How US Sectors Create and Destroy Value

Interactive dashboard exploring value creation across 94 US industries
using Aswath Damodaran's January 2026 dataset.

Narrative arc follows a Freytag pyramid across five charts.

Author: Daniel Sigerist | HSLU DVIZ MM F2601 | 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Price of Growth",
    page_icon="📈",
    layout="wide",
)

# ── Global CSS: animations & polish ─────────────────────────────────────────
st.markdown("""
<style>
/* ── 1. Keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes accentGrow {
    from { border-left-width: 0; padding-left: 0; opacity: 0; }
    to   { border-left-width: 4px; padding-left: 12px; opacity: 1; }
}

/* ── 2. Page entry ── */
.main .block-container {
    animation: fadeInUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* ── 3. Chart containers: glow on hover ── */
.stPlotlyChart {
    transition: box-shadow 0.40s ease, transform 0.28s ease;
    border-radius: 12px;
}
.stPlotlyChart:hover {
    box-shadow: 0 8px 40px rgba(0, 114, 178, 0.30), 0 2px 12px rgba(86,180,233,0.10);
    transform: translateY(-3px);
}

/* ── 4. Section headings ── */
h3 {
    border-left: 4px solid #0072B2 !important;
    padding-left: 12px !important;
    color: #c8d0dc !important;
    font-family: Georgia, 'Times New Roman', serif !important;
    letter-spacing: 0.4px !important;
    animation: accentGrow 0.5s ease-out both !important;
}
h2 {
    color: #e8eaf0 !important;
    font-family: Georgia, 'Times New Roman', serif !important;
    letter-spacing: 0.3px !important;
}

/* ── 5. Markdown text sections ── */
.stMarkdown {
    animation: fadeIn 0.75s ease-out both;
}
.stMarkdown p {
    line-height: 1.75 !important;
    color: #c8d0dc !important;
    font-size: 0.97rem !important;
}

/* ── 6. Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,114,178,0.30) !important;
    margin: 1.4rem 0 !important;
}

/* ── 7. Custom scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a2035; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #0072B2, #56B4E9);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: #56B4E9; }

/* ── 8. Bold & emphasis ── */
strong {
    color: #e8eaf0 !important;
    font-weight: 700 !important;
}
em { color: #56B4E9 !important; font-style: normal !important; }

/* ── 9. Selectbox / widget labels ── */
label { color: #8a9bae !important; font-size: 0.87rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
DATA = BASE / "data"
AVATAR_PATH = BASE / "assets" / "github_avatar.png"


# ══════════════════════════════════════════════════════════════════════════════
#  DATA LOADING & PREPARATION
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Load and clean all seven Damodaran CSV files. Cached for performance."""

    # ── 1. Load datasets ─────────────────────────────────────────────────────
    dollar = pd.read_csv(DATA / "DollarUS.csv")
    wacc   = pd.read_csv(DATA / "wacc.csv")
    eva    = pd.read_csv(DATA / "EVA.csv")
    roe    = pd.read_csv(DATA / "roe.csv")
    div    = pd.read_csv(DATA / "divfcfe.csv")
    betas  = pd.read_csv(DATA / "betas.csv")
    growth = pd.read_csv(DATA / "fundgrowth.csv")

    # ── 2. Clean column names ────────────────────────────────────────────────
    for df in [dollar, wacc, eva, roe, div, betas]:
        df.columns = [c.strip().replace('  ', ' ') for c in df.columns]

    # ── 3. Parse growth columns (already stored as decimals in CSV) ─────────
    for col in ['ROC', 'Reinvestment Rate', 'Expected Growth in EBIT']:
        growth[col] = pd.to_numeric(growth[col], errors='coerce')

    # ── 4. GICS-based sector mapping (94 industries → 11 sectors) ────────────
    SECTORS = {
        'Technology': [
            'Semiconductor', 'Semiconductor Equip',
            'Software (System & Application)', 'Software (Entertainment)',
            'Software (Internet)', 'Computers/Peripherals',
            'Computer Services', 'Electronics (General)',
            'Electronics (Consumer & Office)', 'Telecom. Equipment',
        ],
        'Communication Services': [
            'Broadcasting', 'Cable TV', 'Entertainment',
            'Publishing & Newspapers', 'Telecom (Wireless)',
            'Telecom. Services', 'Advertising',
        ],
        'Healthcare': [
            'Drugs (Biotechnology)', 'Drugs (Pharmaceutical)',
            'Healthcare Products', 'Healthcare Support Services',
            'Heathcare Information and Technology',
            'Hospitals/Healthcare Facilities',
        ],
        'Financials': [
            'Bank (Money Center)', 'Banks (Regional)',
            'Brokerage & Investment Banking',
            'Financial Svcs. (Non-bank & Insurance)',
            'Insurance (General)', 'Insurance (Life)',
            'Insurance (Prop/Cas.)',
            'Investments & Asset Management', 'Reinsurance',
        ],
        'Energy': [
            'Oil/Gas (Integrated)', 'Oil/Gas (Production and Exploration)',
            'Oil/Gas Distribution', 'Oilfield Svcs/Equip.',
            'Coal & Related Energy', 'Green & Renewable Energy',
        ],
        'Consumer Discretionary': [
            'Auto & Truck', 'Auto Parts', 'Apparel',
            'Hotel/Gaming', 'Restaurant/Dining', 'Recreation',
            'Retail (General)', 'Retail (Automotive)',
            'Retail (Building Supply)', 'Retail (Special Lines)',
            'Retail (Distributors)', 'Shoe', 'Education',
        ],
        'Consumer Staples': [
            'Beverage (Alcoholic)', 'Beverage (Soft)',
            'Food Processing', 'Food Wholesalers',
            'Household Products', 'Retail (Grocery and Food)',
            'Tobacco', 'Farming/Agriculture',
        ],
        'Industrials': [
            'Aerospace/Defense', 'Air Transport', 'Building Materials',
            'Business & Consumer Services', 'Construction Supplies',
            'Electrical Equipment', 'Engineering/Construction',
            'Environmental & Waste Services', 'Machinery',
            'Office Equipment & Services', 'Packaging & Container',
            'Shipbuilding & Marine', 'Transportation',
            'Transportation (Railroads)', 'Trucking',
            'Diversified', 'Information Services',
        ],
        'Materials': [
            'Chemical (Basic)', 'Chemical (Diversified)',
            'Chemical (Specialty)', 'Metals & Mining',
            'Paper/Forest Products', 'Precious Metals',
            'Rubber& Tires', 'Steel',
        ],
        'Real Estate': [
            'R.E.I.T.', 'Real Estate (Development)',
            'Real Estate (General/Diversified)',
            'Real Estate (Operations & Services)', 'Retail (REITs)',
        ],
        'Utilities': [
            'Power', 'Utility (General)', 'Utility (Water)',
        ],
    }

    SECTOR_MAP = {ind: sector for sector, inds in SECTORS.items() for ind in inds}

    # ── 5. Attach sector labels to every dataset ─────────────────────────────
    for df in [dollar, wacc, eva, roe, div, betas, growth]:
        if 'Industry Name' in df.columns:
            df['Sector'] = df['Industry Name'].map(SECTOR_MAP)

    return dollar, wacc, eva, roe, div, betas, growth, SECTOR_MAP


dollar, wacc, eva, roe, div, betas, growth, SECTOR_MAP = load_data()


# ══════════════════════════════════════════════════════════════════════════════
#  BRANDING HELPER
# ══════════════════════════════════════════════════════════════════════════════

def add_branding(fig, x=0.99, y=1.10, size_x=0.035, size_y=0.05,
                 text_x=0.953, text_y=1.065):
    """Add GitHub avatar + handle to any Plotly figure."""
    if AVATAR_PATH.exists():
        avatar = Image.open(AVATAR_PATH)
        fig.add_layout_image(dict(
            source=avatar, xref='paper', yref='paper',
            x=x, y=y, sizex=size_x, sizey=size_y,
            xanchor='right', yanchor='top', opacity=0.95, layer='above',
        ))
    fig.add_annotation(
        xref='paper', yref='paper', x=text_x, y=text_y,
        text='<b>@Sigerist1505</b>', showarrow=False,
        font=dict(size=10, color='#8a9bae',
                  family='Helvetica, Arial, sans-serif'),
        xanchor='right', yanchor='middle',
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<h1 style="font-family:Georgia,Garamond,serif; font-size:42px;
           letter-spacing:1px; margin-bottom:0">
    The Price of Growth
</h1>
<p style="font-family:Helvetica,Arial,sans-serif; font-size:16px;
          color:#8a9bae; letter-spacing:2px; text-transform:uppercase;
          margin-top:4px">
    How US Sectors Create and Destroy Value
</p>
""", unsafe_allow_html=True)

st.markdown("""
*An exploration of value creation across 94 US industries using
Aswath Damodaran's January 2026 dataset from NYU Stern.*

The story follows a **Freytag pyramid**: tension builds toward a climax in
Chart 3. Charts 1 and 2 set the context, Chart 3 delivers the verdict,
Chart 4 tests whether the market agrees, and Chart 5 resolves the arc by
revealing how value creators allocate their profits.
""")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 1 — SECTOR LANDSCAPE (TREEMAP)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
### Exposition: How big is each sector and who is profitable?

Size encodes market capitalization; color encodes net margin
(diverging scale: orange = negative, blue > 30%).
Gives an immediate sense of scale and profitability across all 94 industries.
""")

# ── 1. Prepare data ──────────────────────────────────────────────────────────
treemap_df = dollar[['Industry Name', 'Market Cap ($ millions)',
                     'Revenues ($ millions)', 'Net Income ( $ millions)']].copy()
treemap_df.columns = ['Industry', 'MarketCap', 'Revenue', 'NetIncome']
treemap_df = treemap_df[treemap_df['MarketCap'] > 0].copy()
treemap_df['NetMargin'] = treemap_df['NetIncome'] / treemap_df['Revenue']

# ── 2. Color scale ───────────────────────────────────────────────────────────
# Colorblind-safe diverging scale (Okabe-Ito inspired: orange → yellow → blue)
COLOR_SCALE = [
    [0.00, '#D55E00'], [0.20, '#E69F00'], [0.35, '#F0C05A'],
    [0.50, '#F5E6A3'],
    [0.65, '#7ECEEB'], [0.80, '#56B4E9'], [1.00, '#0072B2'],
]

# ── 3. Build treemap ─────────────────────────────────────────────────────────
fig1 = go.Figure(go.Treemap(
    labels=treemap_df['Industry'],
    values=treemap_df['MarketCap'],
    parents=['' for _ in range(len(treemap_df))],
    text=treemap_df['NetMargin'].apply(lambda x: f"{x:.1%}"),
    texttemplate='<b>%{label}</b><br>%{text}',
    textfont=dict(size=14, family='Arial', color='white'),
    insidetextfont=dict(size=14, color='white'),
    textposition='middle center',
    hovertext=treemap_df.apply(
        lambda r: (
            f"<b>{r['Industry']}</b><br>"
            f"Market Cap: ${r['MarketCap'] / 1000:.0f}B<br>"
            f"Net Margin: {r['NetMargin']:.1%}<br>"
            f"Revenue: ${r['Revenue']:,.0f}M"
        ), axis=1
    ),
    hovertemplate='%{hovertext}<extra></extra>',
    marker=dict(
        colors=treemap_df['NetMargin'],
        colorscale=COLOR_SCALE,
        cmin=-0.15, cmax=0.40,
        line=dict(width=1.2, color='#222944'),
        cornerradius=0.5,
        colorbar=dict(
            title=dict(text='Net Margin', font=dict(size=13, color='#aaa')),
            tickformat='.0%', tickfont=dict(size=12, color='#aaa'),
            tickvals=[-0.1, 0, 0.1, 0.2, 0.3, 0.4],
            orientation='h', x=0.5, xanchor='center',
            y=-0.02, yanchor='top',
            thickness=12, len=0.5, outlinewidth=0,
        ),
    ),
    tiling=dict(packing='squarify', pad=0.5),
    root=dict(color='rgba(0,0,0,0)'),
    pathbar=dict(visible=False),
))

add_branding(fig1, y=1.12, size_x=0.04, size_y=0.06, text_x=0.948, text_y=1.07)

fig1.update_layout(
    title=dict(
        text=(
            '<b style="font-family:Georgia,Garamond,serif;font-size:26px;'
            'letter-spacing:0.5px">US Sector Landscape</b>'
            '<br><span style="font-family:Helvetica,Arial,sans-serif;font-size:14px;'
            'color:#8a9bae;letter-spacing:1.5px;text-transform:uppercase">'
            'market cap by industry · color = net margin · 94 industries '
            '· damodaran jan 2026</span>'
        ),
        font=dict(size=26, color='white'), x=0.01, xanchor='left',
    ),
    uniformtext=dict(minsize=6, mode='hide'),
    margin=dict(t=80, l=2, r=2, b=60),
    height=720,
    paper_bgcolor='#272f47', plot_bgcolor='#242B46',
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**Key takeaways:** As of January 2026, the US equity market is worth roughly \$70 trillion spread across
94 industries, yet just five of them account for approximately 41% of that total: Semiconductors,
System & Application Software, Entertainment Software, Computers & Peripherals, and Biotech Drugs.
Scale and profitability are not the same thing: some of the largest tiles in the treemap carry the
thinnest margins, while several mid sized industries are among the most profitable in the dataset.
""")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 2 — CAPITAL STRUCTURE & COST (STACKED BAR)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
### Rising Action: What does capital cost and where does that cost come from?

Each bar decomposes the WACC into its two components:
debt contribution Kd(1-t) x D/V and equity contribution Ke x E/V.
The total bar length equals the sector's weighted average cost of capital.
All 11 GICS sectors are shown.
""")

# ── 1. Merge market cap with WACC components at industry level ────────────────
cap_ind = wacc[['Industry Name', 'Sector', 'Beta', 'Cost of Equity',
                'After-tax Cost of Debt', 'E/(D+E)', 'D/(D+E)',
                'Cost of Capital']].merge(
    dollar[['Industry Name', 'Market Cap ($ millions)']],
    on='Industry Name'
).copy()
cap_ind.columns = ['Industry', 'Sector', 'Beta', 'Ke', 'Kd',
                    'EqWeight', 'DebtWeight', 'WACC', 'MCap']

cap_ind['Debt_Cont']   = cap_ind['Kd'] * cap_ind['DebtWeight'] * 100
cap_ind['Equity_Cont'] = cap_ind['Ke'] * cap_ind['EqWeight'] * 100

# ── 2. Market-cap-weighted aggregation to sector level ────────────────────────
def wavg(group, col):
    """Market-cap-weighted average of col within a sector."""
    return np.average(group[col], weights=group['MCap'])

sector = cap_ind.groupby('Sector').apply(
    lambda g: pd.Series({
        'Debt_Contribution':   wavg(g, 'Debt_Cont'),
        'Equity_Contribution': wavg(g, 'Equity_Cont'),
        'WACC':   wavg(g, 'Debt_Cont') + wavg(g, 'Equity_Cont'),
        'Ke':     wavg(g, 'Ke') * 100,
        'Kd':     wavg(g, 'Kd') * 100,
        'EqWeight':   wavg(g, 'EqWeight') * 100,
        'DebtWeight': wavg(g, 'DebtWeight') * 100,
        'Beta':   wavg(g, 'Beta'),
        'MCap':   g['MCap'].sum(),
        'N_Industries': len(g),
    }), include_groups=False
).sort_values('WACC', ascending=True).reset_index()

sector['Debt_Label']   = sector['Debt_Contribution'].apply(
    lambda x: f"{x:.1f}%" if x > 0.6 else '')
sector['Equity_Label'] = sector['Equity_Contribution'].apply(
    lambda x: f"{x:.1f}%")

# ── 3. Build stacked bar chart ───────────────────────────────────────────────
fig2 = go.Figure()

fig2.add_trace(go.Bar(
    y=sector['Sector'], x=sector['Debt_Contribution'], orientation='h',
    name='Debt: Kd × (D/V)',
    marker=dict(color='#56B4E9', line=dict(width=0.5, color='#222944')),
    text=sector['Debt_Label'], textposition='inside',
    textfont=dict(size=10, color='#222944'),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Kd (after-tax): %{customdata[0]:.2f}%<br>'
        'Debt weight (D/V): %{customdata[1]:.0f}%<br>'
        'Debt contribution: %{x:.2f}%<br>'
        'Industries: %{customdata[2]:.0f}'
        '<extra>Debt component</extra>'
    ),
    customdata=np.column_stack([
        sector['Kd'], sector['DebtWeight'], sector['N_Industries']
    ]),
))

fig2.add_trace(go.Bar(
    y=sector['Sector'], x=sector['Equity_Contribution'], orientation='h',
    name='Equity: Ke × (E/V)',
    marker=dict(color='#0072B2', line=dict(width=0.5, color='#222944')),
    text=sector['Equity_Label'], textposition='inside',
    textfont=dict(size=10, color='white'),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Ke: %{customdata[0]:.2f}%<br>'
        'Equity weight (E/V): %{customdata[1]:.0f}%<br>'
        'Beta: %{customdata[2]:.2f}<br>'
        'Equity contribution: %{x:.2f}%<br>'
        'Industries: %{customdata[3]:.0f}'
        '<extra>Equity component</extra>'
    ),
    customdata=np.column_stack([
        sector['Ke'], sector['EqWeight'], sector['Beta'],
        sector['N_Industries']
    ]),
))

for _, row in sector.iterrows():
    fig2.add_annotation(
        x=row['WACC'] + 0.15, y=row['Sector'],
        text=f"<b>{row['WACC']:.1f}%</b>",
        showarrow=False, font=dict(size=10, color='#8a9bae'),
        xanchor='left',
    )

add_branding(fig2, y=1.12, size_x=0.04, size_y=0.07, text_x=0.948, text_y=1.06)

fig2.update_layout(
    barmode='stack',
    title=dict(
        text=(
            '<b style="font-family:Georgia,Garamond,serif;font-size:26px;'
            'letter-spacing:0.5px">Where Does the Cost of Capital Come From?</b>'
            '<br><span style="font-family:Helvetica,Arial,sans-serif;font-size:14px;'
            'color:#8a9bae;letter-spacing:1.5px;text-transform:uppercase">'
            'wacc decomposition · 11 gics sectors · market cap weighted '
            '· damodaran jan 2026</span>'
        ),
        font=dict(size=26, color='white'), x=0.01, xanchor='left',
    ),
    xaxis=dict(
        title='', ticksuffix='%', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.07)', zeroline=False, range=[0, 11],
    ),
    yaxis=dict(title='', tickfont=dict(size=13, color='#c8d0dc')),
    legend=dict(
        orientation='h', yanchor='top', y=-0.08, xanchor='center', x=0.5,
        font=dict(size=11, color='#8a9bae'),
        bgcolor='rgba(0,0,0,0)', borderwidth=0,
    ),
    height=520,
    margin=dict(t=85, l=200, r=80, b=70),
    paper_bgcolor='#272f47', plot_bgcolor='#242B46',
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**Key takeaways:** WACC ranges from roughly 4.9% in Utilities to 9.5% in Technology, a 4.6 pp spread
that defines the minimum return every sector must earn before it creates any value at all. Technology's
high cost comes almost entirely from expensive equity: the sector carries high beta and negligible debt,
so shareholders bear the full risk premium. Financials and Utilities take the opposite approach, using
leverage to compress their cost. Across all sectors the equity premium is the dominant driver; Ke varies
far more than Kd, which means the financing decision shapes the competitive landscape as much as the
operating one. This sets up Chart 3: do sectors with expensive capital actually earn enough ROIC to
justify it?
""")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 3 — VALUE CREATION (BUBBLE CHART)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
### Climax: Which industries actually create value, and which only appear to?

An industry creates value when ROIC > WACC. The horizontal axis shows this
spread; the vertical axis shows expected EBIT growth
(g = ROC x reinvestment rate, from Damodaran's fundamental growth model).
Bubble size encodes |EVA| in dollar terms; blue = value creator,
orange = value destroyer.

Four quadrants emerge: **compounders** (upper right), **cash cows** (lower right),
**growth traps** (upper left), and **value traps** (lower left).
""")

# ── 1. Merge EVA spread + growth + market cap ────────────────────────────────
bubble_df = eva[['Industry Name', 'Sector', '(ROC - WACC)',
                 'EVA (US $ millions)', 'ROC', 'Cost of Capital',
                 'BV of Capital']].merge(
    growth[['Industry Name', 'Expected Growth in EBIT', 'Reinvestment Rate']],
    on='Industry Name', how='left'
).merge(
    dollar[['Industry Name', 'Market Cap ($ millions)']],
    on='Industry Name', how='left'
).copy()

bubble_df.columns = ['Industry', 'Sector', 'Spread', 'EVA', 'ROC', 'WACC',
                      'InvestedCap', 'Growth', 'ReinvRate', 'MCap']

bubble_df = bubble_df.dropna(subset=['Spread', 'Growth']).copy()

bubble_df['Spread_pct'] = bubble_df['Spread'] * 100
bubble_df['Growth_pct'] = bubble_df['Growth'] * 100

# ── 2. Bubble sizing ─────────────────────────────────────────────────────────
bubble_df['AbsEVA']    = bubble_df['EVA'].abs()
bubble_df['BubbleSize'] = (np.sqrt(bubble_df['AbsEVA'] / bubble_df['AbsEVA'].max())
                           * 55 + 4)

# Colorblind-safe: blue = value creator, orange = value destroyer (Okabe-Ito)
bubble_df['Color'] = bubble_df['EVA'].apply(
    lambda x: '#0072B2' if x > 0 else '#E69F00')

# ── 3. Auto-label extremes ──────────────────────────────────────────────────
label_candidates = set()
label_candidates.update(bubble_df.nlargest(3, 'Spread_pct')['Industry'])
label_candidates.update(bubble_df.nsmallest(3, 'Spread_pct')['Industry'])
label_candidates.update(bubble_df.nlargest(3, 'AbsEVA')['Industry'])
label_candidates.update(bubble_df.nlargest(2, 'Growth_pct')['Industry'])

# ── 4. Hover text ────────────────────────────────────────────────────────────
bubble_df['HoverText'] = bubble_df.apply(
    lambda r: (
        f"<b>{r['Industry']}</b> ({r['Sector']})<br>"
        f"ROIC − WACC: {r['Spread_pct']:+.1f} pp<br>"
        f"Expected growth: {r['Growth_pct']:.1f}%<br>"
        f"EVA: ${r['EVA']:,.0f}M<br>"
        f"Market Cap: ${r['MCap'] / 1000:.0f}B"
    ), axis=1
)

# ── 5. Build scatter ─────────────────────────────────────────────────────────
fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=bubble_df['Spread_pct'], y=bubble_df['Growth_pct'],
    mode='markers',
    marker=dict(
        size=bubble_df['BubbleSize'],
        color=bubble_df['Color'],
        line=dict(width=0.8, color='rgba(255,255,255,0.3)'),
        opacity=0.85,
    ),
    hovertext=bubble_df['HoverText'],
    hovertemplate='%{hovertext}<extra></extra>',
    showlegend=False,
))

median_growth = bubble_df['Growth_pct'].median()

# Quadrant background shading (drawn before data so bubbles sit on top)
x_min, x_max = bubble_df['Spread_pct'].min() - 3, bubble_df['Spread_pct'].max() + 3
y_min, y_max = bubble_df['Growth_pct'].min() - 2, bubble_df['Growth_pct'].max() + 2

# Negative quadrants get a warm tint, positive quadrants get a cool tint
quad_shapes = [
    dict(x0=x_min, x1=0, y0=median_growth, y1=y_max,  # top-left: growth traps
         fillcolor='rgba(230,159,0,0.06)', line_width=0),
    dict(x0=0, x1=x_max, y0=median_growth, y1=y_max,  # top-right: compounders
         fillcolor='rgba(0,114,178,0.06)', line_width=0),
    dict(x0=x_min, x1=0, y0=y_min, y1=median_growth,  # bottom-left: value traps
         fillcolor='rgba(230,159,0,0.08)', line_width=0),
    dict(x0=0, x1=x_max, y0=y_min, y1=median_growth,  # bottom-right: cash cows
         fillcolor='rgba(0,114,178,0.04)', line_width=0),
]
for s in quad_shapes:
    fig3.add_shape(type='rect', layer='below', **s)

fig3.add_hline(y=median_growth,
               line=dict(color='rgba(255,255,255,0.20)', width=1.2, dash='dot'))
fig3.add_vline(x=0,
               line=dict(color='rgba(255,255,255,0.30)', width=1.5, dash='dot'))

# Quadrant labels: colored title + plain-language sub-description with background
q_base = dict(showarrow=False, xref='paper', yref='paper',
              bgcolor='rgba(34,41,68,0.75)', borderpad=4)

# Top-left: GROWTH TRAPS (negative, orange tint)
fig3.add_annotation(x=0.02, y=0.98, text='<b>GROWTH TRAPS</b>',
                    xanchor='left', yanchor='top',
                    font=dict(size=14, color='#E69F00', family='Georgia, serif'),
                    **q_base)
fig3.add_annotation(x=0.02, y=0.93, text='Growing fast, but destroying value',
                    xanchor='left', yanchor='top',
                    font=dict(size=10, color='rgba(255,255,255,0.55)',
                              family='Helvetica, Arial, sans-serif'),
                    **q_base)

# Top-right: COMPOUNDERS (positive, blue tint)
fig3.add_annotation(x=0.98, y=0.98, text='<b>COMPOUNDERS</b>',
                    xanchor='right', yanchor='top',
                    font=dict(size=14, color='#56B4E9', family='Georgia, serif'),
                    **q_base)
fig3.add_annotation(x=0.98, y=0.93, text='Growing fast and creating value',
                    xanchor='right', yanchor='top',
                    font=dict(size=10, color='rgba(255,255,255,0.55)',
                              family='Helvetica, Arial, sans-serif'),
                    **q_base)

# Bottom-left: VALUE TRAPS (negative, orange tint)
fig3.add_annotation(x=0.02, y=0.02, text='<b>VALUE TRAPS</b>',
                    xanchor='left', yanchor='bottom',
                    font=dict(size=14, color='#E69F00', family='Georgia, serif'),
                    **q_base)
fig3.add_annotation(x=0.02, y=0.07, text='Low growth, destroying value',
                    xanchor='left', yanchor='bottom',
                    font=dict(size=10, color='rgba(255,255,255,0.55)',
                              family='Helvetica, Arial, sans-serif'),
                    **q_base)

# Bottom-right: CASH COWS (positive, blue tint)
fig3.add_annotation(x=0.98, y=0.02, text='<b>CASH COWS</b>',
                    xanchor='right', yanchor='bottom',
                    font=dict(size=14, color='#56B4E9', family='Georgia, serif'),
                    **q_base)
fig3.add_annotation(x=0.98, y=0.07, text='Low growth, but creating value',
                    xanchor='right', yanchor='bottom',
                    font=dict(size=10, color='rgba(255,255,255,0.55)',
                              family='Helvetica, Arial, sans-serif'),
                    **q_base)

# ── 6. Annotations for extreme industries ────────────────────────────────────
for _, row in bubble_df[bubble_df['Industry'].isin(label_candidates)].iterrows():
    fig3.add_annotation(
        x=row['Spread_pct'], y=row['Growth_pct'],
        text=row['Industry'], showarrow=True,
        arrowhead=0, arrowwidth=0.8, arrowcolor='rgba(255,255,255,0.3)',
        ax=25, ay=-20,
        font=dict(size=9, color='#c8d0dc',
                  family='Helvetica, Arial, sans-serif'),
        bgcolor='rgba(34,41,68,0.7)', borderpad=2,
    )

add_branding(fig3)

fig3.update_layout(
    title=dict(
        text=(
            '<b style="font-family:Georgia,Garamond,serif;font-size:26px;'
            'letter-spacing:0.5px">Who Creates Value, and Who Just Grows?</b>'
            '<br><span style="font-family:Helvetica,Arial,sans-serif;'
            'font-size:14px;color:#8a9bae;letter-spacing:1.5px;'
            'text-transform:uppercase">'
            'roic − wacc vs expected growth · bubble size = |eva| '
            f'· {len(bubble_df)} industries · damodaran jan 2026</span>'
        ),
        font=dict(size=26, color='white'), x=0.01, xanchor='left',
    ),
    xaxis=dict(
        title=dict(text='ROIC − WACC spread (pp)  →  higher = more value created',
                   font=dict(size=14, color='#8a9bae')),
        ticksuffix=' pp', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.05)', zeroline=False,
    ),
    yaxis=dict(
        title=dict(text='Expected EBIT growth (%)  →  higher = faster growth',
                   font=dict(size=14, color='#8a9bae')),
        ticksuffix='%', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.05)', zeroline=False,
    ),
    height=700,
    margin=dict(t=85, l=70, r=40, b=60),
    paper_bgcolor='#272f47', plot_bgcolor='#242B46',
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**Key takeaways:** Most industries cluster to the right of zero: ROIC exceeds WACC in most cases, but the spread
varies enormously, from as low as 7 pp below zero for Software (Internet) and Auto & Truck all
the way to +56 pp for Tobacco. The dominant compounders are Software (System & Application), Software
(Entertainment), Semiconductor, and Computers/Peripherals: large blue bubbles that sit high and to the
right, generating both superior spreads and above average growth expectations. Growth traps do exist:
Software (Internet) and Drugs (Biotechnology) grow fast but destroy value because their ROIC cannot
cover the high cost of equity the market requires from them. Tobacco occupies the opposite extreme:
the most profitable industry in the dataset at +56 pp but with expected growth of only 1.5%, placing it
firmly in the cash cow quadrant. Auto & Truck is the largest single value destroyer in dollar terms,
with \$38 billion in destroyed EVA, combining a spread below its cost of capital with minimal growth.
""")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 4 — MARKET'S VERDICT (SCATTER)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
### Falling Action: Does the market agree with the fundamentals?

EV/IC (Enterprise Value / Invested Capital) measures what the market pays
per dollar of capital deployed. If ROIC > WACC, each dollar of invested
capital generates value, so EV/IC should exceed 1. The regression line
(OLS regression) confirms the market broadly prices value creation correctly;
the most informative cases are the **divergences**, industries above or below
the fit.

**Caveat:** EV/IC structurally favors asset light sectors (tech, software)
where R&D is expensed rather than capitalized, keeping invested capital
artificially low.
""")

# ── 1. Merge spread, EV, invested capital, market cap ────────────────────────
ev_df = dollar[['Industry Name', 'Sector', 'Enteprise Value ($ millions)',
                'Invested Capital ($ millions)',
                'Market Cap ($ millions)']].merge(
    eva[['Industry Name', '(ROC - WACC)', 'EVA (US $ millions)',
         'ROC', 'Cost of Capital']],
    on='Industry Name'
).copy()
ev_df.columns = ['Industry', 'Sector', 'EV', 'IC', 'MCap',
                  'Spread', 'EVA', 'ROIC', 'WACC']

ev_df = ev_df[ev_df['IC'] > 0].copy()
ev_df['EV_IC']      = ev_df['EV'] / ev_df['IC']
ev_df['Spread_pct'] = ev_df['Spread'] * 100

ev_df = ev_df.dropna(subset=['Spread_pct', 'EV_IC']).copy()

# ── 2. Closed-form OLS regression ────────────────────────────────────────────
x_arr = ev_df['Spread_pct'].values
y_arr = ev_df['EV_IC'].values
x_mu, y_mu = x_arr.mean(), y_arr.mean()

slope     = np.sum((x_arr - x_mu) * (y_arr - y_mu)) / np.sum((x_arr - x_mu) ** 2)
intercept = y_mu - slope * x_mu

ss_xy = np.sum((x_arr - x_mu) * (y_arr - y_mu))
ss_xx = np.sum((x_arr - x_mu) ** 2)
ss_yy = np.sum((y_arr - y_mu) ** 2)
r_val = ss_xy / np.sqrt(ss_xx * ss_yy)

ev_df['Expected_EV_IC'] = slope * ev_df['Spread_pct'] + intercept
ev_df['Residual']       = ev_df['EV_IC'] - ev_df['Expected_EV_IC']

# ── 3. Sector color palette ──────────────────────────────────────────────────
# Colorblind-safe sector palette (Okabe-Ito + extended Tol)
SECTOR_COLORS = {
    'Technology': '#0072B2',           'Healthcare': '#009E73',
    'Financials': '#E69F00',           'Energy': '#D55E00',
    'Consumer Discretionary': '#CC79A7', 'Consumer Staples': '#56B4E9',
    'Industrials': '#F0E442',          'Materials': '#999999',
    'Real Estate': '#882255',          'Utilities': '#44AA99',
    'Communication Services': '#DDCC77',
}

# ── 4. Label divergent industries ────────────────────────────────────────────
label_set = set()
label_set.update(ev_df.nlargest(3, 'Residual')['Industry'])
label_set.update(ev_df.nsmallest(2, 'Residual')['Industry'])
label_set.update(ev_df.nlargest(2, 'EV_IC')['Industry'])
label_set.update(ev_df.nsmallest(2, 'EV_IC')['Industry'])

# ── 5. Hover text ────────────────────────────────────────────────────────────
ev_df['HoverText'] = ev_df.apply(
    lambda r: (
        f"<b>{r['Industry']}</b> ({r['Sector']})<br>"
        f"EV/IC: {r['EV_IC']:.1f}x<br>"
        f"ROIC − WACC: {r['Spread_pct']:+.1f} pp<br>"
        f"ROIC: {r['ROIC']*100:.1f}% · WACC: {r['WACC']*100:.1f}%<br>"
        f"EVA: ${r['EVA']:,.0f}M<br>"
        f"Market Cap: ${r['MCap']/1000:.0f}B"
    ), axis=1
)

# ── 5b. Marker size proportional to market cap (log-scaled, 6–22 px) ─────────
_mcap_log = np.log1p(ev_df['MCap'])
ev_df['MarkerSize'] = 6 + (_mcap_log - _mcap_log.min()) / (_mcap_log.max() - _mcap_log.min()) * 16

# ── 6. Build scatter (one trace per sector) ──────────────────────────────────
fig4 = go.Figure()

# Zone shading: value destroyers (left) vs value creators (right)
_x_min = float(ev_df['Spread_pct'].min()) - 5
_x_max = float(ev_df['Spread_pct'].max()) + 5
_y_max = float(ev_df['EV_IC'].max()) + 3
fig4.add_shape(type='rect', layer='below',
    x0=_x_min, x1=0, y0=0, y1=_y_max,
    fillcolor='rgba(230,159,0,0.05)', line_width=0)
fig4.add_shape(type='rect', layer='below',
    x0=0, x1=_x_max, y0=0, y1=_y_max,
    fillcolor='rgba(0,114,178,0.05)', line_width=0)
# EV/IC = 1 reference band (fair value)
fig4.add_shape(type='rect', layer='below',
    x0=_x_min, x1=_x_max, y0=0.85, y1=1.15,
    fillcolor='rgba(255,255,255,0.03)', line_width=0)

for sector_name, color in SECTOR_COLORS.items():
    mask = ev_df['Sector'] == sector_name
    if mask.sum() == 0:
        continue
    sub = ev_df[mask]
    fig4.add_trace(go.Scatter(
        x=sub['Spread_pct'], y=sub['EV_IC'],
        mode='markers', name=sector_name,
        marker=dict(size=sub['MarkerSize'], color=color, opacity=0.82,
                    line=dict(width=0.8, color='rgba(255,255,255,0.25)')),
        hovertext=sub['HoverText'],
        hovertemplate='%{hovertext}<extra></extra>',
    ))

fig4.add_hline(y=1, line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dot'))
fig4.add_vline(x=0, line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dot'))

# ── Highlight industries ABOVE the regression line (residual > 1 SD) ─────
_resid_threshold = ev_df['Residual'].std()
above_line = ev_df[ev_df['Residual'] > _resid_threshold]
# Outer glow ring
fig4.add_trace(go.Scatter(
    x=above_line['Spread_pct'], y=above_line['EV_IC'],
    mode='markers', name='_above_glow',
    marker=dict(
        symbol='circle',
        size=above_line['MarkerSize'] + 18,
        color='rgba(86,180,233,0.12)',
        line=dict(width=0, color='rgba(0,0,0,0)'),
    ),
    showlegend=False, hoverinfo='skip',
))
# Sharp outer ring
fig4.add_trace(go.Scatter(
    x=above_line['Spread_pct'], y=above_line['EV_IC'],
    mode='markers', name='Above regression line',
    marker=dict(
        symbol='circle-open',
        size=above_line['MarkerSize'] + 12,
        color='rgba(0,0,0,0)',
        line=dict(width=2.5, color='rgba(86,180,233,0.85)'),
    ),
    showlegend=True,
    hoverinfo='skip',
))

# OLS trend line (more visible)
x_line = np.linspace(ev_df['Spread_pct'].min() - 2,
                     ev_df['Spread_pct'].max() + 2, 100)
y_line = slope * x_line + intercept
fig4.add_trace(go.Scatter(
    x=x_line, y=y_line, mode='lines', name='Linear fit',
    line=dict(color='rgba(86,180,233,0.70)', width=2.0, dash='dash'),
    showlegend=False,
))

# Regression label next to the line
mid_x = x_line[len(x_line)//2]
mid_y = slope * mid_x + intercept
fig4.add_annotation(
    x=mid_x + 5, y=mid_y + 1.5,
    text=f'r = {r_val:.2f}',
    showarrow=False,
    font=dict(size=10, color='rgba(86,180,233,0.7)', family='Arial'),
)

# Zone annotations: explanatory text boxes
box_style = dict(showarrow=False, xref='paper', yref='paper',
                 bgcolor='rgba(34,41,68,0.80)', borderpad=6,
                 bordercolor='rgba(86,180,233,0.20)', borderwidth=1)
fig4.add_annotation(x=0.98, y=0.99,
    text='<b>Above the line</b>: market expects<br>future improvement or prices in<br>intangibles not on the balance sheet',
    xanchor='right', yanchor='top',
    font=dict(size=9.5, color='rgba(200,208,220,0.80)', family='Arial'),
    **box_style)
fig4.add_annotation(x=0.02, y=0.01,
    text='<b>Below the line</b>: market sees<br>structural risk that current<br>numbers do not yet capture',
    xanchor='left', yanchor='bottom',
    font=dict(size=9.5, color='rgba(200,208,220,0.80)', family='Arial'),
    **box_style)
# Zone label: subtle
fig4.add_annotation(x=0.02, y=0.98,
    text='<b>● Value destroyers</b>',
    showarrow=False, xref='paper', yref='paper',
    xanchor='left', yanchor='top',
    font=dict(size=12, color='rgba(230,159,0,0.85)', family='Arial'),
    bgcolor='rgba(34,41,68,0.55)', borderpad=5)
fig4.add_annotation(x=0.98, y=0.02,
    text='<b>Value creators ●</b>',
    showarrow=False, xref='paper', yref='paper',
    xanchor='right', yanchor='bottom',
    font=dict(size=12, color='rgba(86,180,233,0.85)', family='Arial'),
    bgcolor='rgba(34,41,68,0.55)', borderpad=5)
# Bubble size legend note
fig4.add_annotation(x=0.50, y=0.01,
    text='Bubble size = market capitalisation',
    showarrow=False, xref='paper', yref='paper',
    xanchor='center', yanchor='bottom',
    font=dict(size=9, color='rgba(138,155,174,0.60)', family='Arial'))

# ── 7. Annotations ───────────────────────────────────────────────────────────
for _, row in ev_df[ev_df['Industry'].isin(label_set)].iterrows():
    ay_offset = -22 if row['Residual'] > 0 else 18
    fig4.add_annotation(
        x=row['Spread_pct'], y=row['EV_IC'],
        text=row['Industry'], showarrow=True,
        arrowhead=0, arrowwidth=0.8, arrowcolor='rgba(255,255,255,0.3)',
        ax=30, ay=ay_offset,
        font=dict(size=9, color='#c8d0dc',
                  family='Helvetica, Arial, sans-serif'),
        bgcolor='rgba(34,41,68,0.7)', borderpad=2,
    )

add_branding(fig4)

fig4.update_layout(
    title=dict(
        text=(
            '<b style="font-family:Georgia,Garamond,serif;font-size:26px;'
            'letter-spacing:0.5px">Does the Market Agree?</b>'
            '<br><span style="font-family:Helvetica,Arial,sans-serif;'
            'font-size:14px;color:#8a9bae;letter-spacing:1.5px;'
            'text-transform:uppercase">'
            f'ev/ic multiple vs roic − wacc spread · r = {r_val:.2f} '
            f'· {len(ev_df)} industries · damodaran jan 2026</span>'
        ),
        font=dict(size=26, color='white'), x=0.01, xanchor='left',
    ),
    xaxis=dict(
        title=dict(text='ROIC − WACC spread (pp)  →  right = earns above cost of capital',
                   font=dict(size=14, color='#8a9bae')),
        ticksuffix=' pp', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.06)', zeroline=False,
        zerolinecolor='rgba(255,255,255,0.15)', zerolinewidth=1,
        range=[_x_min, _x_max],
    ),
    yaxis=dict(
        title=dict(text='EV / Invested Capital  →  higher = market pays more per dollar',
                   font=dict(size=14, color='#8a9bae')),
        ticksuffix='x', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.06)', zeroline=False,
        range=[0, _y_max],
    ),
    legend=dict(
        orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.01,
        font=dict(size=10, color='#8a9bae'),
        bgcolor='rgba(34,41,68,0.6)', borderwidth=0,
        itemsizing='constant',
    ),
    height=720,
    margin=dict(t=85, l=70, r=160, b=60),
    paper_bgcolor='#272f47', plot_bgcolor='#242B46',
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown(f"""
**Key takeaways:** The positive correlation (r = {r_val:.2f}, R² = {r_val**2:.2f}) confirms that the
market broadly agrees with the fundamentals: industries earning above their cost of capital trade at
higher EV/IC multiples. Computers/Peripherals is the standout, with an EV/IC near 23x and a +35 pp
spread: the market pays \$23 for every dollar of capital that Apple and its peers have deployed.
The most informative cases are the divergences from the regression line. Software (Internet) and Drugs
(Biotechnology) carry negative spreads yet trade at 9x and 7x respectively, because the market is
pricing in an expected improvement in returns rather than the current trailing data. Tobacco is the
mirror image: despite a +56 pp spread it trades at only 11x, because the market discounts the almost
complete absence of reinvestable growth and assigns a significant regulatory tail risk to future cash flows.
""")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 5 — CAPITAL ALLOCATION (STACKED BAR)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
### Resolution: Where does the profit go?

Value creation is only half the story. The expected growth rate
g = ROC x reinvestment rate depends on how much of its earnings an
industry reinvests at returns above WACC. This chart decomposes net income
into dividends, share buybacks, and retained earnings for 12 representative
industries drawn from the four quadrants of Chart 3.

Compounders retain a large share to fund reinvestment at high returns.
Cash cows return almost everything because attractive reinvestment
opportunities are scarce. Value destroyers often return more than they
earn, which means they are shrinking their capital base.
""")

# ── 1. Merge dividends/buybacks with EVA spread and growth ───────────────────
alloc = div.rename(columns={'Industry name': 'Industry Name'}).merge(
    eva[['Industry Name', '(ROC - WACC)', 'EVA (US $ millions)']],
    on='Industry Name'
).merge(
    growth[['Industry Name', 'Expected Growth in EBIT', 'Reinvestment Rate']],
    on='Industry Name', how='left'
).merge(
    dollar[['Industry Name', 'Market Cap ($ millions)']],
    on='Industry Name', how='left'
)

alloc['Sector']     = alloc['Industry Name'].map(SECTOR_MAP)
alloc['Spread_pct'] = alloc['(ROC - WACC)'] * 100
alloc['Growth_pct'] = alloc['Expected Growth in EBIT'] * 100
alloc['Buybacks']   = alloc['Dividends + Buybacks'] - alloc['Dividends']

# ── 2. Select 12 industries across all four Chart 3 quadrants ────────────────
pick = [
    # Compounders (high spread + high growth)
    'Software (Entertainment)', 'Software (System & Application)',
    'Semiconductor', 'Computers/Peripherals',
    # Cash cows (high spread + low growth)
    'Tobacco', 'Household Products', 'Beverage (Soft)',
    'Drugs (Pharmaceutical)',
    # Value destroyers / mixed (negative spread or borderline)
    'Auto & Truck', 'Green & Renewable Energy',
    'Restaurant/Dining', 'Aerospace/Defense',
]
sel = alloc[alloc['Industry Name'].isin(pick)].copy()

# ── 3. Compute % of net income for each allocation bucket ────────────────────
sel['NI']      = sel['Net Income']
sel['Div_pct'] = sel['Dividends']                              / sel['NI'].abs() * 100
sel['Buy_pct'] = sel['Buybacks']                               / sel['NI'].abs() * 100
sel['Ret_pct'] = (sel['NI'] - sel['Dividends + Buybacks'])     / sel['NI'].abs() * 100

sel = sel.sort_values('Spread_pct', ascending=True).reset_index(drop=True)

# ── 4. Quadrant label ────────────────────────────────────────────────────────
def assign_quadrant(row):
    """Classify industry into Chart 3 quadrant based on spread and growth."""
    if row['Spread_pct'] < 0:
        return 'Destroyer'
    elif row['Growth_pct'] > 5:
        return 'Compounder'
    else:
        return 'Cash Cow'

sel['Quadrant'] = sel.apply(assign_quadrant, axis=1)

sel['Label'] = sel.apply(
    lambda r: f"{r['Industry Name']}  (g={r['Growth_pct']:.1f}%)", axis=1)

# ── 5. Color palette ─────────────────────────────────────────────────────────
# Colorblind-safe allocation colors (Okabe-Ito)
CLR_DIV = '#E69F00'   # Dividends: orange
CLR_BUY = '#56B4E9'   # Buybacks: sky blue
CLR_RET = '#0072B2'   # Retained: blue
sel['Ret_bar'] = sel['Ret_pct'].clip(lower=0)

# ── 6. Build stacked bar chart ───────────────────────────────────────────────
fig5 = go.Figure()

fig5.add_trace(go.Bar(
    y=sel['Label'], x=sel['Div_pct'], orientation='h',
    name='Dividends',
    marker=dict(color=CLR_DIV, line=dict(width=0.5, color='#222944')),
    text=sel['Div_pct'].apply(lambda x: f'{x:.0f}%' if x > 5 else ''),
    textposition='inside', textfont=dict(size=10, color='#222'),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Dividends: %{x:.1f}% of net income<br>'
        '$%{customdata[0]:,.0f}M'
        '<extra>Dividends</extra>'
    ),
    customdata=np.column_stack([sel['Dividends']]),
))

fig5.add_trace(go.Bar(
    y=sel['Label'], x=sel['Buy_pct'], orientation='h',
    name='Buybacks',
    marker=dict(color=CLR_BUY, line=dict(width=0.5, color='#222944')),
    text=sel['Buy_pct'].apply(lambda x: f'{x:.0f}%' if x > 5 else ''),
    textposition='inside', textfont=dict(size=10, color='#003844'),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Buybacks: %{x:.1f}% of net income<br>'
        '$%{customdata[0]:,.0f}M'
        '<extra>Buybacks</extra>'
    ),
    customdata=np.column_stack([sel['Buybacks']]),
))

fig5.add_trace(go.Bar(
    y=sel['Label'], x=sel['Ret_bar'], orientation='h',
    name='Retained (reinvested)',
    marker=dict(color=CLR_RET, line=dict(width=0.5, color='#222944')),
    text=sel['Ret_bar'].apply(lambda x: f'{x:.0f}%' if x > 5 else ''),
    textposition='inside', textfont=dict(size=10, color='#003'),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Retained: %{x:.1f}% of net income<br>'
        'ROIC−WACC: %{customdata[0]:+.1f} pp<br>'
        'Expected growth: %{customdata[1]:.1f}%'
        '<extra>Retained</extra>'
    ),
    customdata=np.column_stack([sel['Spread_pct'], sel['Growth_pct']]),
))

# ── 7. Spread annotation at end of each bar ─────────────────────────────────
for _, row in sel.iterrows():
    total = row['Div_pct'] + row['Buy_pct'] + max(row['Ret_pct'], 0)
    fig5.add_annotation(
        x=total + 2, y=row['Label'],
        text=f"<b>+{row['Spread_pct']:.0f} pp</b>" if row['Spread_pct'] >= 0 else f"<b>{abs(row['Spread_pct']):.0f} pp</b>",
        showarrow=False,
        font=dict(size=11, color='#7ec8a0' if row['Spread_pct'] > 0 else '#e07878'),
        xanchor='left',
    )

# 100% reference line: anything beyond means paying out more than earned
fig5.add_vline(x=100, line=dict(color='rgba(213,94,0,0.75)', width=3.0, dash='solid'))

# Horizontal separators between groups (destroyers | cash cows | compounders)
# Sorted ascending by spread: indices 0-3 destroyers, 4-7 cash cows, 8-11 compounders
fig5.add_hline(y=3.5, line=dict(color='rgba(255,255,255,0.15)', width=1, dash='dot'))
fig5.add_hline(y=7.5, line=dict(color='rgba(255,255,255,0.15)', width=1, dash='dot'))

# Group labels: placed vertically in the middle of each group
# (yref='paper' so they sit in the correct band regardless of x range)
_group_style = dict(showarrow=False, xref='paper', yref='paper',
                    font=dict(size=10, color='rgba(255,255,255,0.55)',
                              family='Georgia, serif'),
                    bgcolor='rgba(34,41,68,0.70)', borderpad=4,
                    bordercolor='rgba(255,255,255,0.10)', borderwidth=1)
# 12 bars → bands at [0, 3.5], [3.5, 7.5], [7.5, 11.5]
# paper y: 0 = bottom bar, 1 = top bar
# Compounders: rows 8-11 → paper y ≈ 0.67–1.0 → midpoint ≈ 0.83
fig5.add_annotation(x=1.01, y=0.85, text='Compounders ▲',
                    xanchor='left', yanchor='middle', **_group_style)
# Cash Cows: rows 4-7 → paper y ≈ 0.33–0.67 → midpoint ≈ 0.50
fig5.add_annotation(x=1.01, y=0.50, text='Cash Cows ●',
                    xanchor='left', yanchor='middle', **_group_style)
# Destroyers: rows 0-3 → paper y ≈ 0.0–0.33 → midpoint ≈ 0.17
fig5.add_annotation(x=1.01, y=0.15, text='Destroyers ▼',
                    xanchor='left', yanchor='middle', **_group_style)

# Explanatory text box (bottom-right corner)
fig5.add_annotation(x=0.98, y=0.98, xref='paper', yref='paper',
    text=('<b>Reading this chart:</b><br>'
          'Each bar = how net income is split: dividends, buybacks, retained<br>'
          '<b>pp</b> = ROIC minus WACC (value created per unit of capital)<br>'
          'Past 100%: payout exceeds net income (financed by debt or cash)'),
    showarrow=False, xanchor='right', yanchor='top',
    font=dict(size=10, color='rgba(255,255,255,0.58)', family='Arial'),
    bgcolor='rgba(34,41,68,0.80)', borderpad=8,
    align='left')

add_branding(fig5, y=1.10, size_x=0.04, size_y=0.06, text_x=0.948, text_y=1.06)

fig5.update_layout(
    barmode='stack',
    title=dict(
        text=(
            '<b style="font-family:Georgia,Garamond,serif;font-size:26px;'
            'letter-spacing:0.5px">Where Does the Profit Go?</b>'
            '<br><span style="font-family:Helvetica,Arial,sans-serif;'
            'font-size:14px;color:#8a9bae;letter-spacing:1.5px;'
            'text-transform:uppercase">'
            'net income split: dividends · buybacks · retained '
            '· 12 industries · damodaran jan 2026</span>'
        ),
        font=dict(size=26, color='white'), x=0.01, xanchor='left',
    ),
    xaxis=dict(
        title=dict(text='% of Net Income',
                   font=dict(size=14, color='#8a9bae')),
        ticksuffix='%', tickfont=dict(size=12, color='#8a9bae'),
        gridcolor='rgba(255,255,255,0.07)', zeroline=False,
    ),
    yaxis=dict(title='', tickfont=dict(size=13, color='#c8d0dc')),
    legend=dict(
        orientation='h', yanchor='top', y=-0.10, xanchor='center', x=0.5,
        font=dict(size=12, color='#c8d0dc'),
        bgcolor='rgba(34,41,68,0.6)', borderwidth=0,
    ),
    height=640,
    margin=dict(t=110, l=260, r=170, b=110),
    paper_bgcolor='#272f47', plot_bgcolor='#242B46',
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
**Key takeaways:** The pattern is unambiguous. Compounders (Software and Semiconductor) retain
34–40% of earnings and grow at over 20% per year, because they have abundant reinvestment opportunities
at returns well above their cost of capital. This is exactly the profile the market values most
aggressively, as seen in Chart 4's highest EV/IC multiples. Tobacco is the perfect counterexample:
the highest spread in the dataset (+56 pp) yet it returns 94% of earnings as dividends and buybacks,
retaining almost nothing, because there is nowhere profitable to deploy additional capital; expected
growth is 1.5%. Auto & Truck and Green & Renewable Energy go further still, paying out more than they
earn; the vermillion segments represent capital being consumed rather than compounded, consistent with
the negative spreads seen in Chart 3. The link to Chart 4 is direct: industries that retain and reinvest
at high ROIC attract the highest market multiples, while industries that pay out everything are discounted
because the market sees no future growth engine.
""")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — CONCLUSIONS: THE VERDICT ON US EQUITY VALUE CREATION
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

st.markdown(
    '<h2 style="font-family:Georgia,Garamond,serif;font-size:30px;'
    'color:#e8eaf0;letter-spacing:0.3px;margin-bottom:4px">'
    'The Verdict: What the Data Says About US Equity in 2025</h2>'
    '<p style="font-family:Helvetica,Arial,sans-serif;font-size:14px;'
    'color:#8a9bae;letter-spacing:1.5px;text-transform:uppercase;margin-top:0">'
    'synthesis · damodaran january 2026 · 94 industries</p>',
    unsafe_allow_html=True,
)

st.markdown("""
The five charts tell a single coherent story: the US equity market in 2025 was not
a monolith. Seventy-five of the ninety-four industries in Damodaran's dataset earned
a return above their cost of capital, with an average positive spread of 11.7 percentage
points and a total aggregate EVA of \$1.35 trillion. But the aggregate masks a concentration
so extreme it borders on winner takes most: the AI infrastructure complex (software,
semiconductors, and computing hardware) generated over \$500 billion of that total alone.
Meanwhile, nineteen industries destroyed value, with auto manufacturing, real estate trusts,
and biotechnology accounting for the largest absolute losses.

**The AI infrastructure bet, already in the earnings.** Software (System & Application) and
Software (Entertainment), the Microsoft, Google, and Meta complex, posted spreads of
+20 and +19 percentage points respectively, with expected EBIT growth above 20% per year.
Semiconductor achieved a +17 pp spread on a capital base that absorbed Nvidia's explosive
capacity buildout during 2025. Critically, these are not valuation multiples built on
future promises: the returns are already in the trailing data, with ROIC averaging 27–29%
against a cost of capital of 9–11%. After the DeepSeek disruption in January 2025 briefly
raised efficiency questions, hyperscalers responded by accelerating, not cutting, capex
commitments; the market's high EV/IC multiples for these industries (Chart 4) reflect
the expectation that the monetisation of AI will compound further through 2026.

**The tobacco paradox: best returns, no reinvestment opportunity.** No industry in the
dataset earns a higher ROIC than tobacco at 63.1%, generating a spread of 56 percentage
points, nearly three times that of the strongest technology industries. Yet the
market cap sits at just \$350 billion. The explanation is in Chart 5: tobacco pays out 93%
of net income in dividends and buybacks, retaining almost nothing, because there is nowhere
profitable to deploy additional capital. Expected growth is 1.5% per year. Chart 4 makes
the market's verdict explicit: EV/IC is low despite the extraordinary spread, because a
stream of declining cash flows, however high margin today, is worth less than a smaller
but compounding one. Tobacco is the cleanest possible illustration of why ROIC alone does
not determine value: capital efficiency without reinvestment opportunity is a terminal asset.

**Auto & Truck: the cost of a transition between two broken models.** With a negative
spread of 7.1 percentage points and a net EVA of \$38 billion in destroyed value, the automotive
industry was the single largest value destroyer in absolute terms. The paradox is structural:
combustion platforms are losing share faster than the industry planned, while electric vehicle
programs require capital at scale without yet earning their cost of capital. Through 2025,
legacy automakers continued absorbing multibillion dollar EV losses while simultaneously
defending their combustion margins against intensified Chinese competition. The industry
responded by paying out 195% of net income (returning more than it earned, financed by debt),
which temporarily supports the share price but accelerates balance sheet deterioration. Chart 4
shows the market has fully priced this: auto trades well below the regression line, implying
no recovery in capital returns in the near term.

**Biotech: the market's largest calculated option position.** Drugs (Biotechnology) earned
a spread 5 pp below its cost of capital and destroyed \$27 billion in EVA, yet the market
assigned it a \$1.6 trillion capitalisation. This is not irrationality: it reflects the option
value embedded in clinical pipelines. Through 2025, GLP-1 receptor agonists continued
expanding from obesity and diabetes into cardiovascular, renal, and sleep disorder
indications, with addressable market estimates increasing with each positive trial readout.
The biotech sector is paying for the next wave of these programmes: most individual assets
will fail, but the few that succeed will generate returns disproportionate to the investment.
Chart 5 underscores the bet: a 322% payout ratio, with the industry burning more than three times
its net income on R&D, M&A, and operating losses, which only makes sense if the pipeline delivers.
The market is pricing in the probability that it will.

**The quiet compounder: healthcare support services.** Healthcare Support Services posted a
ROIC of 31.2% against a WACC of 6.8%, a spread of +24 pp, and aggregate EVA of \$57 billion,
larger than the entire pharmaceutical sector's value creation. These are the companies
managing the plumbing of the American healthcare system: pharmacy benefit managers, managed
care operators, specialised distributors. They benefit from structural complexity that
creates switching costs without requiring significant capital reinvestment, and they compound
(15.8% expected EBIT growth) because the underlying demand driver (an ageing US population
consuming increasingly expensive treatments) is both secular and inelastic. The market has
not fully valued them relative to software (Chart 4 places them above the regression line),
which suggests the spread is real but the growth premium is not yet fully priced in.

**Insurance: the structural winner of the rate normalisation cycle.** Insurance (General)
posted the second highest spread in the dataset at +38 pp, with ROIC of 44.5%. Insurance
(Property/Casualty) added a further \$38 billion in EVA. Even as the Federal Reserve
continued reducing rates through 2025, insurers benefited from the lagged effect of elevated
rates on their fixed income investment portfolios; float income remained structurally
higher than the 2022 baseline. Premium pricing also held firm across most lines following
consecutive years of elevated catastrophe activity. Chart 5 shows these industries retaining
52–57% of earnings for reinvestment, consistent with their above average growth outlook.
They are among the most overlooked compounders in the dataset.

**Real estate: still caught between rates and fundamentals.** REITs posted a −2.1 pp spread
and destroyed \$30 billion in EVA despite a market cap of \$1.2 trillion. The continued rate
reduction cycle through 2025 provided relief at the margin, but could not fully repair the
damage: commercial real estate valuations had reset materially, office vacancy in major US
markets remained structurally elevated, and significant refinancing volumes were still to
come. The REIT model is structurally leveraged to the risk free rate, both through asset
valuation and through the cost of the debt that finances their portfolios, meaning the path
to positive spreads requires not just lower rates but a genuine recovery in asset level cash
flows. Chart 3 places them firmly in the value trap quadrant: large market cap, negative
spread, and negative expected growth. Rate normalisation is necessary but not sufficient.

**The synthesis.** The data drawn from 94 industries and approximately \$70 trillion in
aggregate market capitalisation points to a market that is broadly rational but increasingly
bifurcated. Capital is flowing toward industries with genuine ROIC above cost and real
reinvestment opportunities: the compounders that create value by deploying more capital
at returns above cost. It is staying in industries with option value, correctly pricing
probability weighted outcomes for uncertain but high upside pipelines. And it is marking
down the capital traps, industries where returns are below cost, growth is absent, and the
payout policy reflects strategic exhaustion rather than discipline. The clearest signal in
the dataset is not any individual industry. It is the mechanism: the industries creating the
most value in 2025 are those that can afford to reinvest at scale, precisely because ROIC
exceeds WACC. Everything else is just returning capital while the structural clock runs down.
""")

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.divider()

st.markdown("""
<div style="text-align:center; color:#8a9bae; font-size:14px;
            font-family:Helvetica,Arial,sans-serif; padding:20px 0">
    <b>The Price of Growth</b> · Daniel Sigerist · HSLU DVIZ MM F2601 · 2026<br>
    Data: Aswath Damodaran, NYU Stern, January 2026<br>
    Built with Python, Pandas, Plotly & Streamlit
</div>
""", unsafe_allow_html=True)
