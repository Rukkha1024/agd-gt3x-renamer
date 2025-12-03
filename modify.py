#!/usr/bin/env python3
"""
ActiGraph 파일 메타데이터 수정 스크립트

.agd 파일 (SQLite)과 .gt3x 파일 (ZIP)의 메타데이터를 수정합니다.

사용 예시:
    # 테스트 모드 (Progress 02 검증용)
    conda run -n module python modify.py --test

    # 프로그래밍 방식 사용 (Progress 04에서 사용)
    from modify import ActiGraphModifier
    modifier = ActiGraphModifier()
    modifier.modify_agd_file(path, metadata)
"""

import argparse
import datetime
import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml


class ActiGraphModifier:
    """ActiGraph 파일 (.agd, .gt3x) 메타데이터 수정 클래스"""

    def __init__(self, config_path: str = "config.yaml"):
        """설정 파일을 로드하고 초기화

        Args:
            config_path: config.yaml 파일 경로
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def datetime_to_ticks(self, dt: datetime.datetime) -> int:
        """datetime을 Windows DateTime.Ticks로 변환

        Args:
            dt: 변환할 datetime 객체

        Returns:
            int: Ticks 값 (100ns 단위, 0001-01-01 기준)

        Example:
            >>> datetime.datetime(1999, 11, 1) -> 630770112000000000
        """
        base = datetime.datetime(1, 1, 1)
        delta = dt - base
        return int(delta.total_seconds() * 10_000_000)

    def ticks_to_datetime(self, ticks: int) -> datetime.datetime:
        """Windows DateTime.Ticks를 datetime으로 변환

        Args:
            ticks: Ticks 값

        Returns:
            datetime: 변환된 datetime 객체

        Example:
            >>> 630770112000000000 -> datetime.datetime(1999, 11, 1)
        """
        base = datetime.datetime(1, 1, 1)
        return base + datetime.timedelta(microseconds=int(ticks) / 10)

    def map_handedness(self, hand: str) -> Tuple[str, str]:
        """손잡이 정보를 side/dominance로 매핑

        ActiGraph는 주손의 반대편 손목에 착용합니다.

        Args:
            hand: "오" (오른손잡이) 또는 "왼" (왼손잡이)

        Returns:
            tuple: (side, dominance)

        Example:
            >>> "오" -> ("Left", "Dominant")  # 오른손잡이는 왼쪽 손목
            >>> "왼" -> ("Right", "Non-Dominant")  # 왼손잡이는 오른쪽 손목
        """
        mapping = self.config['metadata']['handedness_mapping']
        if hand not in mapping:
            raise ValueError(f"Unknown handedness: {hand}. Expected '오' or '왼'")

        return (mapping[hand]['side'], mapping[hand]['dominance'])

    def _create_backup(self, file_path: str) -> str:
        """파일 백업 생성

        Args:
            file_path: 백업할 파일 경로

        Returns:
            str: 백업 파일 경로
        """
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path

    def _restore_backup(self, original_path: str, backup_path: str):
        """백업에서 복원

        Args:
            original_path: 원본 파일 경로
            backup_path: 백업 파일 경로
        """
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, original_path)
            os.remove(backup_path)

    def modify_agd_file(self, file_path: str, metadata: Dict) -> bool:
        """.agd 파일 (SQLite) 메타데이터 수정

        Args:
            file_path: .agd 파일 경로
            metadata: 수정할 메타데이터
                - subjectname: str (이름)
                - sex: str ("Male" or "Female")
                - height: int (cm)
                - mass: int (kg)
                - age: int
                - dateOfBirth: datetime 또는 int (Ticks)
                - hand: str ("오" or "왼") - side/dominance로 자동 변환
                - limb: str (Optional, default "Waist")

        Returns:
            bool: 성공 여부
        """
        backup_path = None
        try:
            # 백업 생성
            backup_path = self._create_backup(file_path)

            # SQLite 연결
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # 필드 매핑
            field_mapping = self.config['metadata']['agd_fields']

            # 메타데이터 준비
            updates = {}

            # 기본 필드
            if 'subjectname' in metadata:
                updates[field_mapping['subjectname']] = str(metadata['subjectname'])

            if 'sex' in metadata:
                updates[field_mapping['sex']] = str(metadata['sex'])

            if 'height' in metadata:
                updates[field_mapping['height']] = str(metadata['height'])

            if 'mass' in metadata:
                updates[field_mapping['mass']] = str(metadata['mass'])

            if 'age' in metadata:
                updates[field_mapping['age']] = str(metadata['age'])

            # dateOfBirth 변환
            if 'dateOfBirth' in metadata:
                dob = metadata['dateOfBirth']
                if isinstance(dob, datetime.datetime):
                    dob_ticks = self.datetime_to_ticks(dob)
                else:
                    dob_ticks = int(dob)
                updates[field_mapping['dateOfBirth']] = str(dob_ticks)

            # 손잡이 매핑
            if 'hand' in metadata:
                side, dominance = self.map_handedness(metadata['hand'])
                updates[field_mapping['side']] = side
                updates[field_mapping['dominance']] = dominance

            # limb 기본값
            if 'limb' in metadata:
                updates[field_mapping['limb']] = str(metadata['limb'])
            else:
                default_limb = self.config['metadata']['defaults']['limb']
                updates[field_mapping['limb']] = default_limb

            # UPDATE 실행
            for field_name, value in updates.items():
                cursor.execute(
                    "UPDATE settings SET settingValue=? WHERE settingName=?",
                    (value, field_name)
                )

            conn.commit()
            conn.close()

            # 백업 삭제
            if backup_path and os.path.exists(backup_path):
                os.remove(backup_path)

            return True

        except Exception as e:
            print(f"❌ Error modifying .agd file: {e}")
            if backup_path:
                self._restore_backup(file_path, backup_path)
            return False

    def _parse_info_txt(self, content: str) -> Dict[str, str]:
        """info.txt 내용 파싱

        Args:
            content: info.txt 문자열

        Returns:
            dict: 키-값 딕셔너리
        """
        info_dict = {}
        for line in content.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
        return info_dict

    def _update_info_txt(self, content: str, metadata: Dict) -> str:
        """info.txt 내용 업데이트

        기존 필드를 업데이트하고, 없는 필드는 적절한 위치에 추가합니다.

        Args:
            content: 원본 info.txt 문자열
            metadata: 수정할 메타데이터

        Returns:
            str: 업데이트된 info.txt 문자열
        """
        lines = content.strip().split('\n')
        field_mapping = self.config['metadata']['gt3x_fields']

        # 업데이트할 값 준비
        updates = {}

        if 'subjectname' in metadata:
            updates[field_mapping['subjectname']] = str(metadata['subjectname'])

        if 'sex' in metadata:
            updates[field_mapping['sex']] = str(metadata['sex'])

        if 'height' in metadata:
            updates[field_mapping['height']] = str(metadata['height'])

        if 'mass' in metadata:
            updates[field_mapping['mass']] = str(metadata['mass'])

        if 'age' in metadata:
            updates[field_mapping['age']] = str(metadata['age'])

        if 'dateOfBirth' in metadata:
            dob = metadata['dateOfBirth']
            if isinstance(dob, datetime.datetime):
                dob_ticks = self.datetime_to_ticks(dob)
            else:
                dob_ticks = int(dob)
            updates[field_mapping['dateOfBirth']] = str(dob_ticks)

        if 'hand' in metadata:
            side, dominance = self.map_handedness(metadata['hand'])
            updates[field_mapping['side']] = side
            updates[field_mapping['dominance']] = dominance

        if 'limb' in metadata:
            updates[field_mapping['limb']] = str(metadata['limb'])
        else:
            default_limb = self.config['metadata']['defaults']['limb']
            updates[field_mapping['limb']] = default_limb

        # 현재 존재하는 필드 파악
        existing_keys = set()
        for line in lines:
            if ':' in line:
                key = line.split(':', 1)[0].strip()
                existing_keys.add(key)

        # 라인별로 업데이트 및 삽입
        updated_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            if ':' in line:
                key = line.split(':', 1)[0].strip()

                # 기존 필드 업데이트
                if key in updates:
                    updated_lines.append(f"{key}: {updates[key]}")
                else:
                    updated_lines.append(line)

                # Sex, Height, Mass, Age는 "Acceleration Max" 다음에 삽입
                if key == "Acceleration Max":
                    for field_key in ['Sex', 'Height', 'Mass', 'Age']:
                        if field_key not in existing_keys and field_key in updates:
                            updated_lines.append(f"{field_key}: {updates[field_key]}")

                # DateOfBirth는 "Dominance" 다음에 삽입
                if key == "Dominance":
                    if 'DateOfBirth' not in existing_keys and 'DateOfBirth' in updates:
                        updated_lines.append(f"DateOfBirth: {updates['DateOfBirth']}")

            else:
                updated_lines.append(line)

            i += 1

        return '\n'.join(updated_lines) + '\n'

    def modify_gt3x_file(self, file_path: str, metadata: Dict) -> bool:
        """.gt3x 파일 (ZIP) 메타데이터 수정

        info.txt만 수정하고 log.bin은 수정하지 않습니다.

        Args:
            file_path: .gt3x 파일 경로
            metadata: 수정할 메타데이터 (modify_agd_file과 동일)

        Returns:
            bool: 성공 여부
        """
        backup_path = None
        try:
            # 백업 생성
            backup_path = self._create_backup(file_path)

            # 임시 디렉토리 생성
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # ZIP 압축 해제
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(temp_path)

                # info.txt 읽기 및 수정
                info_txt_path = temp_path / 'info.txt'
                if not info_txt_path.exists():
                    raise FileNotFoundError("info.txt not found in .gt3x file")

                with open(info_txt_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                updated_content = self._update_info_txt(original_content, metadata)

                with open(info_txt_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                # ZIP 재생성
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file in temp_path.rglob('*'):
                        if file.is_file():
                            arcname = file.relative_to(temp_path)
                            zf.write(file, arcname)

            # 백업 삭제
            if backup_path and os.path.exists(backup_path):
                os.remove(backup_path)

            return True

        except Exception as e:
            print(f"❌ Error modifying .gt3x file: {e}")
            if backup_path:
                self._restore_backup(file_path, backup_path)
            return False

    def validate_agd_modification(self, file_path: str, expected: Dict) -> bool:
        """.agd 파일 수정 검증

        Args:
            file_path: 검증할 .agd 파일 경로
            expected: 예상되는 메타데이터 값

        Returns:
            bool: 모든 필드가 예상값과 일치하면 True
        """
        try:
            conn = sqlite3.connect(file_path)
            settings = dict(
                conn.execute("SELECT settingName, settingValue FROM settings").fetchall()
            )
            conn.close()

            field_mapping = self.config['metadata']['agd_fields']

            for key, expected_value in expected.items():
                field_name = field_mapping.get(key)
                if field_name is None:
                    continue

                actual_value = settings.get(field_name, '')

                # dateOfBirth는 Ticks로 변환하여 비교
                if key == 'dateOfBirth':
                    if isinstance(expected_value, datetime.datetime):
                        expected_value = str(self.datetime_to_ticks(expected_value))
                    else:
                        expected_value = str(expected_value)
                else:
                    expected_value = str(expected_value)

                if actual_value != expected_value:
                    print(f"  ❌ Mismatch in {key}: expected '{expected_value}', got '{actual_value}'")
                    return False

            return True

        except Exception as e:
            print(f"❌ Error validating .agd file: {e}")
            return False

    def validate_gt3x_modification(self, file_path: str, expected: Dict) -> bool:
        """.gt3x 파일 수정 검증

        Args:
            file_path: 검증할 .gt3x 파일 경로
            expected: 예상되는 메타데이터 값

        Returns:
            bool: 모든 필드가 예상값과 일치하면 True
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                info_content = zf.read('info.txt').decode('utf-8')

            info_dict = self._parse_info_txt(info_content)
            field_mapping = self.config['metadata']['gt3x_fields']

            for key, expected_value in expected.items():
                field_name = field_mapping.get(key)
                if field_name is None:
                    continue

                actual_value = info_dict.get(field_name, '')

                # dateOfBirth는 Ticks로 변환하여 비교
                if key == 'dateOfBirth':
                    if isinstance(expected_value, datetime.datetime):
                        expected_value = str(self.datetime_to_ticks(expected_value))
                    else:
                        expected_value = str(expected_value)
                else:
                    expected_value = str(expected_value)

                if actual_value != expected_value:
                    print(f"  ❌ Mismatch in {key}: expected '{expected_value}', got '{actual_value}'")
                    return False

            return True

        except Exception as e:
            print(f"❌ Error validating .gt3x file: {e}")
            return False


def test_modifier():
    """Progress 02 검증용 테스트 함수

    조민석 대상자 데이터로 original 파일을 수정하여
    modified 파일과 일치하는지 검증합니다.
    """
    print("="*80)
    print("Progress 02: ActiGraph 파일 수정 테스트")
    print("="*80)

    # 초기화
    modifier = ActiGraphModifier()

    # 조민석 대상자 메타데이터
    metadata = {
        'subjectname': '조민석',
        'sex': 'Male',
        'height': 177,
        'mass': 70,
        'age': 26,
        'dateOfBirth': datetime.datetime(1999, 11, 1),
        'hand': '오',  # 오른손잡이
        'limb': 'Waist'
    }

    print("\n📋 테스트 메타데이터:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # 파일 경로
    base_dir = Path("Archive")
    original_agd = base_dir / "original_MOS2A50130052 (2025-12-02)60sec.agd"
    original_gt3x = base_dir / "original_MOS2A50130052 (2025-12-02)60sec.gt3x"

    # 테스트용 임시 파일 생성
    temp_dir = Path("temp_test")
    temp_dir.mkdir(exist_ok=True)

    test_agd = temp_dir / "test.agd"
    test_gt3x = temp_dir / "test.gt3x"

    try:
        # .agd 파일 테스트
        print("\n" + "="*80)
        print("테스트 1: .agd 파일 수정")
        print("="*80)

        shutil.copy2(original_agd, test_agd)
        print(f"✓ 원본 파일 복사: {original_agd.name}")

        success = modifier.modify_agd_file(str(test_agd), metadata)
        if success:
            print("✓ .agd 파일 수정 완료")
        else:
            print("❌ .agd 파일 수정 실패")
            return

        # 검증
        expected = {
            'subjectname': '조민석',
            'sex': 'Male',
            'height': 177,
            'mass': 70,
            'age': 26,
            'dateOfBirth': datetime.datetime(1999, 11, 1),
            'side': 'Left',
            'dominance': 'Dominant',
            'limb': 'Waist'
        }

        print("\n검증 중...")
        if modifier.validate_agd_modification(str(test_agd), expected):
            print("✅ .agd 파일 검증 성공! 모든 필드가 일치합니다.")
        else:
            print("❌ .agd 파일 검증 실패")
            return

        # .gt3x 파일 테스트
        print("\n" + "="*80)
        print("테스트 2: .gt3x 파일 수정")
        print("="*80)

        shutil.copy2(original_gt3x, test_gt3x)
        print(f"✓ 원본 파일 복사: {original_gt3x.name}")

        success = modifier.modify_gt3x_file(str(test_gt3x), metadata)
        if success:
            print("✓ .gt3x 파일 수정 완료")
        else:
            print("❌ .gt3x 파일 수정 실패")
            return

        # 검증
        print("\n검증 중...")
        if modifier.validate_gt3x_modification(str(test_gt3x), expected):
            print("✅ .gt3x 파일 검증 성공! 모든 필드가 일치합니다.")
        else:
            print("❌ .gt3x 파일 검증 실패")
            return

        # 단위 테스트
        print("\n" + "="*80)
        print("테스트 3: 단위 테스트")
        print("="*80)

        # Ticks 변환 테스트
        dt = datetime.datetime(1999, 11, 1)
        ticks = modifier.datetime_to_ticks(dt)
        expected_ticks = 630770112000000000

        print(f"\nTicks 변환 테스트:")
        print(f"  입력: {dt}")
        print(f"  출력: {ticks}")
        print(f"  예상: {expected_ticks}")

        if ticks == expected_ticks:
            print("  ✅ Ticks 변환 정확")
        else:
            print("  ❌ Ticks 변환 오류")
            return

        # 역변환 테스트
        dt_back = modifier.ticks_to_datetime(ticks)
        print(f"\n역변환 테스트:")
        print(f"  입력: {ticks}")
        print(f"  출력: {dt_back}")

        if dt_back == dt:
            print("  ✅ 역변환 정확 (bidirectional)")
        else:
            print("  ❌ 역변환 오류")
            return

        # 손잡이 매핑 테스트
        print(f"\n손잡이 매핑 테스트:")
        side_r, dom_r = modifier.map_handedness('오')
        print(f"  오른손잡이 ('오'): side={side_r}, dominance={dom_r}")

        if side_r == 'Left' and dom_r == 'Dominant':
            print("  ✅ 오른손잡이 매핑 정확")
        else:
            print("  ❌ 오른손잡이 매핑 오류")
            return

        side_l, dom_l = modifier.map_handedness('왼')
        print(f"  왼손잡이 ('왼'): side={side_l}, dominance={dom_l}")

        if side_l == 'Right' and dom_l == 'Non-Dominant':
            print("  ✅ 왼손잡이 매핑 정확")
        else:
            print("  ❌ 왼손잡이 매핑 오류")
            return

        # 전체 성공
        print("\n" + "="*80)
        print("🎉 모든 테스트 통과!")
        print("="*80)
        print("\n✅ Progress 02 완료:")
        print("  - .agd 파일 수정 및 검증 성공")
        print("  - .gt3x 파일 수정 및 검증 성공")
        print("  - 모든 단위 테스트 통과")
        print("\n📁 테스트 파일 위치:")
        print(f"  {test_agd}")
        print(f"  {test_gt3x}")
        print("\n다음: ActiLife에서 파일을 열어 수동 검증하세요.")

    finally:
        # 정리는 하지 않음 (수동 검증용)
        pass


def main():
    parser = argparse.ArgumentParser(
        description="ActiGraph 파일 메타데이터 수정",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Progress 02 검증 테스트 실행'
    )

    args = parser.parse_args()

    if args.test:
        test_modifier()
    else:
        print("사용법: python modify.py --test")
        print("\nProgress 04에서는 프로그래밍 방식으로 import하여 사용합니다.")
        sys.exit(1)


if __name__ == '__main__':
    main()
