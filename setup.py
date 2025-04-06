from setuptools import setup, find_packages

setup(
    name="free_tc_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-docx>=0.8.11",
        "PyMuPDF>=1.19.0",
        "faiss-cpu>=1.7.4",
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
        "streamlit>=1.24.0",
        "torch==2.2.0",
        "huggingface_hub==0.12.1",
        "transformers==4.20.1",
        "sentence-transformers==2.2.2",
    ],
    python_requires=">=3.9",
)