"""
테스트케이스 생성기 애플리케이션 시작 스크립트
"""

import os
import sys
import importlib

# 패치 스크립트 실행
try:
    from patches.apply_patches import main as apply_patches
    apply_patches()
except ImportError:
    print("경고: 패치 모듈을 가져올 수 없습니다. 호환성 문제가 발생할 수 있습니다.")

# 스트림릿 앱 실행
print("자동 테스트케이스 생성기 웹 인터페이스를 시작합니다...")
os.system("streamlit run ui/app.py")