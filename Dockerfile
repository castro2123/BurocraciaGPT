FROM python:3.11-slim

# Dependências do sistema para EasyOCR, OpenCV e pdf2image
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Pré-descarregar o modelo de embeddings HuggingFace durante o build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')"

# Garantir que a pasta docs/ existe
RUN mkdir -p docs db

EXPOSE 8501

# O "|| true" garante que mesmo que o ingest falhe, o Streamlit arranca sempre
CMD ["bash", "-c", "python ingest.py || true && streamlit run webapp.py --server.port=8501 --server.address=0.0.0.0"]
