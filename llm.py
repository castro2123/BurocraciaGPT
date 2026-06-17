import requests
from config import *

def generate(context, question):

    prompt = f"""
És um assistente especializado em burocracia portuguesa.

REGRAS:
- NÃO copies texto do contexto
- NÃO uses "etc"
- NÃO listes pontos do documento
- Resume de forma natural e simples
- Ignora partes contraditórias do contexto
- Se o contexto for técnico/legal, prioriza definição geral e não detalhes repetitivos.

FORMATO:

📘 Explicação simples
🧾 Informação relevante do documento (paráfrase)
⚠️ Nota importante se necessário

CONTEXTO:
{context}

PERGUNTA:
{question}
"""

    res = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
    )

    return res.json()["response"]