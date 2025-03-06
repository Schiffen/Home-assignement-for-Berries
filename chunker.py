# app/chunker.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List

def chunk_transcript_into_docs(
    transcript_text: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 120
) -> List[Document]:
    """
    Splits transcript into smaller 'documents' using a known method:
    LangChain's RecursiveCharacterTextSplitter.
    Returns a list of LangChain Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    docs = text_splitter.create_documents([transcript_text])
    return docs
