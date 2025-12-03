"""
Analyze and compare .agd files to find metadata differences
"""
import sqlite3
import json
from pathlib import Path


def analyze_agd_file(file_path):
    """
    Analyze .agd file structure and extract metadata

    Args:
        file_path: Path to .agd file

    Returns:
        dict: Dictionary containing all metadata from settings table
    """
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # Get all tables
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print(f"\n=== Tables in {Path(file_path).name} ===")
    print([table[0] for table in tables])

    # Get settings metadata
    settings = dict(
        cursor.execute("SELECT settingName, settingValue FROM settings").fetchall()
    )

    # Get data table schema
    data_schema = cursor.execute("PRAGMA table_info(data)").fetchall()
    print(f"\n=== Data table schema ===")
    for col in data_schema:
        print(f"  {col}")

    conn.close()

    return settings


def compare_agd_files(modified_path, original_path):
    """
    Compare two .agd files and identify differences in metadata

    Args:
        modified_path: Path to modified .agd file
        original_path: Path to original .agd file

    Returns:
        dict: Dictionary of differences
    """
    print("="*80)
    print("ANALYZING MODIFIED FILE")
    print("="*80)
    modified_settings = analyze_agd_file(modified_path)

    print("\n" + "="*80)
    print("ANALYZING ORIGINAL FILE")
    print("="*80)
    original_settings = analyze_agd_file(original_path)

    print("\n" + "="*80)
    print("COMPARING METADATA")
    print("="*80)

    differences = {}
    all_keys = set(modified_settings.keys()) | set(original_settings.keys())

    for key in sorted(all_keys):
        modified_val = modified_settings.get(key, "<NOT PRESENT>")
        original_val = original_settings.get(key, "<NOT PRESENT>")

        if modified_val != original_val:
            differences[key] = {
                "modified": modified_val,
                "original": original_val
            }
            print(f"\n[DIFFERENCE] {key}")
            print(f"  Modified: {modified_val}")
            print(f"  Original: {original_val}")

    if not differences:
        print("\n✓ No differences found in settings metadata")
    else:
        print(f"\n✓ Found {len(differences)} differences")

    return differences


def main():
    # Define file paths
    base_dir = Path("/mnt/c/Users/Alice/OneDrive - 청주대학교/VScode_Repository/agd-gt3x-renamer/Archive")

    modified_agd = base_dir / "modified_MOS2A50130052 (2025-12-02)60sec.agd"
    original_agd = base_dir / "original_MOS2A50130052 (2025-12-02)60sec.agd"

    # Verify files exist
    if not modified_agd.exists():
        print(f"ERROR: Modified file not found: {modified_agd}")
        return
    if not original_agd.exists():
        print(f"ERROR: Original file not found: {original_agd}")
        return

    # Compare files
    differences = compare_agd_files(str(modified_agd), str(original_agd))

    # Save results to JSON
    output_file = base_dir / "agd_differences.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(differences, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
