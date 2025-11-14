#!/usr/bin/env python3
"""
ActiGraph 파일 자동 이름 변경 스크립트

파일명 형식:
  기존: 고유번호 (날짜).확장자
  변경: 고유번호_이름 (날짜).확장자

사용 예시:
  python rename_actigraph_files.py --week "40주차" --dry-run
  python rename_actigraph_files.py --week "40주차" --year 2025
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
import yaml


class ActiGraphRenamer:
    def __init__(self, config_path: str = "config.yaml"):
        """설정 파일을 로드하고 초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.serial_mapping_df = None
        self.subject_info_df = None
        
    def load_data(self, year: int):
        """Excel 파일에서 데이터 로드"""
        print("📂 데이터 로드 중...")
        
        # 관리번호-시리얼번호 매칭 데이터
        serial_path = self.config['paths']['serial_mapping']
        self.serial_mapping_df = pd.read_excel(serial_path)
        print(f"  ✓ 관리번호-시리얼번호 매칭: {len(self.serial_mapping_df)} 건")
        
        # 대상자 정보 데이터 (연도별 시트)
        subject_path = self.config['paths']['subject_info']
        self.subject_info_df = pd.read_excel(subject_path, sheet_name=str(year))
        print(f"  ✓ 대상자 정보 ({year}년): {len(self.subject_info_df)} 건")
        
    def extract_serial_from_filename(self, filename: str) -> Optional[str]:
        """파일명에서 고유번호 추출
        
        예: "MOS2D36155148 (2025-11-13).gt3x" -> "MOS2D36155148"
        """
        match = re.match(r'^([A-Z0-9]+)\s*\(', filename)
        if match:
            return match.group(1)
        return None
    
    def is_already_renamed(self, filename: str) -> bool:
        """이미 이름이 변경된 파일인지 확인
        
        파일명에 '_'와 한글이 포함되어 있으면 이미 변경된 것으로 판단
        """
        korean_pattern = re.compile(r'[가-힣]')
        return '_' in filename and korean_pattern.search(filename) is not None
    
    def get_management_number(self, serial_number: str) -> Optional[int]:
        """고유번호로 관리번호 조회"""
        col_serial = self.config['columns']['serial_mapping']['serial_number']
        col_mgmt = self.config['columns']['serial_mapping']['management_number']
        
        result = self.serial_mapping_df[
            self.serial_mapping_df[col_serial] == serial_number
        ]
        
        if len(result) == 0:
            return None
        
        return int(result.iloc[0][col_mgmt])
    
    def get_subject_name(self, management_number: int, division: str) -> Optional[str]:
        """관리번호와 구분으로 대상자 이름 조회"""
        col_mgmt = self.config['columns']['subject_info']['management_number']
        col_div = self.config['columns']['subject_info']['division']
        col_name = self.config['columns']['subject_info']['name']
        
        result = self.subject_info_df[
            (self.subject_info_df[col_mgmt] == management_number) &
            (self.subject_info_df[col_div] == division)
        ]
        
        if len(result) == 0:
            return None
        
        if len(result) > 1:
            print(f"  ⚠️  경고: 관리번호 {management_number}, 구분 {division}에 {len(result)}개의 매칭 발견")
        
        return str(result.iloc[0][col_name])
    
    def generate_new_filename(self, old_filename: str, name: str) -> str:
        """새 파일명 생성
        
        예: "MOS2D36155148 (2025-11-13).gt3x" + "김선옥" 
            -> "MOS2D36155148_김선옥 (2025-11-13).gt3x"
        """
        match = re.match(r'^([A-Z0-9]+)(\s*\(.+)$', old_filename)
        if match:
            serial = match.group(1)
            rest = match.group(2)
            return f"{serial}_{name}{rest}"
        return old_filename
    
    def process_file(self, filepath: Path, division: str, dry_run: bool = False) -> Tuple[bool, str]:
        """단일 파일 처리
        
        Returns:
            (성공 여부, 메시지)
        """
        filename = filepath.name
        
        # 이미 변경된 파일은 건너뛰기
        if self.is_already_renamed(filename):
            return False, "이미 변경됨"
        
        # 고유번호 추출
        serial_number = self.extract_serial_from_filename(filename)
        if not serial_number:
            return False, "고유번호 추출 실패"
        
        # 관리번호 조회
        management_number = self.get_management_number(serial_number)
        if management_number is None:
            return False, f"관리번호 찾을 수 없음 (고유번호: {serial_number})"
        
        # 이름 조회
        name = self.get_subject_name(management_number, division)
        if name is None:
            return False, f"이름 찾을 수 없음 (관리번호: {management_number}, 구분: {division})"
        
        # 새 파일명 생성
        new_filename = self.generate_new_filename(filename, name)
        new_filepath = filepath.parent / new_filename
        
        # 파일 변경
        if not dry_run:
            try:
                filepath.rename(new_filepath)
                return True, f"변경 완료: {filename} -> {new_filename}"
            except Exception as e:
                return False, f"파일 변경 실패: {str(e)}"
        else:
            return True, f"[DRY-RUN] {filename} -> {new_filename}"
    
    def run(self, division: str, year: int = None, dry_run: bool = False):
        """전체 프로세스 실행"""
        if year is None:
            year = self.config['defaults']['year']
        
        print(f"\n{'='*60}")
        print(f"ActiGraph 파일 자동 이름 변경")
        print(f"{'='*60}")
        print(f"📅 연도: {year}")
        print(f"📌 구분: {division}")
        print(f"🔍 모드: {'DRY-RUN (미리보기)' if dry_run else '실제 변경'}")
        print(f"{'='*60}\n")
        
        # 데이터 로드
        self.load_data(year)
        
        # 대상 디렉토리
        target_dir = Path(self.config['paths']['target_directory'])
        if not target_dir.exists():
            print(f"❌ 오류: 디렉토리를 찾을 수 없습니다: {target_dir}")
            return
        
        # 처리 대상 파일 찾기
        extensions = self.config['file_extensions']
        files = []
        for ext in extensions:
            files.extend(target_dir.glob(f"*{ext}"))
        
        if not files:
            print(f"❌ 처리할 파일이 없습니다. (확장자: {', '.join(extensions)})")
            return
        
        print(f"📁 발견된 파일: {len(files)}개\n")
        
        # 파일 처리
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for filepath in sorted(files):
            success, message = self.process_file(filepath, division, dry_run)
            
            if success:
                print(f"✅ {message}")
                success_count += 1
            else:
                if "이미 변경됨" in message:
                    print(f"⏭️  {filepath.name}: {message}")
                    skip_count += 1
                else:
                    print(f"❌ {filepath.name}: {message}")
                    error_count += 1
        
        # 결과 요약
        print(f"\n{'='*60}")
        print(f"📊 처리 결과")
        print(f"{'='*60}")
        print(f"✅ 성공: {success_count}개")
        print(f"⏭️  건너뜀: {skip_count}개")
        print(f"❌ 실패: {error_count}개")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ActiGraph 파일 자동 이름 변경",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # Dry-run 모드로 미리보기
  python rename_actigraph_files.py --week "40주차" --dry-run
  
  # 실제 파일 변경 (2025년)
  python rename_actigraph_files.py --week "40주차" --year 2025
  
  # 다른 주차 처리
  python rename_actigraph_files.py --week "1주차" --year 2024
        """
    )
    
    parser.add_argument(
        '--week', '--division',
        required=True,
        help='구분 값 (예: "40주차", "1주차")'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        help='연도 (기본값: config.yaml의 defaults.year)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 변경 없이 미리보기만 수행'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='설정 파일 경로 (기본값: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # 실행
    try:
        renamer = ActiGraphRenamer(args.config)
        renamer.run(
            division=args.week,
            year=args.year,
            dry_run=args.dry_run
        )
    except FileNotFoundError as e:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
