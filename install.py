"""
Free TC Generator 설치 스크립트
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """
    필요한 패키지 설치
    """
    print("필수 패키지를 설치합니다...")
    
    # 기본 패키지 설치
    base_packages = [
        "python-docx>=0.8.11",
        "PyMuPDF>=1.19.0",
        "faiss-cpu>=1.7.4",
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
        "streamlit>=1.24.0",
        "huggingface_hub==0.12.1",
    ]
    
    # 운영 체제 확인
    os_name = platform.system()
    
    # PyTorch 설치 - Rust 컴파일러 필요 없는 방식
    if os_name == "Linux":
        print("Linux 환경 감지됨 - CPU 기반 PyTorch 설치")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch>=2.2.0", "--index-url", "https://download.pytorch.org/whl/cpu"])
    else:
        print(f"{os_name} 환경 감지됨 - 기본 PyTorch 설치")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch>=2.2.0"])
    
    # 기본 패키지 설치
    for package in base_packages:
        print(f"{package} 설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    # 의존성 문제 해결을 위해 순서대로 설치
    subprocess.run([sys.executable, "-m", "pip", "install", "tokenizers==0.12.1", "--no-deps"])
    subprocess.run([sys.executable, "-m", "pip", "install", "transformers==4.20.1", "--no-deps"])
    subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2", "--no-deps"])
    
    print("모든 패키지가 설치되었습니다.")

def setup_environment():
    """
    환경 설정
    """
    # 필요한 디렉토리 생성
    os.makedirs("data/embeddings", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    
    print("환경 설정이 완료되었습니다.")

def main():
    """
    설치 프로세스 실행
    """
    print("Free TC Generator 설치를 시작합니다...")
    install_dependencies()
    setup_environment()
    print("설치가 완료되었습니다. 'python run_app.py'로 애플리케이션을 실행할 수 있습니다.")

if __name__ == "__main__":
    main()