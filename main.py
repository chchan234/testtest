#!/usr/bin/env python3
"""
자동 테스트케이스 생성기
기획서 문서를 분석하여 테스트케이스를 자동으로 생성하는 프로그램
"""

import os
import sys

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor.document_processor import process_document
from embedding.embedder import create_embeddings, build_vector_db
from engine.rag_engine import process_rag, generate_testcases
from validator.validator import validate_testcases
from excel_exporter.excel_exporter import export_to_excel, export_validation_results

def main():
    """메인 애플리케이션 진입점"""
    print("자동 테스트케이스 생성기를 시작합니다...")
    # 여기에 실행 로직이 추가됩니다

if __name__ == "__main__":
    main()