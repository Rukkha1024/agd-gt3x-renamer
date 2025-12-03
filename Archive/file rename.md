<name.py>
#!/usr/bin/env python3
"""
ActiGraph 파일 자동 이름 변경 스크립트

파일명 형식:
  기존: 고유번호 (날짜).확장자
  변경: ID_이름 (날짜).확장자

기본 사용 (2025년 기본값)
conda run -n module python name.py --week 40주차

미리보기 모드
conda run -n module python name.py --week 40주차 --dry
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
    
    def extract_info_from_renamed_file(self, filename: str) -> Optional[Tuple[str, str, str]]:
        """이미 변경된 파일명에서 ID, 이름, 날짜 추출
        
        예: "JB54017302_김선옥 (2025-11-08).gt3x" -> ("JB54017302", "김선옥", "2025-11-08")
        """
        match = re.match(r'^([A-Z0-9]+)_([가-힣]+)\s*\((\d{4}-\d{2}-\d{2})\)', filename)
        if match:
            return (match.group(1), match.group(2), match.group(3))
        return None
    
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
    
    def get_subject_info(self, management_number: int, division: str) -> Optional[Tuple[str, str, str]]:
        """관리번호와 구분으로 대상자 ID, 이름, 착용시작일 조회
        
        Returns:
            (ID, 이름, 착용시작일) 튜플 또는 None
        """
        col_mgmt = self.config['columns']['subject_info']['management_number']
        col_div = self.config['columns']['subject_info']['division']
        col_id = self.config['columns']['subject_info']['id']
        col_name = self.config['columns']['subject_info']['name']
        col_wear_date = self.config['columns']['subject_info']['wear_start_date']
        
        result = self.subject_info_df[
            (self.subject_info_df[col_mgmt] == management_number) &
            (self.subject_info_df[col_div] == division)
        ]
        
        if len(result) == 0:
            return None
        
        if len(result) > 1:
            print(f"  ⚠️  경고: 관리번호 {management_number}, 구분 {division}에 {len(result)}개의 매칭 발견")
        
        subject_id = str(result.iloc[0][col_id])
        subject_name = str(result.iloc[0][col_name])
        wear_start_date = result.iloc[0][col_wear_date]
        
        # 날짜 형식 변환
        try:
            wear_date_str = pd.to_datetime(wear_start_date).strftime('%Y-%m-%d')
        except Exception as e:
            print(f"  ⚠️  경고: 착용 시작일 변환 실패 ({wear_start_date}): {e}")
            return None
        
        return (subject_id, subject_name, wear_date_str)
    
    def generate_new_filename(self, old_filename: str, subject_id: str, name: str, wear_date: str) -> str:
        """새 파일명 생성
        
        예: "MOS2D36155148 (2025-11-13).gt3x" + "JB54017302" + "김선옥" + "2025-11-08"
            -> "JB54017302_김선옥 (2025-11-08).gt3x"
        예: "JB54017302_김선옥 (2025-11-13)60sec.agd" + "JB54017302" + "김선옥" + "2025-11-08"
            -> "JB54017302_김선옥 (2025-11-08)60sec.agd"
        """
        # 원본 형식: 고유번호 (날짜).확장자
        match1 = re.match(r'^[A-Z0-9]+\s*\([^)]+\)(.*)$', old_filename)
        if match1:
            suffix = match1.group(1)
            return f"{subject_id}_{name} ({wear_date}){suffix}"
        
        # 이미 변경된 형식: ID_이름 (날짜).확장자
        match2 = re.match(r'^[A-Z0-9]+_[가-힣]+\s*\([^)]+\)(.*)$', old_filename)
        if match2:
            suffix = match2.group(1)
            return f"{subject_id}_{name} ({wear_date}){suffix}"
        
        return old_filename
    
    def process_file(self, filepath: Path, division: str, dry_run: bool = False) -> Tuple[bool, str]:
        """단일 파일 처리
        
        Returns:
            (성공 여부, 메시지)
        """
        filename = filepath.name
        
        # 이미 변경된 파일인지 확인
        renamed_info = self.extract_info_from_renamed_file(filename)
        
        # 고유번호 추출 (원본 파일 또는 변경된 파일)
        if renamed_info:
            # 이미 변경된 파일 - ID로 관리번호 역추적
            existing_id, existing_name, existing_date = renamed_info
            
            # ID로 관리번호 찾기 (역조회)
            col_id = self.config['columns']['subject_info']['id']
            col_mgmt = self.config['columns']['subject_info']['management_number']
            col_div = self.config['columns']['subject_info']['division']
            
            result = self.subject_info_df[
                (self.subject_info_df[col_id] == existing_id) &
                (self.subject_info_df[col_div] == division)
            ]
            
            if len(result) == 0:
                return False, f"ID {existing_id}에 대한 정보를 찾을 수 없음"
            
            management_number = int(result.iloc[0][col_mgmt])
        else:
            # 원본 파일 - 고유번호에서 관리번호 찾기
            serial_number = self.extract_serial_from_filename(filename)
            if not serial_number:
                return False, "고유번호 추출 실패"
            
            # 관리번호 조회
            management_number = self.get_management_number(serial_number)
            if management_number is None:
                return False, f"관리번호 찾을 수 없음 (고유번호: {serial_number})"
        
        # ID, 이름, 착용시작일 조회
        subject_info = self.get_subject_info(management_number, division)
        if subject_info is None:
            return False, f"대상자 정보 찾을 수 없음 (관리번호: {management_number}, 구분: {division})"
        
        subject_id, name, wear_date = subject_info
        
        # 새 파일명 생성
        new_filename = self.generate_new_filename(filename, subject_id, name, wear_date)
        
        # 이미 올바른 파일명인 경우 건너뛰기
        if renamed_info:
            existing_id, existing_name, existing_date = renamed_info
            if existing_id == subject_id and existing_name == name and existing_date == wear_date:
                return False, "이미 올바르게 변경됨"
        
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
  # 기본 사용법
  python name.py -- 40주차
  
  # Dry-run 모드로 미리보기
  python name.py -- 40주차 --dry
  
  # 연도 지정
  python name.py -- 40주차 --year 2025
  
  # 다른 주차 처리
  python name.py -- 1주차 --year 2024
        """
    )
    
    parser.add_argument(
        '--week',
        required=True,
        help='구분 값 (예: "40주차", "1주차")'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        help='연도 (기본값: config.yaml의 defaults.year)'
    )
    
    parser.add_argument(
        '--dry',
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
            dry_run=args.dry
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

</name.py>

<config.yaml>
# ActiGraph 파일 자동 변경 설정

# 파일 경로
paths:
  # 대상자 정보 Excel 파일
  subject_info: "/mnt/c/Users/ding0/대학원생_김종철/OneDrive - 청주대학교/질병관리청/대상자 키,체중,주손 정보.xlsx"
  
  # 관리번호-시리얼번호 매칭 Excel 파일
  serial_mapping: "/mnt/c/Users/ding0/OneDrive/문서/vscode repository/가속도계 파일 바꾸기/관리번호-시리얼번호.xlsx"
  
  # ActiGraph 파일이 저장된 디렉토리
  target_directory: "/mnt/c/Users/ding0/OneDrive/문서/ActiGraph/ActiLife/Downloads"

# Excel 컬럼 설정
columns:
  # 관리번호-시리얼번호.xlsx
  serial_mapping:
    management_number: "관리번호"
    serial_number: "고유번호"
  
  # 대상자 키,체중,주손 정보.xlsx
  subject_info:
    division: "구분"
    management_number: "관리번호"
    id: "ID"
    name: "이름"
    wear_start_date: "착용 시작일"

# 처리 대상 파일 확장자
file_extensions:
  - ".gt3x"
  - ".agd"

# 기본 설정
defaults:
  year: 2025

</config.yaml>