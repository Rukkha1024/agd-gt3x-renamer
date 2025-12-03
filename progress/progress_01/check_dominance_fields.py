"""
Check if Side and Dominance fields exist in .agd and .gt3x files
"""
import sqlite3
import zipfile
import json
from pathlib import Path


def check_agd_dominance(file_path):
    """Check Side and Dominance in .agd file"""
    print(f"\n{'='*80}")
    print(f"Checking {Path(file_path).name}")
    print('='*80)

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # Get all settings
    settings = dict(
        cursor.execute("SELECT settingName, settingValue FROM settings").fetchall()
    )

    # Look for side/dominance related fields
    print("\n=== Searching for side/dominance fields ===")
    found = False
    for key, value in sorted(settings.items()):
        if 'side' in key.lower() or 'dominance' in key.lower() or 'limb' in key.lower():
            print(f"  {key}: {value}")
            found = True

    if not found:
        print("  No side/dominance/limb fields found in settings table")

    conn.close()
    return settings


def check_gt3x_dominance(file_path):
    """Check Side and Dominance in .gt3x file"""
    print(f"\n{'='*80}")
    print(f"Checking {Path(file_path).name}")
    print('='*80)

    with zipfile.ZipFile(file_path, 'r') as zf:
        # Check info.txt
        print("\n=== info.txt ===")
        if 'info.txt' in zf.namelist():
            info_content = zf.read('info.txt').decode('utf-8')
            for line in info_content.split('\n'):
                if any(keyword in line for keyword in ['Side', 'Dominance', 'Limb', 'Race']):
                    print(f"  {line}")

        # Check METADATA JSON
        print("\n=== METADATA JSON ===")
        if 'log.bin' in zf.namelist():
            log_bin = zf.read('log.bin')
            idx = log_bin.find(b'{"MetadataType"')
            if idx != -1:
                # Find end of JSON
                depth = 0
                start = idx
                for i in range(idx, len(log_bin)):
                    if log_bin[i:i+1] == b'{':
                        depth += 1
                    elif log_bin[i:i+1] == b'}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            json_bytes = log_bin[start:end]
                            metadata = json.loads(json_bytes.decode('utf-8'))
                            print(json.dumps(metadata, indent=2, ensure_ascii=False))
                            break


def main():
    base_dir = Path("/mnt/c/Users/Alice/OneDrive - 청주대학교/VScode_Repository/agd-gt3x-renamer/Archive")

    # Check both modified and original files
    files = [
        ("modified_MOS2A50130052 (2025-12-02)60sec.agd", check_agd_dominance),
        ("original_MOS2A50130052 (2025-12-02)60sec.agd", check_agd_dominance),
        ("modified_MOS2A50130052 (2025-12-02)60sec.gt3x", check_gt3x_dominance),
        ("original_MOS2A50130052 (2025-12-02)60sec.gt3x", check_gt3x_dominance),
    ]

    for filename, check_func in files:
        file_path = base_dir / filename
        if file_path.exists():
            check_func(str(file_path))
        else:
            print(f"\nERROR: File not found: {file_path}")


if __name__ == "__main__":
    main()
