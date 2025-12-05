"""
Analyze and compare .gt3x files to find metadata differences
"""
import zipfile
import json
import re
from pathlib import Path


def parse_info_txt(info_content):
    """
    Parse info.txt content into a dictionary

    Args:
        info_content: String content of info.txt

    Returns:
        dict: Parsed key-value pairs
    """
    info_dict = {}
    for line in info_content.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            info_dict[key.strip()] = value.strip()
    return info_dict


def find_metadata_json(log_bin):
    """
    Find and extract METADATA JSON from log.bin

    Args:
        log_bin: Binary content of log.bin

    Returns:
        dict: Parsed metadata JSON or None if not found
    """
    try:
        # Look for JSON pattern in log.bin
        # The METADATA packet contains UTF-8 encoded JSON
        # Pattern: {"MetadataType" ... }

        # Find all potential JSON objects
        json_pattern = rb'\{[^\}]*"MetadataType"[^\}]*\}'
        matches = re.findall(json_pattern, log_bin, re.DOTALL)

        if not matches:
            # Try broader search
            idx = log_bin.find(b'{"MetadataType"')
            if idx == -1:
                return None

            # Find the end of JSON object
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
                        return json.loads(json_bytes.decode('utf-8'))
            return None

        # Parse the first match
        for match in matches:
            try:
                metadata = json.loads(match.decode('utf-8'))
                if metadata.get('MetadataType') == 'Bio':
                    return metadata
            except:
                continue

        # If no Bio metadata found, return first valid JSON
        for match in matches:
            try:
                return json.loads(match.decode('utf-8'))
            except:
                continue

    except Exception as e:
        print(f"  Warning: Could not extract metadata JSON: {e}")
        return None


def analyze_gt3x_file(file_path):
    """
    Analyze .gt3x file structure and extract metadata

    Args:
        file_path: Path to .gt3x file

    Returns:
        dict: Dictionary containing metadata from info.txt and log.bin
    """
    result = {
        'info_txt': {},
        'metadata_json': None
    }

    with zipfile.ZipFile(file_path, 'r') as zf:
        # List all files in the archive
        print(f"\n=== Files in {Path(file_path).name} ===")
        for name in zf.namelist():
            print(f"  {name}")

        # Read info.txt
        if 'info.txt' in zf.namelist():
            info_content = zf.read('info.txt').decode('utf-8')
            result['info_txt'] = parse_info_txt(info_content)
            print(f"\n=== info.txt content ===")
            for key, value in result['info_txt'].items():
                print(f"  {key}: {value}")
        else:
            print("  Warning: info.txt not found")

        # Read log.bin and extract metadata
        if 'log.bin' in zf.namelist():
            log_bin = zf.read('log.bin')
            print(f"\n=== log.bin size: {len(log_bin)} bytes ===")

            result['metadata_json'] = find_metadata_json(log_bin)
            if result['metadata_json']:
                print(f"\n=== METADATA JSON found ===")
                print(json.dumps(result['metadata_json'], indent=2, ensure_ascii=False))
            else:
                print("  Warning: METADATA JSON not found")
        else:
            print("  Warning: log.bin not found")

    return result


def compare_gt3x_files(modified_path, original_path):
    """
    Compare two .gt3x files and identify differences in metadata

    Args:
        modified_path: Path to modified .gt3x file
        original_path: Path to original .gt3x file

    Returns:
        dict: Dictionary of differences
    """
    print("="*80)
    print("ANALYZING MODIFIED FILE")
    print("="*80)
    modified_data = analyze_gt3x_file(modified_path)

    print("\n" + "="*80)
    print("ANALYZING ORIGINAL FILE")
    print("="*80)
    original_data = analyze_gt3x_file(original_path)

    print("\n" + "="*80)
    print("COMPARING METADATA")
    print("="*80)

    differences = {
        'info_txt': {},
        'metadata_json': {}
    }

    # Compare info.txt
    print("\n--- info.txt differences ---")
    all_info_keys = set(modified_data['info_txt'].keys()) | set(original_data['info_txt'].keys())
    for key in sorted(all_info_keys):
        modified_val = modified_data['info_txt'].get(key, "<NOT PRESENT>")
        original_val = original_data['info_txt'].get(key, "<NOT PRESENT>")

        if modified_val != original_val:
            differences['info_txt'][key] = {
                "modified": modified_val,
                "original": original_val
            }
            print(f"\n[DIFFERENCE] {key}")
            print(f"  Modified: {modified_val}")
            print(f"  Original: {original_val}")

    if not differences['info_txt']:
        print("\n✓ No differences found in info.txt")

    # Compare metadata JSON
    print("\n--- METADATA JSON differences ---")
    if modified_data['metadata_json'] and original_data['metadata_json']:
        all_json_keys = set(modified_data['metadata_json'].keys()) | set(original_data['metadata_json'].keys())
        for key in sorted(all_json_keys):
            modified_val = modified_data['metadata_json'].get(key, "<NOT PRESENT>")
            original_val = original_data['metadata_json'].get(key, "<NOT PRESENT>")

            if modified_val != original_val:
                differences['metadata_json'][key] = {
                    "modified": modified_val,
                    "original": original_val
                }
                print(f"\n[DIFFERENCE] {key}")
                print(f"  Modified: {modified_val}")
                print(f"  Original: {original_val}")

        if not differences['metadata_json']:
            print("\n✓ No differences found in METADATA JSON")
    else:
        print("  Warning: Cannot compare METADATA JSON (one or both not found)")

    total_diff = len(differences['info_txt']) + len(differences['metadata_json'])
    print(f"\n✓ Found {total_diff} total differences")

    return differences


def main():
    # Define file paths
    base_dir = Path("/mnt/c/Users/Alice/OneDrive - 청주대학교/VScode_Repository/agd-gt3x-renamer/Archive")

    modified_gt3x = base_dir / "modified_MOS2A50130052 (2025-12-02)60sec.gt3x"
    original_gt3x = base_dir / "original_MOS2A50130052 (2025-12-02)60sec.gt3x"

    # Verify files exist
    if not modified_gt3x.exists():
        print(f"ERROR: Modified file not found: {modified_gt3x}")
        return
    if not original_gt3x.exists():
        print(f"ERROR: Original file not found: {original_gt3x}")
        return

    # Compare files
    differences = compare_gt3x_files(str(modified_gt3x), str(original_gt3x))

    # Save results to JSON
    output_file = base_dir / "gt3x_differences.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(differences, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
