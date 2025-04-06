"""
Streamlit 웹 애플리케이션: 사용자 인터페이스 제공
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile

# 환경 변수 설정을 맨 위로 이동
os.environ['PYTORCH_JIT'] = '0'
if 'TOKENIZERS_PARALLELISM' not in os.environ:
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# 프로젝트 루트를 임포트 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 패치 먼저 적용
try:
    # 오프라인 모드 관련 환경변수 설정
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'
    
    from patches.apply_patches import setup_pytorch_environment, apply_huggingface_hub_patch, apply_sentence_transformers_patch, enable_offline_mode
    
    # 모든 패치 적용
    enable_offline_mode()
    setup_pytorch_environment()
    apply_huggingface_hub_patch()
    apply_sentence_transformers_patch()  # 항상 스텁 패치 적용
    
except ImportError:
    st.warning("패치 모듈을 가져오는데 실패했습니다.")

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
    st.warning(f"huggingface_hub.constants 패치 오류: {e}")

# PyTorch 호환성 문제 해결을 위한 설정
try:
    import torch
    if hasattr(torch, '_C'):
        try:
            torch._C._jit_set_profiling_executor(False)
            torch._C._jit_set_profiling_mode(False)
        except Exception as e:
            st.warning(f"PyTorch JIT 설정 경고: {e}")
except ImportError:
    pass

# huggingface_hub 호환성 처리
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
        except ImportError:
            try:
                from huggingface_hub.utils import cached_download as cached_download_util
                huggingface_hub.cached_download = cached_download_util
            except ImportError:
                try:
                    from huggingface_hub.file_download import cached_download as cached_download_util
                    huggingface_hub.cached_download = cached_download_util
                except ImportError:
                    st.warning("huggingface_hub 호환성 패치 적용 실패")
except ImportError as e:
    st.warning(f"huggingface_hub 가져오기 경고: {e}")

try:
    from processor.document_processor import process_document
    from embedding.embedder import create_embeddings, build_vector_db, load_vector_db
    from engine.rag_engine import process_rag, generate_testcases
    from validator.validator import validate_testcases
    from excel_exporter.excel_exporter import export_to_excel, export_validation_results, export_to_bytes
except Exception as e:
    st.error(f"모듈 가져오기 오류: {e}")
    st.stop()

# 앱 설정
st.set_page_config(
    page_title="자동 테스트케이스 생성기",
    page_icon="📋",
    layout="wide"
)

def main():
    """Streamlit 애플리케이션 메인 함수"""
    
    st.title("📋 자동 테스트케이스 생성기")
    st.write("기획서 문서를 업로드하면 자동으로 테스트케이스를 생성합니다.")
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 청크 크기 설정
        chunk_size = st.slider(
            "청크 크기", 
            min_value=500, 
            max_value=2000, 
            value=1000, 
            step=100,
            help="문서를 분할할 청크의 크기를 설정합니다."
        )
        
        # 청크 오버랩 설정
        chunk_overlap = st.slider(
            "청크 오버랩", 
            min_value=0, 
            max_value=500, 
            value=200, 
            step=50,
            help="청크 간 겹치는 정도를 설정합니다."
        )
        
        # 검색 결과 수
        n_results = st.slider(
            "검색 결과 수", 
            min_value=3, 
            max_value=10, 
            value=5, 
            step=1,
            help="RAG 검색 시 반환할 결과 수를 설정합니다."
        )
        
        # 벡터 DB 디렉토리
        vector_db_dir = st.text_input(
            "벡터 DB 디렉토리",
            value="data/embeddings",
            help="벡터 DB를 저장할 디렉토리를 지정합니다."
        )
        
        st.divider()
        
        # 프로세스 정보
        st.header("ℹ️ 프로세스 정보")
        st.info(
            "1. 문서 업로드: DOCX 또는 PDF 기획서를 업로드합니다.\n"
            "2. 데이터 처리: 문서를 텍스트로 추출하고 청크로 분할합니다.\n"
            "3. 임베딩 생성: 텍스트 청크를 벡터로 변환합니다.\n"
            "4. 테스트케이스 생성: RAG 방식으로 테스트케이스를 생성합니다.\n"
            "5. 검증 및 피드백: 생성된 테스트케이스를 검증하고 피드백을 제공합니다.\n"
            "6. 엑셀 내보내기: 최종 결과를 엑셀 파일로 다운로드합니다."
        )
    
    # 세션 상태 초기화
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    if 'testcases_generated' not in st.session_state:
        st.session_state.testcases_generated = False
    
    # 메인 영역 - 탭 구성
    tab1, tab2, tab3 = st.tabs(["📤 문서 업로드", "🔍 테스트케이스 생성", "📊 결과 확인"])
    
    # 탭1: 문서 업로드
    with tab1:
        st.header("📤 문서 업로드")
        
        uploaded_file = st.file_uploader(
            "DOCX 또는 PDF 파일을 업로드하세요.", 
            type=["docx", "pdf"]
        )
        
        if uploaded_file is not None:
            try:
                # 데이터 디렉토리 확인 및 생성
                if not os.path.exists("data"):
                    os.makedirs("data", exist_ok=True)
                
                # 고정 임시 파일 경로 사용 (디버깅용)
                fixed_temp_dir = os.path.join(os.path.abspath("data"), "temp")
                os.makedirs(fixed_temp_dir, exist_ok=True)
                
                # 파일 확장자 확인
                file_ext = os.path.splitext(uploaded_file.name)[1]
                st.write(f"파일 형식: {file_ext}")
                
                # 임시 파일로 저장
                temp_file_path = os.path.join(fixed_temp_dir, f"uploaded{file_ext}")
                with open(temp_file_path, "wb") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                
                st.write(f"임시 파일 저장됨: {temp_file_path}")
                st.write(f"파일 크기: {os.path.getsize(temp_file_path)} 바이트")
                
                st.success(f"'{uploaded_file.name}' 파일이 업로드되었습니다!")
            except Exception as upload_error:
                st.error(f"파일 업로드 처리 오류: {upload_error}")
                import traceback
                st.code(traceback.format_exc())
            
            # 세션 상태에 파일 경로 저장
            st.session_state.uploaded_file_path = temp_file_path
            st.session_state.uploaded_file_name = uploaded_file.name
            
            # 처리 버튼
            if st.button("문서 처리 시작", type="primary"):
                try:
                    with st.spinner("문서를 처리하고 있습니다..."):
                        # 1. 문서 처리
                        st.info("1/4 단계: 문서를 텍스트로 추출하고 청크로 분할 중...")
                        try:
                            # 디버깅을 위한 정보 출력
                            st.write(f"파일 경로: {st.session_state.uploaded_file_path}")
                            st.write(f"파일 존재 여부: {os.path.exists(st.session_state.uploaded_file_path)}")
                            
                            chunks = process_document(
                                st.session_state.uploaded_file_path, 
                                chunk_size=chunk_size, 
                                chunk_overlap=chunk_overlap
                            )
                            st.write(f"처리된 청크 수: {len(chunks)}")
                        except Exception as doc_error:
                            st.error(f"문서 처리 오류: {doc_error}")
                            import traceback
                            st.code(traceback.format_exc())
                            raise
                        
                        # 2. 임베딩 생성
                        st.info("2/4 단계: 텍스트 청크 임베딩 생성 중...")
                        try:
                            embedded_chunks = create_embeddings(chunks)
                            st.write(f"임베딩된 청크 수: {len(embedded_chunks)}")
                        except Exception as emb_error:
                            st.error(f"임베딩 생성 오류: {emb_error}")
                            import traceback
                            st.code(traceback.format_exc())
                            raise
                        
                        # 3. 벡터 DB 구축
                        st.info("3/4 단계: 벡터 DB 구축 중...")
                        try:
                            vector_db = build_vector_db(embedded_chunks, vector_db_dir)
                            st.write(f"벡터 DB 디렉토리: {vector_db_dir}")
                        except Exception as db_error:
                            st.error(f"벡터 DB 구축 오류: {db_error}")
                            import traceback
                            st.code(traceback.format_exc())
                            raise
                        
                        # 4. 원본 텍스트 저장
                        original_text = "\n".join([chunk['text'] for chunk in chunks])
                        
                        # 세션 상태에 저장
                        st.session_state.chunks = chunks
                        st.session_state.embedded_chunks = embedded_chunks
                        st.session_state.vector_db = vector_db
                        st.session_state.vector_db_dir = vector_db_dir
                        st.session_state.original_text = original_text
                        st.session_state.document_processed = True
                        
                        st.success("문서 처리가 완료되었습니다! '테스트케이스 생성' 탭으로 이동하세요.")
                except Exception as e:
                    st.error(f"문서 처리 중 오류가 발생했습니다: {e}")
    
    # 탭2: 테스트케이스 생성
    with tab2:
        st.header("🔍 테스트케이스 생성")
        
        if not st.session_state.get("document_processed", False):
            st.warning("먼저 '문서 업로드' 탭에서 문서를 업로드하고 처리해주세요.")
        else:
            st.info(f"처리된 문서: {st.session_state.uploaded_file_name}")
            
            # 쿼리 입력 (선택사항)
            query = st.text_input(
                "특정 부분에 대한 테스트케이스를 생성하려면 여기에 쿼리를 입력하세요 (선택사항)",
                help="비워두면 전체 문서에 대한 테스트케이스가 생성됩니다."
            )
            
            # 테스트케이스 생성 버튼
            if st.button("테스트케이스 생성", type="primary"):
                try:
                    with st.spinner("테스트케이스를 생성하고 있습니다..."):
                        # 벡터 DB가 세션에 없다면 로드
                        if 'vector_db' not in st.session_state:
                            vector_db = load_vector_db(st.session_state.vector_db_dir)
                            st.session_state.vector_db = vector_db
                        
                        if query:
                            # 쿼리 기반 테스트케이스 생성
                            st.info("쿼리 기반 테스트케이스 생성 중...")
                            testcases = process_rag(
                                st.session_state.vector_db, 
                                query,
                                n_results=n_results
                            )
                        else:
                            # 전체 문서 기반 테스트케이스 생성
                            st.info("전체 문서 기반 테스트케이스 생성 중...")
                            testcases = generate_testcases(
                                st.session_state.vector_db, 
                                st.session_state.chunks
                            )
                        
                        # 검증 절차
                        st.info("생성된 테스트케이스 검증 중...")
                        validation_results = validate_testcases(
                            testcases, 
                            st.session_state.original_text
                        )
                        
                        # 세션 상태에 저장
                        st.session_state.testcases = testcases
                        st.session_state.validation_results = validation_results
                        st.session_state.testcases_generated = True
                        
                        st.success("테스트케이스 생성이 완료되었습니다! '결과 확인' 탭으로 이동하세요.")
                except Exception as e:
                    st.error(f"테스트케이스 생성 중 오류가 발생했습니다: {e}")
    
    # 탭3: 결과 확인
    with tab3:
        st.header("📊 결과 확인")
        
        if not st.session_state.get("testcases_generated", False):
            st.warning("먼저 '테스트케이스 생성' 탭에서 테스트케이스를 생성해주세요.")
        else:
            try:
                # 테스트케이스 테이블 표시
                st.subheader("생성된 테스트케이스")
                
                # DataFrame 생성
                testcases_df = pd.DataFrame(st.session_state.testcases)
                
                # 필수 컬럼 추가
                required_columns = ["대분류", "중분류", "소분류", "확인내용", "결과", "JIRA", "AD", "iOS", "PC", "비고"]
                for col in required_columns:
                    if col not in testcases_df.columns:
                        testcases_df[col] = ""
                
                # 컬럼 순서 정렬
                testcases_df = testcases_df[required_columns]
                
                # 테이블 표시
                st.dataframe(testcases_df, use_container_width=True)
                
                # 통계 정보 표시
                st.subheader("QA T/C 총 현황")
                total_count = len(testcases_df)
                pass_count = sum(1 for _, row in testcases_df.iterrows() 
                                if row.get('AD') == 'PASS' or row.get('iOS') == 'PASS' or row.get('PC') == 'PASS')
                fail_count = sum(1 for _, row in testcases_df.iterrows() 
                                if row.get('AD') == 'FAIL' or row.get('iOS') == 'FAIL' or row.get('PC') == 'FAIL')
                not_tested_count = total_count - pass_count - fail_count
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("테스트 전", not_tested_count)
                with col2:
                    st.metric("통과", pass_count)
                with col3:
                    st.metric("실패", fail_count)
                with col4:
                    st.metric("전체 개수", total_count)
                
                # 엑셀 다운로드 섹션
                st.subheader("결과 다운로드")
                
                # Excel 파일로 내보내기
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                excel_filename = f"테스트케이스_{timestamp}.xlsx"
                
                try:
                    # excel_exporter에서 바이트 형식으로 내보내기
                    excel_bytes = export_to_bytes(st.session_state.testcases)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="엑셀 파일 다운로드",
                        data=excel_bytes,
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as excel_error:
                    st.error(f"엑셀 내보내기 오류: {excel_error}")
                    import traceback
                    st.code(traceback.format_exc())
            except Exception as e:
                st.error(f"결과 표시 중 오류가 발생했습니다: {e}")
                if st.button("세션 초기화"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.experimental_rerun()

if __name__ == "__main__":
    main()