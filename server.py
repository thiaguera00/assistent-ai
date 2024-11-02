from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.functions.main import *  # Importando suas funções principais
import re

class ClassificarNivelInput(BaseModel):
    resposta1: str
    resposta2: str
    resposta3: str

class RespostaRequest(BaseModel):
    questao: str
    resposta: str

class GerarQuestaoRequest(BaseModel):
    conteudo: str
    nivel: str = "normal"

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
def api_gerar_questao(request: GerarQuestaoRequest):
    """Gera uma questão com base no conteúdo e nível de dificuldade especificado"""
    questao = gerar_questionario_questao(request.conteudo, dificuldade=request.nivel)
    questao_formatada = formatar_saida(questao)
    
    return {"questao": questao_formatada}

def extrair_conteudo_da_questao(questao: str) -> str:
    """
    Tenta extrair dinamicamente o conteúdo da questão.
    Neste exemplo, vamos supor que o conteúdo esteja na primeira linha ou 
    que possamos deduzir de palavras-chave.
    """
    palavras_chave = ["algoritmo", "variáveis", "estruturas de controle", "loops", "funções", "tipos de dados", "listas", "condicionais"]

    for palavra in palavras_chave:
        if palavra.lower() in questao.lower():
            return palavra

    return "conteúdo geral"

@app.post("/verificar-resposta-questionario/")
def api_verificar_resposta_questionario(payload: RespostaRequest):
    """Verifica a resposta de uma questão e fornece feedback detalhado"""
    resposta = verificar_resposta_questionario(payload.questao, payload.resposta)

    return {
        "correto": resposta["correto"],
        "mensagem": resposta["mensagem"]
    }

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

@app.post("/gerar-questionario/")
def api_gerar_questionario(request: GerarQuestaoRequest):
    """Gera uma questão de questionário com base no conteúdo e nível de dificuldade especificado"""
    questao = gerar_questionario_questao(request.conteudo, dificuldade=request.nivel)
    questao_formatada = formatar_saida(questao)
    return {"questao": questao_formatada}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
