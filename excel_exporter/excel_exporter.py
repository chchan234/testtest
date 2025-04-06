"""
엑셀 내보내기 모듈: 테스트케이스 및 검증 결과를 엑셀 파일로 내보내기
"""

import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import io

def export_to_excel(testcases: List[Dict[str, Any]], output_dir: str = "data/output") -> str:
    """
    테스트케이스를 엑셀 파일로 내보내기
    
    Args:
        testcases: 내보낼 테스트케이스 리스트
        output_dir: 엑셀 파일을 저장할 디렉토리
        
    Returns:
        생성된 엑셀 파일 경로
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 출력 파일 경로
    output_file = os.path.join(output_dir, f"testcases_{timestamp}.xlsx")
    
    # DataFrame 생성
    df = pd.DataFrame(testcases)
    
    # 필수 열이 없는 경우 빈 열 추가
    required_columns = ["대분류", "중분류", "소분류", "확인내용", "결과", "JIRA", "AD", "iOS", "PC", "비고"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # 열 순서 정렬
    df = df[required_columns]
    
    # QA 테스트 현황을 위한 통계 계산
    total_count = len(testcases)
    pass_count = sum(1 for tc in testcases if tc.get('AD', '') == 'PASS' or tc.get('iOS', '') == 'PASS' or tc.get('PC', '') == 'PASS')
    fail_count = sum(1 for tc in testcases if tc.get('AD', '') == 'FAIL' or tc.get('iOS', '') == 'FAIL' or tc.get('PC', '') == 'FAIL')
    not_tested_count = total_count - pass_count - fail_count
    
    # 엑셀 파일로 저장
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 데이터 시작 위치를 8행으로 조정 (상단에 통계 영역 추가)
        df.to_excel(writer, index=False, sheet_name="시스템", startrow=7)
        
        # 워크시트 가져오기
        worksheet = writer.sheets["시스템"]
        
        # 상단 통계 영역 추가
        worksheet.cell(row=2, column=2, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=3, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=7, value="QA 진행률")
        worksheet.cell(row=2, column=8, value="미진행")
        worksheet.cell(row=3, column=2, value="통과")
        worksheet.cell(row=3, column=3, value=pass_count)
        worksheet.cell(row=3, column=7, value="미진행")
        worksheet.cell(row=4, column=2, value="실패")
        worksheet.cell(row=4, column=3, value=fail_count)
        worksheet.cell(row=4, column=7, value="PASS")
        worksheet.cell(row=5, column=2, value="테스트 전")
        worksheet.cell(row=5, column=3, value=not_tested_count)
        worksheet.cell(row=5, column=7, value="BLOCKED")
        worksheet.cell(row=6, column=2, value="전체 개수")
        worksheet.cell(row=6, column=3, value=total_count)
        worksheet.cell(row=6, column=7, value="FAIL")
        worksheet.cell(row=7, column=7, value="전체")
        
        # 열 너비 조정
        worksheet.column_dimensions['B'].width = 20  # 대분류
        worksheet.column_dimensions['C'].width = 20  # 중분류
        worksheet.column_dimensions['D'].width = 20  # 소분류
        worksheet.column_dimensions['E'].width = 40  # 확인내용
        worksheet.column_dimensions['F'].width = 15  # 결과
        worksheet.column_dimensions['G'].width = 15  # JIRA
        worksheet.column_dimensions['H'].width = 10  # AD
        worksheet.column_dimensions['I'].width = 10  # iOS
        worksheet.column_dimensions['J'].width = 10  # PC
        worksheet.column_dimensions['K'].width = 40  # 비고
    
    return output_file

def export_to_bytes(testcases: List[Dict[str, Any]]) -> bytes:
    """
    테스트케이스를 엑셀 파일로 내보내고 바이트로 반환
    
    Args:
        testcases: 내보낼 테스트케이스 리스트
        
    Returns:
        엑셀 파일 바이트
    """
    # DataFrame 생성
    df = pd.DataFrame(testcases)
    
    # 필수 열이 없는 경우 빈 열 추가
    required_columns = ["대분류", "중분류", "소분류", "확인내용", "결과", "JIRA", "AD", "iOS", "PC", "비고"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # 열 순서 정렬
    df = df[required_columns]
    
    # QA 테스트 현황을 위한 통계 계산
    total_count = len(testcases)
    pass_count = sum(1 for tc in testcases if tc.get('AD', '') == 'PASS' or tc.get('iOS', '') == 'PASS' or tc.get('PC', '') == 'PASS')
    fail_count = sum(1 for tc in testcases if tc.get('AD', '') == 'FAIL' or tc.get('iOS', '') == 'FAIL' or tc.get('PC', '') == 'FAIL')
    not_tested_count = total_count - pass_count - fail_count
    
    # 바이트 스트림으로 저장
    output = io.BytesIO()
    
    # 엑셀 파일로 저장
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 데이터 시작 위치를 8행으로 조정 (상단에 통계 영역 추가)
        df.to_excel(writer, index=False, sheet_name="시스템", startrow=7)
        
        # 워크시트 가져오기
        worksheet = writer.sheets["시스템"]
        
        # 상단 통계 영역 추가
        worksheet.cell(row=2, column=2, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=3, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=7, value="QA 진행률")
        worksheet.cell(row=2, column=8, value="미진행")
        worksheet.cell(row=3, column=2, value="통과")
        worksheet.cell(row=3, column=3, value=pass_count)
        worksheet.cell(row=3, column=7, value="미진행")
        worksheet.cell(row=4, column=2, value="실패")
        worksheet.cell(row=4, column=3, value=fail_count)
        worksheet.cell(row=4, column=7, value="PASS")
        worksheet.cell(row=5, column=2, value="테스트 전")
        worksheet.cell(row=5, column=3, value=not_tested_count)
        worksheet.cell(row=5, column=7, value="BLOCKED")
        worksheet.cell(row=6, column=2, value="전체 개수")
        worksheet.cell(row=6, column=3, value=total_count)
        worksheet.cell(row=6, column=7, value="FAIL")
        worksheet.cell(row=7, column=7, value="전체")
        
        # 열 너비 조정
        worksheet.column_dimensions['B'].width = 20  # 대분류
        worksheet.column_dimensions['C'].width = 20  # 중분류
        worksheet.column_dimensions['D'].width = 20  # 소분류
        worksheet.column_dimensions['E'].width = 40  # 확인내용
        worksheet.column_dimensions['F'].width = 15  # 결과
        worksheet.column_dimensions['G'].width = 15  # JIRA
        worksheet.column_dimensions['H'].width = 10  # AD
        worksheet.column_dimensions['I'].width = 10  # iOS
        worksheet.column_dimensions['J'].width = 10  # PC
        worksheet.column_dimensions['K'].width = 40  # 비고
    
    # 스트림 위치를 처음으로 되돌림
    output.seek(0)
    
    return output.getvalue()

def export_validation_results(validation_results: List[Dict[str, Any]], output_dir: str = "data/output") -> str:
    """
    검증 결과를 엑셀 파일로 내보내기
    
    Args:
        validation_results: 내보낼 검증 결과 목록
        output_dir: 엑셀 파일을 저장할 디렉토리
        
    Returns:
        생성된 엑셀 파일 경로
    """
    # 결과 데이터 처리
    processed_results = []
    
    for result in validation_results:
        testcase = result.pop("testcase", {})
        # 테스트케이스와 검증 결과 통합
        processed_result = {**testcase, **result}
        processed_results.append(processed_result)
    
    # 기본 열 정의
    columns = ["대분류", "중분류", "소분류", "확인내용", "결과", "JIRA", "AD", "iOS", "PC", "비고", 
               "정확성", "완전성", "명확성", "플랫폼_적합성", "총점", "개선_제안", "통과_여부"]
    
    # DataFrame 생성
    df = pd.DataFrame(processed_results)
    
    # 필수 열이 없는 경우 빈 열 추가
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    
    # 열 순서 정렬
    df = df[columns]
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 출력 파일 경로
    output_file = os.path.join(output_dir, f"validated_testcases_{timestamp}.xlsx")
    
    # QA 테스트 현황을 위한 통계 계산
    total_count = len(processed_results)
    pass_count = sum(1 for tc in processed_results if tc.get('AD', '') == 'PASS' or tc.get('iOS', '') == 'PASS' or tc.get('PC', '') == 'PASS')
    fail_count = sum(1 for tc in processed_results if tc.get('AD', '') == 'FAIL' or tc.get('iOS', '') == 'FAIL' or tc.get('PC', '') == 'FAIL')
    not_tested_count = total_count - pass_count - fail_count
    
    # 엑셀 파일로 저장
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 데이터 시작 위치를 8행으로 조정 (상단에 통계 영역 추가)
        df.to_excel(writer, index=False, sheet_name="시스템", startrow=7)
        
        # 워크시트 가져오기
        worksheet = writer.sheets["시스템"]
        
        # 상단 통계 영역 추가
        worksheet.cell(row=2, column=2, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=3, value="QA T/C 총 현황")
        worksheet.cell(row=2, column=7, value="QA 진행률")
        worksheet.cell(row=2, column=8, value="미진행")
        worksheet.cell(row=3, column=2, value="통과")
        worksheet.cell(row=3, column=3, value=pass_count)
        worksheet.cell(row=3, column=7, value="미진행")
        worksheet.cell(row=4, column=2, value="실패")
        worksheet.cell(row=4, column=3, value=fail_count)
        worksheet.cell(row=4, column=7, value="PASS")
        worksheet.cell(row=5, column=2, value="테스트 전")
        worksheet.cell(row=5, column=3, value=not_tested_count)
        worksheet.cell(row=5, column=7, value="BLOCKED")
        worksheet.cell(row=6, column=2, value="전체 개수")
        worksheet.cell(row=6, column=3, value=total_count)
        worksheet.cell(row=6, column=7, value="FAIL")
        worksheet.cell(row=7, column=7, value="전체")
        
        # 열 너비 조정
        worksheet.column_dimensions['B'].width = 20  # 대분류
        worksheet.column_dimensions['C'].width = 20  # 중분류
        worksheet.column_dimensions['D'].width = 20  # 소분류
        worksheet.column_dimensions['E'].width = 40  # 확인내용
        worksheet.column_dimensions['F'].width = 15  # 결과
        worksheet.column_dimensions['G'].width = 15  # JIRA
        worksheet.column_dimensions['H'].width = 10  # AD
        worksheet.column_dimensions['I'].width = 10  # iOS
        worksheet.column_dimensions['J'].width = 10  # PC
        worksheet.column_dimensions['K'].width = 40  # 비고
        worksheet.column_dimensions['L'].width = 10  # 정확성
        worksheet.column_dimensions['M'].width = 10  # 완전성
        worksheet.column_dimensions['N'].width = 10  # 명확성
        worksheet.column_dimensions['O'].width = 15  # 플랫폼_적합성
        worksheet.column_dimensions['P'].width = 10  # 총점
        worksheet.column_dimensions['Q'].width = 40  # 개선_제안
        worksheet.column_dimensions['R'].width = 10  # 통과_여부
    
    return output_file