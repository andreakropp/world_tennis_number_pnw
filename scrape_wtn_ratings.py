#!/usr/bin/env python3
"""
Script to scrape WTN (World Tennis Number) ratings from USTA player profiles.
Reads player profile links from a CSV file and extracts current doubles and singles ratings.
"""

import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys


def setup_driver():
    """Set up Selenium WebDriver with Chrome in headless mode."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure you have Chrome and chromedriver installed.")
        print("Install chromedriver: brew install chromedriver")
        sys.exit(1)


def scrape_wtn_profile(driver, url, name):
    """
    Scrape WTN ratings from a USTA player profile.

    Args:
        driver: Selenium WebDriver instance
        url: USTA profile URL
        name: Player name (for logging)

    Returns:
        dict: {
            'doubles_rating': str or None,
            'doubles_confidence': str or None,
            'singles_rating': str or None,
            'singles_confidence': str or None,
            'updated_date': str or None
        }
    """
    try:
        print(f"Scraping profile for {name}...")

        # Clear browser state by navigating to about:blank first
        # This forces a fresh load of the profile page
        driver.get("about:blank")
        time.sleep(0.5)

        # Now load the profile URL
        driver.get(url)

        # Wait for the WTN widget sections to be present (this ensures the page has loaded)
        wait = WebDriverWait(driver, 15)

        # Initialize variables
        result = {
            'doubles_rating': None,
            'doubles_confidence': None,
            'singles_rating': None,
            'singles_confidence': None,
            'updated_date': None
        }

        # Try to find WTN ratings on the page
        try:
            # Wait explicitly for WTN widget sections to appear
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "v-form-wtn-widget__section")))
                # Add extra time for all content to load
                time.sleep(2)
            except TimeoutException:
                print(f"  Timeout waiting for WTN widget to load for {name}")
                return result

            # Find all WTN sections (there should be one for doubles and optionally one for singles)
            try:
                wtn_sections = driver.find_elements(By.CLASS_NAME, "v-form-wtn-widget__section")

                for section in wtn_sections:
                    try:
                        # Get the section title (e.g., "WTN DOUBLES" or "WTN SINGLES")
                        title_elem = section.find_element(By.CLASS_NAME, "v-form-wtn-widget__section-title")
                        title = title_elem.text.strip().upper()

                        # Get the rating value (the large number)
                        try:
                            rating_elem = section.find_element(By.CLASS_NAME, "v-form-wtn-widget__section-value")
                            rating = rating_elem.text.strip()
                        except NoSuchElementException:
                            rating = None

                        # Get the confidence level
                        try:
                            conf_elem = section.find_element(By.CLASS_NAME, "v-form-wtn-widget__section-confidence")
                            confidence_text = conf_elem.text.strip()
                            # Extract just "High", "Medium", or "Low" from "High Confidence"
                            confidence = confidence_text.split()[0] if confidence_text else None
                        except NoSuchElementException:
                            confidence = None

                        # Get the updated date (distinct from "Last Played")
                        try:
                            # Find all subtitle elements in this section
                            subtitle_elems = section.find_elements(By.CLASS_NAME, "v-form-wtn-widget__section-subtitle")
                            for subtitle_elem in subtitle_elems:
                                subtitle_text = subtitle_elem.text.strip()
                                if "Updated" in subtitle_text:
                                    # Extract date from "Updated 01/28/2026" format
                                    date_str = subtitle_text.replace("Updated ", "").strip()
                                    # Only set it once (both sections should have the same updated date)
                                    if not result['updated_date']:
                                        result['updated_date'] = date_str
                                    break
                        except NoSuchElementException:
                            pass

                        # Assign to appropriate field based on title
                        if "DOUBLES" in title:
                            result['doubles_rating'] = rating
                            result['doubles_confidence'] = confidence
                        elif "SINGLES" in title:
                            result['singles_rating'] = rating
                            result['singles_confidence'] = confidence

                    except Exception as e:
                        print(f"  Warning: Could not parse section: {e}")
                        continue

            except Exception as e:
                print(f"  Warning: Could not find WTN sections for {name}: {e}")

        except TimeoutException:
            print(f"  Timeout loading profile for {name}")

        return result

    except Exception as e:
        print(f"  Error scraping profile for {name}: {e}")
        return {
            'doubles_rating': None,
            'doubles_confidence': None,
            'singles_rating': None,
            'singles_confidence': None,
            'updated_date': None
        }


def main():
    """Main function to scrape all profiles and append to wtn_ratings.csv."""

    # File paths
    input_csv = "data/wtn_profile_links.csv"
    output_csv = "data/wtn_ratings.csv"

    # Read the profile links CSV file
    print("Reading profile links CSV file...")
    try:
        profiles_df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find {input_csv}")
        sys.exit(1)

    print(f"Found {len(profiles_df)} profiles to scrape")

    # Load existing ratings CSV or create new dataframe
    try:
        ratings_df = pd.read_csv(output_csv)
        print(f"Loaded existing ratings CSV with {len(ratings_df)} records")
    except FileNotFoundError:
        print("Creating new ratings CSV file")
        ratings_df = pd.DataFrame(columns=['Name', 'UAID', 'Date', 'Format', 'Rating', 'Confidence'])

    # List to store new rating records
    new_records = []

    # Set up the web driver
    print("Setting up web driver...")
    driver = setup_driver()

    try:
        # Scrape each profile
        for idx, row in profiles_df.iterrows():
            name = row['Name']
            uaid = row['UAID']
            url = row['WTN_Profile']

            # Scrape the profile
            result = scrape_wtn_profile(driver, url, name)

            # Get the current date for scraping
            scrape_date = datetime.now().strftime("%Y-%m-%d")

            # Use the updated date from the profile if available, otherwise use scrape date
            record_date = result['updated_date'] if result['updated_date'] else scrape_date

            # Create record for doubles rating if available
            if result['doubles_rating']:
                new_records.append({
                    'Name': name,
                    'UAID': uaid,
                    'Date': record_date,
                    'Format': 'Doubles',
                    'Rating': result['doubles_rating'],
                    'Confidence': result['doubles_confidence'] if result['doubles_confidence'] else 'Unknown'
                })

            # Create record for singles rating if available
            if result['singles_rating']:
                new_records.append({
                    'Name': name,
                    'UAID': uaid,
                    'Date': record_date,
                    'Format': 'Singles',
                    'Rating': result['singles_rating'],
                    'Confidence': result['singles_confidence'] if result['singles_confidence'] else 'Unknown'
                })

            print(f"  Doubles: {result['doubles_rating']} ({result['doubles_confidence']})")
            print(f"  Singles: {result['singles_rating']} ({result['singles_confidence']})")
            print(f"  Date: {record_date}")

            # Be polite to the server - add a delay between requests
            time.sleep(2)

            # Save progress every 10 profiles
            if (idx + 1) % 10 == 0:
                # Append new records to ratings dataframe
                if new_records:
                    temp_df = pd.DataFrame(new_records)
                    ratings_df = pd.concat([ratings_df, temp_df], ignore_index=True)
                    ratings_df.to_csv(output_csv, index=False)
                    new_records = []  # Clear the list after saving
                print(f"Progress saved: {idx + 1}/{len(profiles_df)} profiles scraped")

        # Save any remaining records
        if new_records:
            temp_df = pd.DataFrame(new_records)
            ratings_df = pd.concat([ratings_df, temp_df], ignore_index=True)

        # Save final results
        ratings_df.to_csv(output_csv, index=False)
        print(f"\nScraping complete! Results appended to {output_csv}")
        print(f"Total profiles scraped: {len(profiles_df)}")
        print(f"Total records in CSV: {len(ratings_df)}")

        # Count new records by format
        new_doubles = sum(1 for r in new_records if r.get('Format') == 'Doubles')
        new_singles = sum(1 for r in new_records if r.get('Format') == 'Singles')
        print(f"New doubles ratings added: {new_doubles}")
        print(f"New singles ratings added: {new_singles}")

    finally:
        # Close the browser
        driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    main()
