from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.functions.main import *
from typing import List
import random

class ClassificarNivelInput(BaseModel):
    resposta1: str
    resposta2: str
    resposta3: str

class RespostaRequest(BaseModel):
    questao: str
    alternativas: str
    resposta: str

class GerarQuestaoRequest(BaseModel):
    conteudo: List[str]

class CodigoRequest(BaseModel):
    questao: str
    codigo: str

class Feedback(BaseModel):
    resumo: str
    correcao: str
    melhorias: str

class CorrecaoResponse(BaseModel):
    esta_correto: bool
    feedback: Feedback

app = FastAPI(title="Assistente IA", description="Um assistente para auxiliar no aprendizado de Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/gerar-questao/")
def api_gerar_questao(request: GerarQuestaoRequest):
    try:
        if not request.conteudo:
            raise ValueError("A lista de conteúdos está vazia.")

        conteudo_escolhido = random.choice(request.conteudo)

        questao = gerar_questao(conteudo_escolhido)
        return questao
    except Exception as e:
        return {"erro": str(e)}

@app.post("/verificar-resposta-questionario/")
def api_verificar_resposta_questionario(payload: RespostaRequest):
    """Verifica a resposta de uma questão e fornece feedback detalhado"""
    resposta = verificar_resposta_questionario(payload.questao, payload.alternativas, payload.resposta)

    return {
        "correto": resposta["correto"],
        "mensagem": resposta["mensagem"]
    }

@app.post("/corrigir-codigo/", response_model=CorrecaoResponse)
def api_corrigir_codigo(request: CodigoRequest):
    """
    API para corrigir código Python submetido pelo usuário.
    """
    try:
        resposta = corrigir_codigo(request.questao, request.codigo)
        feedback = Feedback(
            resumo=resposta["feedback"]["resumo"],
            correcao=resposta["feedback"]["correcao"],
            melhorias=resposta["feedback"]["melhorias"]
        )

        return CorrecaoResponse(
            esta_correto=resposta["esta_correto"],
            feedback=feedback
        )

    except Exception as e:
        return {"error": f"Erro ao corrigir o código: {str(e)}"}

@app.post("/dar-feedback/")
def api_dar_feedback(codigo: str):
    feedback = dar_feedback(codigo)
    return {"feedback": feedback}

@app.post("/desafio/") 
def api_desafio():
    desafio = gerar_desafio_para_usuario()
    return {"desafio": desafio}

@app.post("/gerar-questionario/")
def api_gerar_questionario(conteudos: List[str]):
    """
    Endpoint para gerar uma questão objetiva de múltipla escolha.
    Aceita uma lista de conteúdos e escolhe um aleatoriamente.
    """
    if not conteudos or not isinstance(conteudos, list):
        return {"erro": "Nenhum conteúdo válido fornecido."}

    conteudo_escolhido = random.choice(conteudos)

    try:
        questao = gerar_questionario_questao(conteudo_escolhido)
        return questao 
    except Exception as e:
        return {"erro": str(e)}

@app.post("/classificar-nivel/")
async def api_classificar_nivel(input_data: ClassificarNivelInput):
    resposta1 = input_data.resposta1
    resposta2 = input_data.resposta2
    resposta3 = input_data.resposta3

    try:
        nivel_resposta = classificar_nivel_estudante(resposta1, resposta2, resposta3)
        return {"nivel": nivel_resposta}
    except Exception as e:
        return {"erro": "Ocorreu um erro ao classificar o nível do estudante."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
