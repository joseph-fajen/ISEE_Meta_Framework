#!/usr/bin/env python3
"""
Script to extend weekly organization to all months (not just July)
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

def extend_weekly_structure():
    output_dir = "/Users/josephfajen/git/ISEE_Meta_Framework/data/output"
    os.chdir(output_dir)
    
    moves_log = []
    
    # Process each month that needs weekly subfolders
    for month_dir in ['2025-05', '2025-06', '2025-08']:
        if not os.path.exists(month_dir):
            continue
            
        print(f"\nProcessing {month_dir}...")
        
        # Create weekly subdirectories
        for week in range(1, 6):
            week_dir = os.path.join(month_dir, f"week{week}")
            os.makedirs(week_dir, exist_ok=True)
        
        # Find all run folders in this month
        run_folders = glob.glob(f"{month_dir}/run_*")
        
        for folder_path in run_folders:
            folder_name = os.path.basename(folder_path)
            
            try:
                # Extract date from folder name: run_YYYYMMDD_HHMMSS
                date_part = folder_name.split('_')[1]  # YYYYMMDD
                week_num = get_week_of_month(date_part)
                
                # Move to appropriate week subfolder
                week_dir = f"{month_dir}/week{week_num}"
                dest_path = os.path.join(week_dir, folder_name)
                
                print(f"  Moving {folder_path} -> {dest_path}")
                shutil.move(folder_path, dest_path)
                moves_log.append(f"{folder_path} -> {dest_path}")
                
            except (IndexError, ValueError) as e:
                print(f"  Error processing folder {folder_name}: {e}")
                continue
    
    # Update the organization log
    with open("organization_log.txt", "a") as f:
        f.write(f"\n\nWeekly Extension - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        for move in moves_log:
            f.write(f"{move}\n")
    
    print(f"\nWeekly extension complete! Moved {len(moves_log)} folders.")
    print("Updated organization_log.txt")

if __name__ == "__main__":
    extend_weekly_structure()