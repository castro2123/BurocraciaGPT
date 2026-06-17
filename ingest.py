import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import *
from ocr import extract_image_text

from pdf2image import convert_from_path
import tempfile

print("📄 A carregar documentos...")

if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)

docs = []

def ocr_pdf(path):
    images = convert_from_path(path)
    text = ""

    for img in images:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name)
            text += extract_image_text(tmp.name) + "\n"

    return text


for file in os.listdir("docs"):

    if not file.endswith(".pdf"):
        continue

    path = f"docs/{file}"

    loader = PyPDFLoader(path)
    pages = loader.load()

    text = "\n".join([p.page_content for p in pages])

    if len(text.strip()) < 100:
        text = ocr_pdf(path)

    # 🔥 LIMPEZA CRÍTICA (remove lixo repetitivo)
    text = "\n".join(list(dict.fromkeys(text.split("\n"))))

    docs.append(Document(
        page_content=text,
        metadata={"source": file}
    ))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " "]
)

chunks = splitter.split_documents(docs)

print("Chunks:", len(chunks))

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"local_files_only": True, "device": "cuda"}
)

db = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory=CHROMA_PATH
)

db.persist()

print("✅ Base criada")