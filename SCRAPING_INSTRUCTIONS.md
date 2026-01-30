# WTN Rating Scraper Instructions

This guide explains how to scrape WTN (World Tennis Number) ratings from USTA player profiles.

## Prerequisites

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome and ChromeDriver:**
   ```bash
   # On macOS with Homebrew
   brew install chromedriver

   # Or download from: https://chromedriver.chromium.org/
   ```

## Step 1: Inspect Page Structure (Optional but Recommended)

Before running the main scraper, it's helpful to inspect the USTA page structure to ensure the selectors are correct.

```bash
python inspect_usta_page.py
```

This will:
- Open a Chrome browser window
- Load a sample USTA profile
- Print out the page structure and elements containing WTN-related keywords
- Keep the browser open for 30 seconds so you can manually inspect

**What to look for:**
- Where the WTN Doubles rating is displayed
- Where the WTN Singles rating is displayed
- Where the "Updated" or "Last Updated" date is shown
- The HTML structure and CSS classes used

## Step 2: Update Selectors (if needed)

Based on the inspection, you may need to update the XPath selectors in `scrape_wtn_ratings.py`:

Look for these sections in the code:
```python
# Line ~90-95: Finding doubles rating
doubles_elem = driver.find_element(By.XPATH, "...")

# Line ~98-103: Finding singles rating
singles_elem = driver.find_element(By.XPATH, "...")

# Line ~106-111: Finding updated date
date_elem = driver.find_element(By.XPATH, "...")
```

## Step 3: Run the Scraper

```bash
python scrape_wtn_ratings.py
```

This will:
- Read all profiles from `data/wtn_profile_links.csv`
- Visit each USTA profile URL
- Extract WTN Doubles rating, WTN Singles rating, and Updated Date
- Save results to `data/wtn_profile_links_updated.csv`
- Save progress every 10 profiles (in case of interruption)

**Features:**
- Progress is printed for each profile
- 2-second delay between requests (to be respectful to USTA servers)
- Automatic progress saving every 10 profiles
- Error handling for failed requests

## Output

The script appends new records to: `data/wtn_ratings.csv`

Each player can have up to 2 records added (one for Doubles, one for Singles):
- `Name`: Player name
- `UAID`: USTA player ID
- `Date`: Date from the USTA profile showing when the rating was last updated
- `Format`: Either "Doubles" or "Singles"
- `Rating`: The WTN rating value (e.g., "24.77")
- `Confidence`: Confidence level (e.g., "High", "Medium", "Low")

## Troubleshooting

**ChromeDriver errors:**
- Make sure ChromeDriver is installed and in your PATH
- Try: `chromedriver --version` to verify installation
- Update ChromeDriver if using a newer version of Chrome

**No ratings found:**
- Run `inspect_usta_page.py` to see the actual page structure
- The USTA website may have changed - selectors may need updating
- Some profiles may not have WTN ratings yet

**Timeout errors:**
- Your internet connection may be slow
- Increase the timeout in `scrape_wtn_ratings.py` (line 60): `WebDriverWait(driver, 10)` → `WebDriverWait(driver, 20)`

**Rate limiting:**
- If USTA blocks requests, increase the delay (line 138): `time.sleep(2)` → `time.sleep(5)`

## Notes

- The script uses headless Chrome (runs in background)
- Scraping ~80 profiles will take approximately 3-4 minutes
- Results are saved incrementally, so you can stop and resume
