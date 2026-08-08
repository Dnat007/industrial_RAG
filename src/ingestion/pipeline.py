from pathlib import Path
from uuid import uuid4
from src.ingestion.parser import load_pdf
from src.ingestion.chunker import split_documents
from src.ingestion.embeddings import embed_documents
from src.ingestion.indexer import upload_documents

DATA_DIR = Path("data")

def ingest_pdf(file_path):

    documents = load_pdf(file_path)
    print(f"Loaded {len(documents)} pages")

    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_documents(texts)
    print(f"Generated {len(embeddings)} embeddings")

    search_documents = []
    document_id = str(uuid4())
    document_name = file_path.name
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        page_number = chunk.metadata.get("page",0)
        search_documents.append({
            "id": f"{document_id}_{i}",
            "document_id": document_id,
            "document_name": document_name,
            "content": chunk.page_content,
            "content_vector": embedding,
            "page_number": page_number,
            "section": "",
            "department": "",
            "version": "",
            "effective_date": None,
            "access_level": "internal",
        })

    # 5. Upload to Azure AI Search
    upload_documents(search_documents)

    print(f"Successfully indexed {len(search_documents)} chunks.")

if __name__ == "__main__":

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")
        ingest_pdf(pdf_file)