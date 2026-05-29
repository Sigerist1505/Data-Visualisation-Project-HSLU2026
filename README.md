# The Price of Growth

How US Sectors Create and Destroy Value

HSLU DVIZ MM F2601 — Final Project, Spring 2026 · Daniel Sigerist

---

## About

This project explores value creation across 94 US industries using Aswath Damodaran's January 2026 dataset from NYU Stern. The central question is which sectors actually earn more than their cost of capital, and which ones just grow without creating real value. The story is told through five interactive charts built with Plotly, structured as a Freytag narrative arc and delivered as a Streamlit app.

## Live app

https://dviz-project-hslu2026.streamlit.app/

---

## Running the project

### Option 1 — Docker (easiest)

Runs both the Streamlit app and the Jupyter notebook together with no setup needed beyond having Docker installed.

```bash
git clone https://github.com/Sigerist1505/Data-Visualization-Project-HSLU2026.git
cd Data-Visualisation-Project-HSLU2026

docker compose up --build
```

- Streamlit app → `http://localhost:8501`
- Jupyter notebook → `http://localhost:8888`

The first build takes a few minutes. After that it starts instantly.

### Option 2 — Local (manual)

```bash
git clone https://github.com/Sigerist1505/Data-Visualization-Project-HSLU2026.git
cd Data-Visualisation-Project-HSLU2026

python -m venv venv
source venv/Scripts/activate    # Windows
source venv/bin/activate        # macOS / Linux

pip install -r requirements.docker.txt
streamlit run app.py
```

For the notebook, open a second terminal and run `jupyter notebook`.

---

## About the two requirements files

There are two dependency files in this repo and they serve different purposes.

`requirements.txt` is the slim version used by Streamlit Cloud for the live deployment. It only includes what the hosted app needs to run. Keeping it minimal avoids unnecessary build time and memory usage on the cloud platform.

`requirements.docker.txt` is the full version used for local development and Docker. It adds Jupyter and the rest of the development dependencies on top of the slim set, so both the app and the notebook can run together.

---

## Project structure

```
├── app.py                    # Streamlit app
├── requirements.txt          # Streamlit Cloud (slim)
├── requirements.docker.txt   # Docker and local dev (full)
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── data/                     # 7 CSV files from Damodaran (Jan 2026)
├── notebooks/
│   └── 01_data_story.ipynb
├── docs/
│   └── design_report.docx
└── assets/
    └── github_avatar.png
```

---

## The five charts

**Chart 1 — Sector Landscape.** Treemap of market cap by industry coloured by net margin. Gives a sense of where economic mass sits across the US economy.

**Chart 2 — Cost of Capital.** WACC decomposed into debt and equity for each sector. Sets the baseline return each industry must beat to create value.

**Chart 3 — Value Creation.** Bubble chart of ROIC minus WACC versus expected growth, with bubble size = absolute EVA. The four quadrants (compounders, cash cows, growth traps, value destroyers) are the core of the data story.

**Chart 4 — Market's Verdict.** EV/Invested Capital versus the ROIC minus WACC spread with an OLS regression. Tests whether market pricing lines up with the fundamentals.

**Chart 5 — Capital Allocation.** Net income split into dividends, buybacks and retained earnings for 12 industries across all four quadrants. The pp values show each industry's ROIC minus WACC spread.

---

## Data

All data comes from Aswath Damodaran's public datasets at NYU Stern (January 2026, FY2025 figures). Seven CSV files covering market cap, WACC, EVA, ROE, growth rates, dividends and betas across 94 US industries. https://pages.stern.nyu.edu/~adamodar/

## Tools

Python, Pandas, NumPy, Plotly, Streamlit, Jupyter
