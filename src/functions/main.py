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

def gerar_questionario_questao(conteudo, dificuldade="normal"):
    if dificuldade == "fácil":
        message_content = f"Crie uma questão objetiva fácil sobre o conteúdo {conteudo}, adequada para iniciantes."
    else:
        message_content = f"Crie uma questão objetiva sobre o conteúdo {conteudo}."

    message = HumanMessage(content=message_content)
    resposta = llm.invoke([message])
    parser = StrOutputParser()

    return parser.invoke(resposta)

def verificar_resposta_questionario(questao, resposta):
    message = HumanMessage(
        content=f"""
        Verifique se a resposta à questão abaixo está correta.
        Questão: {questao}
        Resposta do usuário: {resposta}
        
        Por favor, responda se a resposta está correta ou incorreta.
        Se estiver incorreta, explique detalhadamente o porquê, mas sem revelar a resposta correta.
        
        Formato de resposta esperado:
        - Correto: [sim/não]
        - Explicação: [forneça uma explicação detalhada]
        """
    )
    resposta_da_ia = llm.invoke([message])
    parser = StrOutputParser()
    resposta_str = parser.invoke(resposta_da_ia)

    lines = resposta_str.split('\n')
    correto = False
    mensagem = ""

    for line in lines:
        if "Correto:" in line:
            if "sim" in line.lower():
                correto = True
        elif "Explicação:" in line:
            mensagem = line.replace("Explicação:", "").strip()

    return {
        "correto": correto,
        "mensagem": mensagem
    }

def realizar_questionario(conteudo, resposta_usuario):
    questao = gerar_questionario_questao(conteudo, dificuldade="normal")
    resultado = verificar_resposta_questionario(questao, resposta_usuario)

    if resultado["correto"]:
        print("Parabéns! Resposta correta! 🎉")
        print(f"Explicação: {resultado['mensagem']}")
    else:
        print("Resposta incorreta. Vamos tentar com uma questão mais fácil.")
        print(f"Explicação: {resultado['mensagem']}")

        parser = StrOutputParser()
        resposta_str = parser.invoke(questao)
        print("\nAqui está uma nova questão para você praticar:\n")
        print(resposta_str)

