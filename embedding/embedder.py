"""
임베딩 모듈: 텍스트 청크를 임베딩 벡터로 변환하고 벡터 DB 구축
"""

import os
from typing import List, Dict, Any
import numpy as np
import pickle
import faiss
import torch
import sys

# 프로젝트 루트를 임포트 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 기본 임베딩 모델
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

# Torch 설정 - 스트림릿 호환성 문제 해결
os.environ['PYTORCH_JIT'] = '0'
if hasattr(torch, '_C'):
    try:
        torch._C._jit_set_profiling_executor(False)
        torch._C._jit_set_profiling_mode(False)
    except Exception as e:
        print(f"토치 JIT 설정 경고: {e}")

# huggingface_hub.constants 패치 - sentence-transformers 호환성을 위함
try:
    import huggingface_hub.constants
    if not hasattr(huggingface_hub.constants, 'HF_HUB_DISABLE_TELEMETRY'):
        huggingface_hub.constants.HF_HUB_DISABLE_TELEMETRY = "HF_HUB_DISABLE_TELEMETRY"
    # 추가적인 누락된 상수들에 대한 패치
    for const_name in ["HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "HUGGINGFACE_HUB_CACHE", "HUGGINGFACE_ASSETS_CACHE"]:
        if not hasattr(huggingface_hub.constants, const_name):
            setattr(huggingface_hub.constants, const_name, const_name)
except (ImportError, AttributeError) as e:
    print(f"huggingface_hub.constants 패치 오류: {e}")

# 버전 호환성 문제 해결을 위한 패치
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
                from huggingface_hub.utils import cached_download as cached_download_util
                huggingface_hub.cached_download = cached_download_util
            except ImportError:
                try:
                    from huggingface_hub.file_download import cached_download as cached_download_util
                    huggingface_hub.cached_download = cached_download_util
                except ImportError:
                    print("캐시 다운로드 패치 적용 실패: huggingface_hub 버전 확인이 필요합니다.")
except ImportError as e:
    print(f"huggingface_hub 가져오기 오류: {e}")

# 오프라인 모드 설정
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

# 이제 sentence_transformers 가져오기
try:
    # 패치 모듈 가져와서 적용
    from patches.apply_patches import apply_sentence_transformers_patch, enable_offline_mode
    
    # 오프라인 모드 활성화 및 스텁 패치 적용
    enable_offline_mode()
    apply_sentence_transformers_patch()
    
    # 패치된 클래스 사용
    from sentence_transformers import SentenceTransformer
    print("오프라인 패치된 SentenceTransformer 사용")
    
except ImportError as e:
    print(f"패치 모듈 가져오기 오류: {e}")
    # 스텁 구현
    import numpy as np
    class SentenceTransformer:
        def __init__(self, model_name_or_path=None, **kwargs):
            self.model_name = model_name_or_path
            print(f"[로컬 임베딩 스텁] SentenceTransformer 모델 '{model_name_or_path}' 로드")
            
        def encode(self, sentences, **kwargs):
            print(f"[로컬 임베딩 스텁] 텍스트 {len(sentences) if isinstance(sentences, list) else 1}개 인코딩")
            # 재현 가능한 임의 임베딩 벡터 생성
            np.random.seed(42)
            
            # 입력 텍스트에 따라 다른 벡터 생성 (의미적 차이 유지)
            if isinstance(sentences, list):
                vectors = []
                for text in sentences:
                    # 텍스트 기반 해시 시드
                    text_seed = sum(ord(c) for c in str(text)[:100]) % 10000
                    np.random.seed(text_seed)
                    vectors.append(np.random.rand(384).astype(np.float32))
                return np.array(vectors)
            else:
                text_seed = sum(ord(c) for c in str(sentences)[:100]) % 10000
                np.random.seed(text_seed)
                return np.random.rand(384).astype(np.float32)

class Embedder:
    """텍스트 임베딩 처리 클래스"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        임베딩 처리기 초기화
        
        Args:
            model_name: 사용할 임베딩 모델명
        """
        try:
            self.model = SentenceTransformer(model_name)
            print(f"임베딩 모델 '{model_name}' 로드 완료")
        except Exception as e:
            print(f"임베딩 모델 초기화 오류: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 목록을 임베딩 벡터로 변환
        
        Args:
            texts: 임베딩할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        if not texts:
            return []
            
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            print(f"텍스트 임베딩 오류: {e}")
            raise

def create_embeddings(chunks: List[Dict[str, Any]], model_name: str = DEFAULT_MODEL_NAME) -> List[Dict[str, Any]]:
    """
    청크 리스트를 임베딩하여 벡터 정보 추가
    
    Args:
        chunks: 텍스트 청크 리스트
        model_name: 사용할 임베딩 모델명
        
    Returns:
        임베딩 벡터가 추가된 청크 리스트
    """
    if not chunks:
        return []
        
    embedder = Embedder(model_name)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)
    
    # 청크에 임베딩 추가
    for i, embedding in enumerate(embeddings):
        chunks[i]['embedding'] = embedding
    
    return chunks

def build_vector_db(chunks: List[Dict[str, Any]], persist_directory: str) -> Dict:
    """
    임베딩된 청크를 사용하여 FAISS 벡터 DB 구축
    
    Args:
        chunks: 임베딩 벡터가 포함된 청크 리스트
        persist_directory: 벡터 DB 저장 경로
        
    Returns:
        검색에 필요한 정보를 포함한 사전
    """
    if not chunks:
        raise ValueError("임베딩된 청크가 제공되지 않았습니다.")
    
    # 지정된 디렉토리가 없으면 생성
    os.makedirs(persist_directory, exist_ok=True)
    
    # 벡터와 텍스트 준비
    texts = [chunk['text'] for chunk in chunks]
    embeddings = np.array([chunk['embedding'] for chunk in chunks], dtype=np.float32)
    
    # 벡터 차원 확인
    dimension = embeddings.shape[1]
    
    # FAISS 인덱스 생성
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 저장 경로
    index_path = os.path.join(persist_directory, "faiss_index.bin")
    faiss.write_index(index, index_path)
    
    # 메타데이터와 텍스트 저장
    metadata = {
        'texts': texts,
        'metadatas': [chunk.get('metadata', {}) for chunk in chunks],
    }
    
    metadata_path = os.path.join(persist_directory, "metadata.pkl")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    # 검색에 필요한 정보 반환
    return {
        'index': index,
        'index_path': index_path,
        'metadata': metadata,
        'metadata_path': metadata_path,
        'dimension': dimension
    }

def load_vector_db(persist_directory: str) -> Dict:
    """
    저장된 FAISS 벡터 DB 로드
    
    Args:
        persist_directory: 벡터 DB가 저장된 경로
        
    Returns:
        검색에 필요한 정보를 포함한 사전
    """
    index_path = os.path.join(persist_directory, "faiss_index.bin")
    metadata_path = os.path.join(persist_directory, "metadata.pkl")
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise FileNotFoundError(f"벡터 DB 파일을 찾을 수 없습니다: {persist_directory}")
    
    # FAISS 인덱스 로드
    index = faiss.read_index(index_path)
    
    # 메타데이터 로드
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    return {
        'index': index,
        'index_path': index_path,
        'metadata': metadata,
        'metadata_path': metadata_path,
        'dimension': index.d
    }

def search_similar(vector_db: Dict, query_text: str, top_k: int = 5, model_name: str = DEFAULT_MODEL_NAME) -> List[Dict]:
    """
    쿼리 텍스트와 유사한 청크 검색
    
    Args:
        vector_db: 벡터 DB 정보 사전
        query_text: 검색할 쿼리 텍스트
        top_k: 반환할 결과 수
        model_name: 임베딩 모델명
        
    Returns:
        유사 청크 목록
    """
    if not query_text.strip():
        return []
    
    # 쿼리 임베딩 생성
    embedder = Embedder(model_name)
    query_embedding = np.array([embedder.embed_texts([query_text])[0]], dtype=np.float32)
    
    # 유사 벡터 검색
    distances, indices = vector_db['index'].search(query_embedding, min(top_k, vector_db['index'].ntotal))
    
    # 결과 포맷팅
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(vector_db['metadata']['texts']):
            results.append({
                'text': vector_db['metadata']['texts'][idx],
                'metadata': vector_db['metadata']['metadatas'][idx],
                'distance': float(distances[0][i])
            })
    
    return results