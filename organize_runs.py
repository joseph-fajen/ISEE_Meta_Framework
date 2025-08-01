#!/usr/bin/env python3
"""
Script to organize ISEE run folders by month and week
"""
import os
import shutil
from datetime import datetime
import glob

def get_week_of_month(date_str):
    """Convert YYYYMMDD to week number within month (1-5)"""
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    
    date_obj = datetime(year, month, day)
    first_day = datetime(year, month, 1)
    
    # Calculate week number (1-based)
    days_from_start = (date_obj - first_day).days
    week_num = (days_from_start // 7) + 1
    
    return min(week_num, 5)  # Cap at week 5 for end-of-month runs

def organize_runs():
    output_dir = "/Users/josephfajen/git/ISEE_Meta_Framework/data/output"
    os.chdir(output_dir)
    
    # Find all run folders
    run_folders = glob.glob("run_*")
    run_folders.sort()
    
    moves_log = []
    
    for folder in run_folders:
        if not os.path.isdir(folder):
            continue
            
        # Extract date from folder name: run_YYYYMMDD_HHMMSS
        try:
            date_part = folder.split('_')[1]  # YYYYMMDD
            year_month = date_part[:6]  # YYYYMM
            
            # Determine destination
            if year_month in ['202505', '202506', '202508']:
                # Simple monthly structure for lighter months
                dest_dir = f"20{year_month[2:4]}-{year_month[4:6]}"
            elif year_month == '202507':
                # Weekly structure for July
                week_num = get_week_of_month(date_part)
                dest_dir = f"2025-07/week{week_num}"
            else:
                print(f"Unexpected date format in folder: {folder}")
                continue
                
            # Move folder
            dest_path = os.path.join(dest_dir, folder)
            print(f"Moving {folder} -> {dest_path}")
            shutil.move(folder, dest_path)
            moves_log.append(f"{folder} -> {dest_path}")
            
        except (IndexError, ValueError) as e:
            print(f"Error processing folder {folder}: {e}")
            continue
    
    # Save moves log for undo capability
    with open("organization_log.txt", "w") as f:
        f.write("ISEE Run Organization Log\n")
        f.write("=" * 30 + "\n\n")
        for move in moves_log:
            f.write(f"{move}\n")
    
    print(f"\nOrganization complete! Moved {len(moves_log)} folders.")
    print("Log saved to organization_log.txt")

if __name__ == "__main__":
    organize_runs()