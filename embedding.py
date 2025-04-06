"""
임베딩 모듈: 텍스트 청크를 임베딩 벡터로 변환하고 벡터 DB 구축
"""

import os
from typing import List, Dict, Any
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

# 기본 임베딩 모델
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

class Embedder:
    """텍스트 임베딩 처리 클래스"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        임베딩 처리기 초기화
        
        Args:
            model_name: 사용할 임베딩 모델명
        """
        self.model = SentenceTransformer(model_name)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 목록을 임베딩 벡터로 변환
        
        Args:
            texts: 임베딩할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

def create_embeddings(chunks: List[Dict[str, Any]], model_name: str = DEFAULT_MODEL_NAME) -> List[Dict[str, Any]]:
    """
    청크 리스트를 임베딩하여 벡터 정보 추가
    
    Args:
        chunks: 텍스트 청크 리스트
        model_name: 사용할 임베딩 모델명
        
    Returns:
        임베딩 벡터가 추가된 청크 리스트
    """
    embedder = Embedder(model_name)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)
    
    # 청크에 임베딩 추가
    for i, embedding in enumerate(embeddings):
        chunks[i]['embedding'] = embedding
    
    return chunks

def build_vector_db(chunks: List[Dict[str, Any]], persist_directory: str) -> chromadb.PersistentClient:
    """
    임베딩된 청크를 사용하여 벡터 DB 구축
    
    Args:
        chunks: 임베딩 벡터가 포함된 청크 리스트
        persist_directory: 벡터 DB 저장 경로
        
    Returns:
        생성된 ChromaDB 클라이언트
    """
    # 지정된 디렉토리가 없으면 생성
    os.makedirs(persist_directory, exist_ok=True)
    
    # ChromaDB 클라이언트 생성
    client = chromadb.PersistentClient(path=persist_directory)
    
    # 컬렉션 생성 또는 가져오기
    collection = client.get_or_create_collection(name="document_embeddings")
    
    # 청크 데이터 추가
    ids = [str(i) for i in range(len(chunks))]
    texts = [chunk['text'] for chunk in chunks]
    embeddings = [chunk['embedding'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    
    # 컬렉션에 데이터 추가
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    return client