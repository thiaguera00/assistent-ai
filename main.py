from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

def init_llm():
    from dotenv import load_dotenv
    import os
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
    message = HumanMessage(content=f"Classifique se o estudante tem o nivel iniciante, intermediário ou avançado em programação com o texto a seguir:
    \nQual é o seu nível de conhecimento em programação?\n 
    Resposta: {resposta1}\n Com qual linguagem de programação você já teve contato? \n Resposta: {resposta2}\n Qual é o seu objetivo ao aprender programação?\n Resposta: {resposta3}.\n quero uma saída onde uma linha vai ter o nivel que você classificou e em outra o linha o por que essa pessoa está nesse nivel")
    resposta = llm.invoke([message])
    parser = StrOutputParser()
    
    return parser.invoke(resposta)
