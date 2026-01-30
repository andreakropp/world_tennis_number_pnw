# World Tennis Number - PNW

Track and visualize World Tennis Number ratings over time for Pacific Northwest players.

## Features

- Individual player rating trends (singles and doubles)
- Multi-player comparison charts
- Rating distribution statistics
- Top player rankings
- Player profile links
- Automated web scraping of USTA ratings

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Visualization App
```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Weekly Data Updates

### Update Ratings from USTA Profiles

Run the scraper to fetch the latest ratings:
```bash
python scrape_wtn_ratings.py
```

**What it does:**
- Visits all USTA profiles in `data/wtn_profile_links.csv`
- Extracts current WTN ratings (singles and doubles)
- Filters to Medium and High confidence ratings only
- Appends new data to `data/wtn_ratings.csv`
- Takes ~3-4 minutes for 80 players (2-second delay between requests)

**Requirements:**
- Chrome browser installed
- ChromeDriver installed: `brew install chromedriver` (macOS)

**Note:** If you encounter macOS Gatekeeper issues with ChromeDriver:
```bash
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

## Data Files

- `data/wtn_ratings.csv` - Historical rating data (updated by scraper)
- `data/wtn_profile_links.csv` - Player profiles and USTA links

## Data Cleaning

If you encounter duplicate entries after scraping:
```bash
python clean_duplicates.py
```

## Project Structure

```
WTN/
├── app.py                      # Streamlit visualization app
├── scrape_wtn_ratings.py       # Web scraper for USTA profiles
├── clean_duplicates.py         # Utility to remove duplicate entries
├── requirements.txt            # Python dependencies
└── data/
    ├── wtn_ratings.csv         # Historical ratings (time series)
    └── wtn_profile_links.csv   # Player information and URLs
```
