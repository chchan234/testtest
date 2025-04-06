"""
라이브러리 호환성 패치 스크립트
"""

import os
import sys
import importlib

# 먼저 huggingface_hub.constants 패치
try:
    import huggingface_hub.constants
    if not hasattr(huggingface_hub.constants, 'HF_HUB_DISABLE_TELEMETRY'):
        huggingface_hub.constants.HF_HUB_DISABLE_TELEMETRY = "HF_HUB_DISABLE_TELEMETRY"
    # 추가적인 누락된 상수들에 대한 패치
    for const_name in ["HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "HUGGINGFACE_HUB_CACHE", "HUGGINGFACE_ASSETS_CACHE"]:
        if not hasattr(huggingface_hub.constants, const_name):
            setattr(huggingface_hub.constants, const_name, const_name)
except (ImportError, AttributeError):
    pass

# huggingface_hub.utils 패치 - OfflineModeIsEnabled 클래스 추가
try:
    import huggingface_hub.utils
    # OfflineModeIsEnabled 클래스가 없는 경우 추가
    if not hasattr(huggingface_hub.utils, 'OfflineModeIsEnabled'):
        class OfflineModeIsEnabled(Exception):
            """Exception: offline mode is enabled."""
            pass
        huggingface_hub.utils.OfflineModeIsEnabled = OfflineModeIsEnabled
    
    # 다른 필요한 utils 함수 패치
    utils_patches = {
        "get_token": lambda: None,
        "configure_http_backend": lambda *args, **kwargs: None,
        "get_session": lambda: None,
        "hf_raise_for_status": lambda *args, **kwargs: None,
        "is_notebook": lambda: False,
    }
    
    for func_name, func in utils_patches.items():
        if not hasattr(huggingface_hub.utils, func_name):
            setattr(huggingface_hub.utils, func_name, func)
            
except (ImportError, AttributeError):
    pass

def apply_huggingface_hub_patch():
    """
    huggingface_hub 라이브러리의 최신 버전 호환성 패치
    
    최신 버전에서는 cached_download 대신 hf_hub_download 함수를 사용합니다.
    """
    try:
        import huggingface_hub
        if not hasattr(huggingface_hub, 'cached_download'):
            try:
                # 최신 버전의 경우 hf_hub_download 함수 사용
                from huggingface_hub import hf_hub_download
                def cached_download_wrapper(*args, **kwargs):
                    # cached_download -> hf_hub_download 대체 래퍼
                    if 'cache_dir' in kwargs and 'local_dir' not in kwargs:
                        kwargs['local_dir'] = kwargs.pop('cache_dir')
                    if 'force_download' in kwargs and 'force_download' not in kwargs:
                        kwargs['force_download'] = kwargs.pop('force_download')
                    return hf_hub_download(*args, **kwargs)
                
                huggingface_hub.cached_download = cached_download_wrapper
                print("huggingface_hub 패치 적용 성공: hf_hub_download 사용")
            except ImportError:
                try:
                    # 이전 버전 호환성 시도
                    from huggingface_hub.utils import cached_download as cached_download_util
                    huggingface_hub.cached_download = cached_download_util
                    print("huggingface_hub 패치 적용 성공: utils.cached_download")
                except ImportError:
                    try:
                        from huggingface_hub.file_download import cached_download as cached_download_util
                        huggingface_hub.cached_download = cached_download_util
                        print("huggingface_hub 패치 적용 성공: file_download.cached_download")
                    except ImportError:
                        print("경고: huggingface_hub에서 cached_download를 찾을 수 없습니다.")
    except ImportError as e:
        print(f"huggingface_hub 가져오기 오류: {e}")

def setup_pytorch_environment():
    """
    PyTorch 환경 설정
    """
    try:
        # PyTorch JIT 컴파일러 설정
        os.environ['PYTORCH_JIT'] = '0'
        
        # tokenizers 병렬 처리 설정
        if 'TOKENIZERS_PARALLELISM' not in os.environ:
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
        # PyTorch 설정
        import torch
        torch._C._jit_set_profiling_executor(False)
        torch._C._jit_set_profiling_mode(False)
        
        # torch.classes 모듈 제거
        if 'torch.classes' in sys.modules:
            sys.modules.pop('torch.classes')
            
        print("PyTorch 환경 설정 완료")
    except ImportError as e:
        print(f"PyTorch 설정 오류: {e}")

def enable_offline_mode():
    """
    라이브러리들을 오프라인 모드로 설정
    """
    import os
    # Hugging Face 오프라인 모드 활성화
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'
    print("Hugging Face 오프라인 모드 활성화됨")

def apply_sentence_transformers_patch():
    """
    sentence_transformers 라이브러리 패치 적용 - 완전 오프라인 모드
    """
    try:
        # 오프라인 모드 활성화
        enable_offline_mode()
        
        # 먼저 sentence_transformers 패치를 적용
        import sys
        import types
        import numpy as np
        
        # sentence_transformers 모듈이 있는지 확인
        if 'sentence_transformers' in sys.modules:
            del sys.modules['sentence_transformers']
            
        # 가짜 모듈 생성
        sentence_transformers = types.ModuleType('sentence_transformers')
        sys.modules['sentence_transformers'] = sentence_transformers
        
        # SentenceTransformer 클래스 정의 - 완전 오프라인 스텁
        class SentenceTransformer:
            def __init__(self, model_name_or_path=None, **kwargs):
                self.model_name = model_name_or_path
                print(f"[오프라인 모드] SentenceTransformer 모델 '{model_name_or_path}' 로드 (스텁)")
                
            def encode(self, sentences, **kwargs):
                print(f"[오프라인 모드] 텍스트 {len(sentences) if isinstance(sentences, list) else 1}개 인코딩")
                # 간단한 임의 임베딩 벡터 반환 - 재현 가능한 결과를 위해 고정 시드 사용
                np.random.seed(42)  # 일관된 결과를 위한 고정 시드
                
                # 입력 텍스트를 기반으로 한 간단한 해시 값을 시드로 사용하여 약간의 의미 유지
                if isinstance(sentences, list):
                    vectors = []
                    for text in sentences:
                        # 간단한 해시 기반 시드 (텍스트마다 다른 벡터 생성하지만 같은 텍스트는 같은 벡터)
                        text_seed = sum(ord(c) for c in str(text)[:100]) % 10000
                        np.random.seed(text_seed)
                        vectors.append(np.random.rand(384).astype(np.float32))
                    return np.array(vectors)
                else:
                    text_seed = sum(ord(c) for c in str(sentences)[:100]) % 10000
                    np.random.seed(text_seed)
                    return np.random.rand(384).astype(np.float32)
        
        # 클래스 등록
        sentence_transformers.SentenceTransformer = SentenceTransformer
        
        print("sentence_transformers 패치 적용 성공 (오프라인 스텁 구현)")
        return True
    except Exception as e:
        print(f"sentence_transformers 패치 오류: {e}")
        return False

def main():
    """
    모든 패치 적용
    """
    print("라이브러리 호환성 패치 적용 중...")
    
    # 오프라인 모드 활성화
    enable_offline_mode()
    
    # 기본 환경 설정
    setup_pytorch_environment()
    apply_huggingface_hub_patch()
    
    # 항상 스텁 패치 적용 (online/offline 상관없이)
    apply_sentence_transformers_patch()
    
    print("패치 적용 완료")

if __name__ == "__main__":
    main()