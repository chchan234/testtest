"""
문서 처리 모듈: DOCX, PDF 파일을 텍스트로 추출하고 청크 단위로 분리
"""

import os
from typing import List, Dict, Any, Union
import docx
import fitz  # PyMuPDF
import re

def extract_text(file_path: str) -> str:
    """
    DOCX 또는 PDF 파일에서 텍스트를 추출
    
    Args:
        file_path: 처리할 파일 경로
        
    Returns:
        추출된 전체 텍스트
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.docx':
        return _extract_from_docx(file_path)
    elif file_ext == '.pdf':
        return _extract_from_pdf(file_path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file_ext}")

def _extract_from_docx(file_path: str) -> str:
    """DOCX 파일에서 텍스트를 추출"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        
        # 디버깅 정보
        print(f"DOCX 파일 처리: {file_path}")
        print(f"단락 수: {len(doc.paragraphs)}")
        
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # 표(tables)에서 텍스트 추출
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        
        return '\n'.join(full_text)
    except Exception as e:
        print(f"DOCX 파일 처리 중 오류: {str(e)}")
        # 파일 존재 여부 확인
        import os
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"파일은 존재함 (크기: {file_size} 바이트)")
        else:
            print(f"파일이 존재하지 않음: {file_path}")
        raise

def _extract_from_pdf(file_path: str) -> str:
    """PDF 파일에서 텍스트를 추출"""
    try:
        doc = fitz.open(file_path)
        full_text = []
        
        # 디버깅 정보
        print(f"PDF 파일 처리: {file_path}")
        print(f"페이지 수: {len(doc)}")
        
        for page in doc:
            full_text.append(page.get_text())
        
        return '\n'.join(full_text)
    except Exception as e:
        print(f"PDF 파일 처리 중 오류: {str(e)}")
        # 파일 존재 여부 확인
        import os
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"파일은 존재함 (크기: {file_size} 바이트)")
        else:
            print(f"파일이 존재하지 않음: {file_path}")
        raise

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    텍스트를 청크로 분할
    
    Args:
        text: 분할할 텍스트
        chunk_size: 각 청크의 최대 크기
        chunk_overlap: 청크 간 겹치는 문자 수
        
    Returns:
        분할된 텍스트 청크 리스트
    """
    # 텍스트가 비어있는 경우
    if not text:
        return []
    
    # 단락 단위로 분할
    paragraphs = text.split('\n')
    paragraphs = [p for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        # 단락이 청크 사이즈보다 크면 추가 분할
        if len(para) > chunk_size:
            # 현재 청크를 저장
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                # 겹치는 부분 유지
                overlap_paras = current_chunk[-1:] if current_chunk else []
                current_chunk = overlap_paras
                current_size = sum(len(p) for p in current_chunk)
            
            # 큰 단락 분할
            words = para.split()
            temp_chunk = []
            temp_size = 0
            
            for word in words:
                if temp_size + len(word) + 1 > chunk_size:
                    chunks.append(' '.join(temp_chunk))
                    # 겹치는 부분 유지
                    overlap_point = max(0, len(temp_chunk) - int(chunk_overlap / 5))
                    temp_chunk = temp_chunk[overlap_point:]
                    temp_size = sum(len(w) + 1 for w in temp_chunk)
                
                temp_chunk.append(word)
                temp_size += len(word) + 1
            
            if temp_chunk:
                current_chunk.append(' '.join(temp_chunk))
                current_size += temp_size
        
        # 일반적인 경우: 단락 추가
        elif current_size + len(para) > chunk_size:
            chunks.append('\n'.join(current_chunk))
            # 겹치는 부분 유지
            overlap_paras = current_chunk[-1:] if current_chunk else []
            current_chunk = overlap_paras
            current_size = sum(len(p) for p in current_chunk)
            current_chunk.append(para)
            current_size += len(para)
        else:
            current_chunk.append(para)
            current_size += len(para)
    
    # 마지막 청크 추가
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def process_document(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """
    문서를 처리하여 청크 단위로 분리
    
    Args:
        file_path: 처리할 파일 경로
        chunk_size: 각 청크의 최대 크기
        chunk_overlap: 청크 간 겹치는 문자 수
        
    Returns:
        청크 리스트 (메타데이터 포함)
    """
    # 텍스트 추출
    text = extract_text(file_path)
    
    # 텍스트 분할
    chunks = split_text(text, chunk_size, chunk_overlap)
    
    # 메타데이터 추가 (파일명, 페이지 번호 등)
    file_name = os.path.basename(file_path)
    processed_chunks = []
    
    for i, chunk_text in enumerate(chunks):
        processed_chunks.append({
            'text': chunk_text,
            'metadata': {
                'file_name': file_name,
                'chunk_id': i,
                'source': file_path
            }
        })
    
    return processed_chunks