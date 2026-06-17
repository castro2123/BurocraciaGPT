import streamlit as st
import time
from rag import search
from llm import generate
from ocr import extract_image_text
from pdf2image import convert_from_path
import tempfile
import os

st.set_page_config(page_title="Burocracia GPT 🇵🇹")

# =========================
# STATE
# =========================

if "chat" not in st.session_state:
    st.session_state.chat = []

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "show_arch" not in st.session_state:
    st.session_state.show_arch = False

# =========================
# UPLOAD FILES
# =========================

st.sidebar.title("📄 Upload de documentos")

uploaded_file = st.sidebar.file_uploader(
    "Carrega PDF ou imagem (carta, documento, etc.)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# =========================
# EXTRACÇÃO TEXTO
# =========================

def extract_pdf_text(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name)
            text += extract_image_text(tmp.name) + "\n"
    return text

if uploaded_file:

    with st.spinner("📄 A ler documento..."):

        file_type = uploaded_file.name.split(".")[-1].lower()

        if file_type == "pdf":

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            text = extract_pdf_text(tmp_path)

        else:
            text = extract_image_text(uploaded_file)

        st.session_state.doc_text = text

    st.success("✅ Documento carregado e analisado!")


# =========================
# BOTÃO ARQUITETURA
# =========================

col1, col2 = st.columns([8, 1])

with col2:
    if st.button("🧠"):
        st.session_state.show_arch = True

if st.session_state.show_arch:

    st.title("🧠 Arquitetura do sistema")

    # =========================
    # 📊 DIAGRAMA VISUAL
    # =========================

    st.subheader("📊 Fluxo do sistema")

    st.graphviz_chart("""
    digraph G {
        rankdir=LR;

        User -> Query;

        Query -> Decision;

        Decision -> Upload [label="com documento"];
        Decision -> RAG [label="sem documento"];

        Upload -> OCR;
        OCR -> DocText;

        DocText -> Merge;
        RAG -> Merge;

        Merge -> Context;
        Context -> LLM;
        LLM -> Response;
        Response -> User;
    }
    """)

    # =========================
    # 🧠 EXPLICAÇÃO SIMPLES
    # =========================

    st.subheader("🧠 Explicação simples")

    st.markdown("""
Este sistema pode funcionar de duas formas:

### 🔹 1. Sem documento (modo normal)
- O utilizador faz apenas uma pergunta  
- O sistema procura informação na base de conhecimento  
- Usa RAG para encontrar conteúdo relevante  
- O modelo gera uma resposta  

---

### 🔹 2. Com documento (modo análise)
- O utilizador envia um PDF ou imagem  
- O sistema extrai o texto (**OCR / PDF**)  
- Junta esse texto com a pesquisa na base  
- O modelo analisa e explica o documento  

---

👉 Nos dois casos, o objetivo é o mesmo:  
dar uma resposta clara com base em informação real.
""")

    # =========================
    # ⚙️ TECNOLOGIAS
    # =========================

    st.subheader("⚙️ Tecnologias utilizadas")

    st.markdown("""
- **Streamlit** → Interface do chat  
- **ChromaDB** → Base de dados vetorial  
- **HuggingFace Embeddings** → Compreensão semântica  
- **Ollama (Llama3)** → Geração de respostas  
- **EasyOCR** → Leitura de imagens  
- **PyPDF / pdf2image** → Leitura de PDFs  
""")

    # =========================
    # 🔄 FLUXO DETALHADO
    # =========================

    st.subheader("🔄 Passo a passo")

    st.markdown("""
1. 🧑 O utilizador faz uma pergunta  
2. 📄 (Opcional) envia um documento  
3. 🔍 Se existir documento → extrai texto (OCR/PDF)  
4. 🧠 A pergunta é convertida em embeddings  
5. 📚 O sistema procura informação relevante  
6. 🧩 Junta contexto (documento + base de dados)  
7. 🤖 O LLM gera a resposta  
8. ✅ O utilizador recebe uma explicação simples  
""")

    # =========================
    # 💡 IDEIA CHAVE
    # =========================

    st.subheader("💡 Ideia chave")

    st.info("""
O sistema adapta-se automaticamente:

📄 Com documento → analisa a carta  
💬 Sem documento → responde com base na base de conhecimento  

Não inventa respostas — usa sempre contexto real.
""")

    if st.button("❌ Fechar"):
        st.session_state.show_arch = False
        st.rerun()

    st.stop()

# =========================
# CHAT
# =========================

st.title("🇵🇹 Burocracia GPT")

query = st.chat_input("Escreve a tua dúvida...")

if query:

    st.session_state.chat.append({"role": "user", "content": query})

    with st.status("🔍 A analisar documento + base de dados...", expanded=True) as status:

        st.write("📄 A ler contexto do documento...")

        doc_context = st.session_state.doc_text

        st.write("🧠 A procurar na base vetorial...")

        docs, confidence, debug = search(query + " " + doc_context)

        context = ""

        if docs:
            context = "\n\n".join([d.page_content[:500] for d in docs])

        if doc_context:
            context = doc_context + "\n\n" + context

        st.write("🤖 A gerar resposta...")

        if not context.strip():
            resposta = "❌ Não consegui encontrar informação suficiente."
        else:
            resposta = generate(context, query)

        status.update(label="✅ Resposta pronta!", state="complete")

    st.session_state.chat.append({
        "role": "assistant",
        "content": resposta,
        "query": query,
        "confidence": confidence,
        "debug": debug,
        "context": context
    })

# =========================
# DISPLAY CHAT
# =========================

for m in st.session_state.chat:

    if m["role"] == "user":
        st.markdown(f"🧑 {m['content']}")

    else:
        st.markdown(f"🤖 {m['content']}")
        st.write(f"📊 Confiança: {m.get('confidence', 0):.2f}")

        with st.expander("🧠 Como foi gerada"):

            st.write("❓ Pergunta:", m.get("query", ""))
            st.text(m.get("context", ""))

            debug = m.get("debug", [])

            for i, d in enumerate(debug):
                st.markdown(f"Chunk {i+1} (score {d['score']:.2f})")
                st.write(d["text"])

st.divider()
st.write("🧠 RAG + OCR + LLM System")