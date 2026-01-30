#!/usr/bin/env python3
"""
Remove duplicate rows from the bad scraping run.
Keep rows where rating is 34.21 ONLY if the player has no other entry for that date/format.
"""

import pandas as pd

# Read the CSV
df = pd.read_csv('data/wtn_ratings.csv')

print(f"Total rows before cleaning: {len(df)}")

# Find rows with date 01/28/2026 and rating 34.21
bad_scrape_mask = (df['Date'] == '01/28/2026') & (df['Rating'] == 34.21)
bad_scrape_df = df[bad_scrape_mask]

print(f"Rows with 34.21 rating on 01/28/2026: {len(bad_scrape_df)}")

# For each player with 34.21, check if they have another entry for the same date and format
rows_to_remove = []

for idx, row in bad_scrape_df.iterrows():
    name = row['Name']
    date = row['Date']
    format_type = row['Format']

    # Find all rows for this player with same date and format
    same_player_mask = (df['Name'] == name) & (df['Date'] == date) & (df['Format'] == format_type)
    same_player_df = df[same_player_mask]

    # If there are multiple rows and one is 34.21, remove the 34.21 one
    if len(same_player_df) > 1:
        # Check if there's a non-34.21 entry
        non_bad_entries = same_player_df[same_player_df['Rating'] != 34.21]
        if len(non_bad_entries) > 0:
            # Keep the non-34.21 entry, remove this 34.21 entry
            rows_to_remove.append(idx)
            print(f"Removing duplicate 34.21 for {name} (has correct value: {non_bad_entries.iloc[0]['Rating']})")
    else:
        # Only one entry - this is the actual rating, keep it
        print(f"Keeping 34.21 for {name} (no duplicate found)")

# Remove the identified rows
df_cleaned = df.drop(rows_to_remove)

print(f"\nTotal rows removed: {len(rows_to_remove)}")
print(f"Total rows after cleaning: {len(df_cleaned)}")

# Save the cleaned CSV
df_cleaned.to_csv('data/wtn_ratings.csv', index=False)
print("\nCleaned CSV saved!")
