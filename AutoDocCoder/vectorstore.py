from typing import Optional, Set
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import requests, validators, os

class VectorStore:
  def create_faiss_vectorstore(doc_text: str, save_path: str = "./faiss_index"):
    """
    Creates a FAISS vector store from the given document text and saves it to disk.

    Args:
    doc_text (str): The document text to create the vector store from.
    save_path (str): The path to save the vector store to. Defaults to "./faiss_index".

    Returns:
    Optional[IndexFlatL2]: The created FAISS vector store, or None if an error occurred.
    """
    try:
        # 1. Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(doc_text)

        # 2. Convert to vector embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1024
        )

        # 3. Store in FAISS
        vectorstore = FAISS.from_texts(chunks, embeddings)

        # 4. Save to disk
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        vectorstore.save_local(save_path)
        return vectorstore
    except Exception as e:
        raise Exception(f"Error creating FAISS vector store: {e}")

  def load_and_query_vectorstore(query: str, save_path: str = "./faiss_index", k: int = 10) -> Optional[str]:
    """
    Loads a FAISS vector store from disk and queries it with the given query string.

    Args:
    query (str): The query string to search for in the vector store.
    save_path (str): The path to the saved vector store. Defaults to "./faiss_index".
    k (int): The number of results to return. Defaults to 10.

    Returns:
    Optional[str]: The relevant chunks of text from the vector store, or None if an error occurred.
    """

    try:
        # Add additional query text
        query += "\nAlso, Handle the Authentication and proper Error Handling in the code"

        # Load embeddings model
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1024
        )

        # Load vector store from disk
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"Vector store not found at: {save_path}")
        vectorstore = FAISS.load_local(save_path, embeddings, allow_dangerous_deserialization=True)

        # Query vector store
        results = vectorstore.similarity_search(query, k=k)

        # Extract relevant chunks
        relevant_chunks = [doc.page_content for doc in results]

        # Join chunks into a single string
        return "\n\n".join(relevant_chunks)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Vector store not found at: {save_path}")
    except Exception as e:
        raise Exception(f"Error querying vector store: {e}")
