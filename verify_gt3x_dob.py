"""
verify_gt3x_dob.py

Purpose: Verify the correct DateOfBirth format for .gt3x files
         to ensure compatibility with ActiLife software.

This script creates two test files:
  - test_dob_ticks.gt3x: DateOfBirth as Windows Ticks integer
  - test_dob_string.gt3x: DateOfBirth as String format (MM/DD/YYYY)

After running, open both files in ActiLife to determine which format is correct.
"""

import os
import shutil
import zipfile
import datetime
import tempfile
from pathlib import Path


def datetime_to_ticks(dt: datetime.datetime) -> int:
    """
    Convert datetime to Windows Ticks.
    Ticks = number of 100-nanosecond intervals since 0001-01-01 00:00:00.
    """
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    ticks = int(delta.total_seconds() * 10_000_000)
    return ticks


def ticks_to_datetime(ticks: int) -> datetime.datetime:
    """
    Convert Windows Ticks to datetime.
    """
    base = datetime.datetime(1, 1, 1)
    dt = base + datetime.timedelta(microseconds=int(ticks) / 10)
    return dt


def read_info_txt(info_path: str) -> dict:
    """
    Read info.txt and return as a dictionary.
    """
    info_dict = {}
    with open(info_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
    return info_dict


def write_info_txt(info_path: str, info_dict: dict):
    """
    Write dictionary back to info.txt format.
    """
    with open(info_path, 'w', encoding='utf-8') as f:
        for key, value in info_dict.items():
            f.write(f"{key}: {value}\n")


def modify_gt3x_dob(source_gt3x: str, output_gt3x: str, dob_value: str):
    """
    Modify the DateOfBirth field in a .gt3x file.
    
    Args:
        source_gt3x: Path to the source .gt3x file
        output_gt3x: Path to save the modified .gt3x file
        dob_value: The DateOfBirth value to set (ticks or string)
    """
    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the .gt3x file (it's a zip archive)
        with zipfile.ZipFile(source_gt3x, 'r') as zf:
            zf.extractall(temp_dir)
        
        # Find and modify info.txt
        info_path = os.path.join(temp_dir, 'info.txt')
        if not os.path.exists(info_path):
            raise FileNotFoundError(f"info.txt not found in {source_gt3x}")
        
        # Read current info.txt
        info_dict = read_info_txt(info_path)
        
        # Set the DateOfBirth value
        info_dict['DateOfBirth'] = dob_value
        
        # Write back info.txt
        write_info_txt(info_path, info_dict)
        
        # Re-create the .gt3x file (zip archive)
        with zipfile.ZipFile(output_gt3x, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zf.write(file_path, arcname)


def main():
    print("=" * 70)
    print(" GT3X DateOfBirth Format Verification Script")
    print("=" * 70)
    print()
    
    # Setup paths
    script_dir = Path(__file__).parent
    temp_test_dir = script_dir / "temp_test"
    
    # Find existing .gt3x file in temp_test
    gt3x_files = list(temp_test_dir.glob("*.gt3x"))
    
    if not gt3x_files:
        print("[ERROR] No .gt3x file found in temp_test directory.")
        print(f"        Please place a .gt3x file in: {temp_test_dir}")
        return
    
    source_gt3x = gt3x_files[0]
    print(f"[INFO] Found source file: {source_gt3x.name}")
    print()
    
    # Test date: 1990-01-01
    test_date = datetime.datetime(1990, 1, 1)
    
    # Calculate ticks for 1990-01-01
    ticks_value = datetime_to_ticks(test_date)
    
    # String format: MM/DD/YYYY
    string_value = "01/01/1990"
    
    print(f"[INFO] Test Date: {test_date.strftime('%Y-%m-%d')}")
    print(f"       Ticks value: {ticks_value}")
    print(f"       String value: {string_value}")
    print()
    
    # Create output paths
    output_ticks = temp_test_dir / "test_dob_ticks.gt3x"
    output_string = temp_test_dir / "test_dob_string.gt3x"
    
    # Test Case A: Ticks format
    print("[STEP 1] Creating test_dob_ticks.gt3x with Ticks format...")
    try:
        modify_gt3x_dob(str(source_gt3x), str(output_ticks), str(ticks_value))
        print(f"         Created: {output_ticks}")
    except Exception as e:
        print(f"[ERROR] Failed to create test_dob_ticks.gt3x: {e}")
        return
    
    # Test Case B: String format
    print("[STEP 2] Creating test_dob_string.gt3x with String format...")
    try:
        modify_gt3x_dob(str(source_gt3x), str(output_string), string_value)
        print(f"         Created: {output_string}")
    except Exception as e:
        print(f"[ERROR] Failed to create test_dob_string.gt3x: {e}")
        return
    
    print()
    print("=" * 70)
    print(" VERIFICATION INSTRUCTIONS")
    print("=" * 70)
    print()
    print("Two test files have been created in the temp_test directory:")
    print()
    print(f"  1. test_dob_ticks.gt3x  - DateOfBirth = {ticks_value} (Windows Ticks)")
    print(f"  2. test_dob_string.gt3x - DateOfBirth = '{string_value}' (String)")
    print()
    print("Please perform the following steps:")
    print()
    print("  [A] Open ActiLife software")
    print()
    print("  [B] Import/Open 'test_dob_ticks.gt3x'")
    print("      - Check the Subject Information")
    print("      - Note if Date of Birth displays as: 1990-01-01 (or Jan 1, 1990)")
    print()
    print("  [C] Import/Open 'test_dob_string.gt3x'")
    print("      - Check the Subject Information")
    print("      - Note if Date of Birth displays as: 1990-01-01 (or Jan 1, 1990)")
    print()
    print("  [D] Report which file shows the CORRECT Date of Birth:")
    print()
    print("      * If test_dob_ticks.gt3x is correct  -> Ticks format is required")
    print("      * If test_dob_string.gt3x is correct -> String format is required")
    print("      * If BOTH are correct                -> Either format works")
    print("      * If NEITHER is correct              -> Different format may be needed")
    print()
    print("=" * 70)
    print()
    
    # Additional: Show the info.txt content from each file for debugging
    print("[DEBUG] Verifying created files...")
    print()
    
    for test_file, format_name in [(output_ticks, "Ticks"), (output_string, "String")]:
        print(f"  {format_name} format ({test_file.name}):")
        try:
            with zipfile.ZipFile(test_file, 'r') as zf:
                with zf.open('info.txt') as f:
                    content = f.read().decode('utf-8')
                    # Find DateOfBirth line
                    for line in content.split('\n'):
                        if 'DateOfBirth' in line:
                            print(f"    -> {line.strip()}")
                            break
        except Exception as e:
            print(f"    [ERROR] Could not read: {e}")
        print()
    
    print("Script completed. Please test in ActiLife and report your findings.")


if __name__ == "__main__":
    main()
