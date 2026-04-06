# LILA BLACK — Level Designer Dashboard

A web tool for exploring player behavior on LILA BLACK maps.

## Project Structure

```
lila-viz/
├── app.py                  ← Main Streamlit app (run this)
├── data_loader.py          ← Parquet loading + preprocessing
├── coordinate_utils.py     ← World → minimap pixel conversion
├── requirements.txt
├── player_data/            ← PUT YOUR DATA HERE
│   ├── February_10/
│   ├── February_11/
│   ├── February_12/
│   ├── February_13/
│   └── February_14/
├── minimaps/               ← PUT MINIMAP IMAGES HERE
│   ├── AmbroseValley_Minimap.png
│   ├── GrandRift_Minimap.png
│   └── Lockdown_Minimap.jpg
└── README.md
```

## Local Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place data files
#    - Unzip player_data.zip → put the player_data/ folder here
#    - Put minimap images in minimaps/ folder

# 4. Run
streamlit run app.py
```

App opens at http://localhost:8501

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub (include requirements.txt, exclude player_data/)
2. Since player_data is large, you have two options:
   - **Option A (simple):** Commit the data files to the repo (fine for ~5MB)
   - **Option B (better):** Host data on S3/GCS and load via URL in data_loader.py
3. Go to https://share.streamlit.io → Connect your repo → Deploy

## What Each File Does

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI — sidebar filters, 3 tabs (Journeys, Heatmaps, Stats) |
| `data_loader.py` | Loads all 1243 parquet files, decodes bytes, computes pixel coords, caches result |
| `coordinate_utils.py` | Converts world (x,z) → minimap pixel → Plotly coordinates |

## Key Design Decisions

**Coordinate system:**  
`pixel_y = (1 - v) * 1024` (image coords, 0 = top)  
`plot_y  = 1024 - pixel_y` (Plotly coords, 0 = bottom)  
This ensures scatter points align with the minimap background image.

**Performance:**  
- Pixel coords pre-computed once at load time, stored in dataframe
- Player paths use Plotly's None-separator trick (all paths = 1 trace)
- `@st.cache_data` means data loads once per session (~30s first time)

**Paths only on single match:**  
Showing paths across 796 matches is visually useless. Heatmaps handle the multi-match case.
