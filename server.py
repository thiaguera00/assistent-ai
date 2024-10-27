from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.functions.main import *
import re

class ClassificarNivelInput(BaseModel):
    resposta1: str
    resposta2: str
    resposta3: str

class RespostaRequest(BaseModel):
    questao: str
    resposta: str

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
def api_gerar_questao(nivel: str, conteudo: str):
    questao = gerar_questao(nivel, conteudo)
    questao_formatada = formatar_saida(questao)
    
    return {"questao": questao_formatada}

@app.post("/corrigir-codigo/")
def api_corrigir_codigo(codigo: str):
    correcao = corrigir_codigo(codigo)
    correcao_formatada = formatar_saida(correcao)

    return {"correcao": correcao_formatada}

@app.post("/dar-feedback/")
def api_dar_feedback(codigo: str):
    feedback = dar_feedback(codigo)
    feedback_formatada = formatar_saida(feedback)

    return {"feedback": feedback_formatada}

@app.post("/classificar-nivel/")
async def api_classificar_nivel(input_data: ClassificarNivelInput):
    resposta1 = input_data.resposta1
    resposta2 = input_data.resposta2
    resposta3 = input_data.resposta3

    print("Recebendo respostas:", resposta1, resposta2, resposta3)

    try:
        nivel_resposta = classificar_nivel_estudante(resposta1, resposta2, resposta3)

        return {"nivel": nivel_resposta}
    except Exception as e:
        print("Erro ao classificar o nível do estudante:", e)
        return {"erro": "Ocorreu um erro ao classificar o nível do estudante."}
    
@app.post("/gerar_questionario")
def gerar_questionario_algoritmo():
    questionario = gerar_questionario_questao()
    
    return {'questionario': questionario}

@app.post("/verficar_resposta_questionario")
def resposta_questionario(payload: RespostaRequest):
    resposta = verificar_repostas_questionario(payload.questao, payload.resposta)
    
    return {'resposta': resposta}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
