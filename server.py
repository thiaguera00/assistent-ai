from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import * 
import re

app = FastAPI(title="Assistente IA", description="Um assistente para auxiliar no aprendizado de Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def formatar_saida(questao: str) -> str:
    questao_formatada = re.sub(r'\*\*(.*?)\*\*', r'\1:', questao)
    questao_formatada = re.sub(r'\n+', '\n', questao_formatada)
    
    return questao_formatada

@app.post("/gerar-questao/")
async def api_gerar_questao(nivel: str, conteudo: str):
    questao = gerar_questao(nivel, conteudo)
    questao_formatada = formatar_saida(questao)
    
    return {"questao": questao_formatada}

@app.post("/corrigir-codigo/")
async def api_corrigir_codigo(codigo: str):
    correcao = corrigir_codigo(codigo)
    correcao_formatada = formatar_saida(correcao)

    return {"correcao": correcao_formatada}

@app.post("/dar-feedback/")
async def api_dar_feedback(codigo: str):
    feedback = dar_feedback(codigo)
    feedback_formatada = formatar_saida(feedback)

    return {"feedback": feedback_formatada}

@app.post("/classificar-nivel")
async def classificar_nivel(resposta1: str, resposta2: str, resposta3: str):
    nivel = classificar_nivel(resposta1, resposta2, resposta3)
    return {"nivel": nivel}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
