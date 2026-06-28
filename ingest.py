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

# Em Docker, o volume está montado na pasta "db/" e não pode ser apagado.
# Em vez de apagar a pasta, apagamos apenas o conteúdo interno.
if os.path.exists(CHROMA_PATH):
    for item in os.listdir(CHROMA_PATH):
        item_path = os.path.join(CHROMA_PATH, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

docs = []

def ocr_pdf(path):
    images = convert_from_path(path)
    text = ""
    for img in images:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name)
            text += extract_image_text(tmp.name) + "\n"
    return text


# Verificar se existem PDFs na pasta docs/
pdf_files = [f for f in os.listdir("docs") if f.endswith(".pdf")]

if not pdf_files:
    print("⚠️  Nenhum PDF encontrado em docs/. A criar base vazia...")
else:
    for file in pdf_files:
        path = f"docs/{file}"
        print(f"  → A processar: {file}")
        try:
            loader = PyPDFLoader(path)
            pages = loader.load()
            text = "\n".join([p.page_content for p in pages])

            if len(text.strip()) < 100:
                text = ocr_pdf(path)

            # Limpeza: remove linhas duplicadas
            text = "\n".join(list(dict.fromkeys(text.split("\n"))))

            docs.append(Document(
                page_content=text,
                metadata={"source": file}
            ))
        except Exception as e:
            print(f"  ⚠️  Erro ao processar {file}: {e}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " "]
)

chunks = splitter.split_documents(docs)
print("Chunks:", len(chunks))

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"local_files_only": True}
)

# Só cria a base se houver chunks; caso contrário cria uma base vazia
if chunks:
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print("✅ Base criada com", len(chunks), "chunks")
else:
    # Cria base vazia para que o rag.py não falhe ao arrancar
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    print("✅ Base vazia criada (adiciona PDFs à pasta docs/ e reinicia)")
