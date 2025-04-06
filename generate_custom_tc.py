"""
커스텀 테스트케이스 생성 스크립트
대분류, 중분류를 지정하여 맞춤형 테스트케이스를 자동 생성합니다.
"""

import pandas as pd
import os
from datetime import datetime
import argparse

def generate_custom_testcases(major_category, medium_category, description=None):
    """
    사용자 지정 대분류/중분류 기반으로 테스트케이스를 생성합니다.
    
    Args:
        major_category: 대분류 (예: 스킬 시스템, 인벤토리 등)
        medium_category: 중분류 (예: 아이템 장착, 아이템 사용 등)
        description: 추가 설명 (선택 사항)
        
    Returns:
        테스트케이스 목록 (dictionary 형태)
    """
    # 기본 템플릿 가져오기
    template_testcases = _get_template_testcases(major_category, medium_category)
    
    # 템플릿이 없으면 빈 테스트케이스 리스트 생성
    if not template_testcases:
        # 기본 테스트케이스 구조 생성
        testcases = [
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "기본 기능",
                "확인내용": f"{medium_category} 기능이 정상적으로 동작하는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "기본 테스트케이스"
            }
        ]
        print(f"[주의] '{major_category} - {medium_category}'에 대한 템플릿이 없어 기본 테스트케이스를 생성합니다.")
    else:
        testcases = template_testcases
        print(f"'{major_category} - {medium_category}'에 대한 템플릿 테스트케이스 {len(testcases)}개를 생성했습니다.")
    
    # 설명이 있으면 비고 필드에 추가
    if description:
        for tc in testcases:
            if not tc.get("비고"):
                tc["비고"] = description
            else:
                tc["비고"] += f" | {description}"
    
    return testcases

def _get_template_testcases(major_category, medium_category):
    """
    대분류, 중분류에 맞는 템플릿 테스트케이스를 반환합니다.
    
    Args:
        major_category: 대분류
        medium_category: 중분류
        
    Returns:
        템플릿 테스트케이스 목록
    """
    # 스킬 시스템 - 아이템 장착 템플릿
    if major_category.lower() == "스킬 시스템" and medium_category.lower() in ["아이템 장착", "장비 장착", "장비"]:
        return [
            # 1. 기본 장착 기능
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "장착 기능",
                "확인내용": "인벤토리에서 장비 슬롯으로 아이템을 드래그 앤 드롭하여 정상적으로 장착되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "모든 장비 슬롯 유형 검증 (무기, 방어구, 장신구)"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "장착 기능",
                "확인내용": "장비 아이콘 더블 클릭으로 해당 슬롯에 자동 장착되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "모바일에서는 탭 동작 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "장착 해제",
                "확인내용": "장착된 장비 슬롯을 클릭하여 아이템이 정상적으로 해제되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "해제된 아이템이 인벤토리로 이동됨"
            },
            
            # 2. 외형 및 시각적 피드백
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "캐릭터 외형",
                "확인내용": "무기 장착 시 캐릭터 모델에 해당 무기가 올바르게 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "무기 위치, 크기, 각도 검증"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "캐릭터 외형",
                "확인내용": "방어구 장착 시 캐릭터 외형이 해당 방어구 모델로 변경되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "여러 부위 동시 장착 시 모든 부위 검증"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "UI 피드백",
                "확인내용": "장착 가능 아이템이 인벤토리에서 녹색 테두리로 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "요구 레벨, 클래스 조건 충족 시"
            },
            
            # 3. 능력치 영향 및 스탯 증가
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "능력치 증가",
                "확인내용": "공격력 증가 효과가 있는 아이템 장착 시 캐릭터 정보창에 공격력이 정확히 증가하는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "기본 공격력 + 아이템 효과 = 최종 공격력"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "능력치 증가",
                "확인내용": "방어력 증가 효과가 있는 아이템 장착 시 캐릭터 정보창에 방어력이 정확히 증가하는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "기본 방어력 + 아이템 효과 = 최종 방어력"
            },
            
            # 4. 스킬 영향 및 강화
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "스킬 강화",
                "확인내용": "특정 스킬 데미지 증가 효과가 있는 아이템 장착 시 해당 스킬의 데미지가 증가하는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "스킬 툴팁 및 실제 데미지 모두 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "스킬 강화",
                "확인내용": "스킬 쿨타임 감소 효과가 있는 아이템 장착 시 해당 스킬의 재사용 대기시간이 감소하는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "스킬 툴팁 및 실제 쿨타임 모두 확인"
            },
            
            # 5. 세트 효과
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "세트 효과",
                "확인내용": "동일 세트의 아이템 2개 장착 시 2세트 효과가 캐릭터에 적용되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "세트 효과 툴팁 및 실제 능력치 증가 확인"
            },
            
            # 6. 장착 제한 조건
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "레벨 제한",
                "확인내용": "캐릭터 레벨이 아이템 요구 레벨보다 낮을 때 장착이 제한되고 적절한 안내 메시지가 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "정확한 요구 레벨 표시 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "클래스 제한",
                "확인내용": "다른 클래스 전용 아이템 장착 시도 시 제한되고 적절한 안내 메시지가 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "요구 클래스 정보 표시 확인"
            }
        ]
    
    # 스킬 시스템 - 스킬 사용 템플릿
    elif major_category.lower() == "스킬 시스템" and medium_category.lower() in ["스킬 사용", "스킬"]:
        return [
            # 1. 기본 스킬 사용
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "기본 사용",
                "확인내용": "스킬 버튼 클릭 시 스킬이 정상적으로 발동되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "공격, 방어, 버프 등 다양한 스킬 유형 검증"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "단축키",
                "확인내용": "스킬 단축키로 스킬이 정상적으로 발동되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "PC 전용 기능"
            },
            
            # 2. 스킬 쿨타임
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "쿨타임 표시",
                "확인내용": "스킬 사용 후 쿨타임이 UI에 정확하게 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "숫자 카운트다운 및 시각적 표시 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "쿨타임 중 사용",
                "확인내용": "쿨타임 중인 스킬 사용 시도 시 적절한 안내 메시지가 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "버튼 비활성화 상태 확인"
            },
            
            # 3. 스킬 효과 및 데미지
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "공격 데미지",
                "확인내용": "공격 스킬 사용 시 공식에 따라 정확한 데미지가 적용되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "캐릭터 스탯, 아이템 효과 반영 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "버프 효과",
                "확인내용": "버프 스킬 사용 시 효과가 캐릭터에 정확히 적용되고 지속시간이 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "버프 아이콘 및 지속시간 UI 확인"
            },
            
            # 4. 리소스 소모
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "마나 소모",
                "확인내용": "스킬 사용 시 설정된 마나가 정확히 소모되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "마나 부족 시 사용 제한 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "리소스 부족",
                "확인내용": "필요 리소스(마나, 체력 등) 부족 시 스킬 사용이 제한되고 안내 메시지가 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "시스템별 리소스 유형에 맞게 확인"
            }
        ]
    
    # 스킬 시스템 - 스킬 강화 템플릿
    elif major_category.lower() == "스킬 시스템" and medium_category.lower() in ["스킬 강화", "레벨업"]:
        return [
            # 1. 기본 강화 기능
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "레벨업",
                "확인내용": "스킬 강화 버튼 클릭 시 스킬 레벨이 증가하고 능력치가 향상되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "스킬 레벨별 능력치 증가율 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "리소스 소모",
                "확인내용": "스킬 강화 시 필요한 포인트/재화가 정확히 소모되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "강화 비용 증가율 확인"
            },
            
            # 2. UI 및 피드백
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "강화 효과 표시",
                "확인내용": "스킬 강화 전후 효과 비교가 UI에 정확히 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "변경되는 수치 하이라이트 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "강화 성공 알림",
                "확인내용": "스킬 강화 성공 시 적절한 이펙트와 알림이 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "사운드 및 시각적 피드백 확인"
            },
            
            # 3. 강화 제한
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "최대 레벨",
                "확인내용": "스킬이 최대 레벨에 도달했을 때 더 이상 강화되지 않고 안내 메시지가 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "최대 레벨 UI 표시 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "선행 조건",
                "확인내용": "선행 스킬 레벨 조건이 있는 경우, 조건 미달 시 강화가 제한되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "필요 조건 안내 확인"
            }
        ]
    
    # 스킬 시스템 - 세트 효과 템플릿  
    elif major_category.lower() == "스킬 시스템" and medium_category.lower() in ["세트 효과", "세트"]:
        return [
            # 1. 세트 활성화
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "2세트 효과",
                "확인내용": "동일 세트 아이템 2개 장착 시 2세트 효과가 활성화되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "세트 효과 및 스탯 증가 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "4세트 효과",
                "확인내용": "동일 세트 아이템 4개 장착 시 2세트 및 4세트 효과가 함께 활성화되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "누적 효과 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "완성 세트",
                "확인내용": "세트 아이템을 모두 장착하여 완성 시 모든 단계 세트 효과와 특수 이펙트가 적용되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "캐릭터 외형 변화 확인"
            },
            
            # 2. UI 및 정보 표시
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "세트 정보",
                "확인내용": "세트 아이템 정보창에 현재 장착 중인 세트 아이템 개수와 효과가 정확히 표시되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "활성/비활성 효과 구분 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "아이템 표시",
                "확인내용": "인벤토리에서 세트 아이템이 특별한 표시(아이콘, 색상 등)로 구분되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "세트명 및 소속 세트 표시 확인"
            },
            
            # 3. 세트 스킬 효과
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "스킬 강화",
                "확인내용": "세트 효과로 인한 스킬 강화(데미지, 쿨타임 등)가 정확히 적용되는지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "스킬 정보창에 세트 효과 반영 확인"
            },
            {
                "대분류": major_category,
                "중분류": medium_category,
                "소분류": "특수 스킬",
                "확인내용": "세트 완성 시 해금되는 특수 스킬이 스킬창에 추가되고 사용 가능한지 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": "세트 미완성 시 스킬 잠금 상태 확인"
            }
        ]
    
    # 기본값 (템플릿 없음)
    return []

def export_to_excel(testcases, output_path="custom_testcases.xlsx"):
    """
    테스트케이스를 엑셀 파일로 내보냅니다.
    
    Args:
        testcases: 테스트케이스 목록
        output_path: 출력 파일 경로
    """
    # DataFrame 생성
    df = pd.DataFrame(testcases)
    
    # 현재 날짜/시간 추가
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{output_path.split('.')[0]}_{timestamp}.xlsx"
    
    # 엑셀 작성자 생성
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # 데이터 시작 위치를 8행으로 조정 (상단에 통계 영역 추가)
        df.to_excel(writer, index=False, sheet_name="테스트케이스", startrow=7)
        
        # 워크시트 가져오기
        worksheet = writer.sheets["테스트케이스"]
        
        # 상단 통계 영역 추가
        total_count = len(testcases)
        pass_count = sum(1 for tc in testcases if tc.get('AD', '') == 'PASS' or tc.get('iOS', '') == 'PASS' or tc.get('PC', '') == 'PASS')
        fail_count = sum(1 for tc in testcases if tc.get('AD', '') == 'FAIL' or tc.get('iOS', '') == 'FAIL' or tc.get('PC', '') == 'FAIL')
        not_tested_count = total_count - pass_count - fail_count
        
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
        
    print(f"테스트케이스가 다음 파일로 저장되었습니다: {file_path}")
    return file_path

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="커스텀 테스트케이스 생성기")
    parser.add_argument("--major", required=True, help="대분류 (예: '스킬 시스템')")
    parser.add_argument("--medium", required=True, help="중분류 (예: '아이템 장착')")
    parser.add_argument("--desc", help="추가 설명 (선택 사항)")
    parser.add_argument("--output", default="custom_testcases.xlsx", help="출력 파일명 (기본값: custom_testcases.xlsx)")
    
    args = parser.parse_args()
    
    print(f"{args.major} - {args.medium} 테스트케이스를 생성합니다...")
    testcases = generate_custom_testcases(args.major, args.medium, args.desc)
    output_path = export_to_excel(testcases, args.output)
    print(f"테스트케이스 생성 완료! 총 {len(testcases)}개의 테스트케이스가 생성되었습니다.")
    print(f"파일 위치: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()