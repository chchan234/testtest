#!/bin/bash

# pip 업그레이드
pip install --upgrade pip

# 필요한 디렉토리 생성
mkdir -p data/embeddings data/output data/processed data/raw

# 환경 변수 설정
export PYTORCH_JIT=0
export TOKENIZERS_PARALLELISM=false

# 메시지 출력
echo "환경 설정이 완료되었습니다."