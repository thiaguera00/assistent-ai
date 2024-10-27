from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

def init_llm():
    load_dotenv()
    chave_api = os.getenv("API_KEY")

    return ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", api_key=chave_api)

llm = init_llm()

def gerar_questao(nivel, conteudo):
    message = HumanMessage(content=f"Crie uma questão de programação em Python para um iniciante no nível {nivel}, com o conteúdo de {conteudo}.")
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def corrigir_codigo(codigo):
    message = HumanMessage(content=f"Corrija este código em Python e explique os erros:\n{codigo}")
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def dar_feedback(codigo):
    message = HumanMessage(content=f"Analise este código em Python e sugira melhorias:\n{codigo}")
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def classificar_nivel_estudante(resposta1, resposta2, resposta3):
    message = HumanMessage(
        content=(
            f"Classifique o nível de programação do estudante como iniciante, intermediário ou avançado "
            f"baseado nas seguintes informações:\n"
            f"- Nível de conhecimento: '{resposta1}'\n"
            f"- Linguagem de programação com a qual já teve contato: '{resposta2}'\n"
            f"- Objetivo ao aprender programação: '{resposta3}'\n"
            f"Responda apenas com o nível e uma breve justificativa."
            f"Responda como se tivesse falando com esse estudante"
        )
    )
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def gerar_questionario_questao():
    message = HumanMessage(content=f"Crie uma questão objetiva sobre algoritmo")
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def verificar_repostas_questionario(questao, resposta):
    message = HumanMessage(
        content=f"Verifique se a resposta à questão '{questao}' é válida:\n{resposta}, mas se for errada explique sem da a resposta correta"
        )
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)
