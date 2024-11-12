from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import subprocess
import traceback
from typing import Tuple

def init_llm():
    load_dotenv()
    chave_api = os.getenv("API_KEY")

    return ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", api_key=chave_api)

llm = init_llm()

def gerar_questao(conteudo):
    message = HumanMessage(content=f"Crie uma questão de programação em Python para um iniciante, com o conteúdo de {conteudo}. faça uma questão simples para não gerar muita dificuldade")
    resposta = llm.invoke([message])
    parser = StrOutputParser()
    questao_completa = parser.invoke(resposta)

    return {
        "questao": questao_completa
    }

def corrigir_codigo(questao: str, codigo: str) -> Tuple[bool, str]:
    """
    Corrige e avalia um código Python submetido, retornando se está correto e um feedback detalhado.

    Args:
    - questao: A descrição da tarefa/questão que o código deve resolver.
    - codigo: O código Python submetido pelo usuário.

    Returns:
    - Tuple[bool, str]: Um par contendo se o código está correto e o feedback.
    """

 
    message = HumanMessage(content=f"Você recebeu a seguinte questão: {questao}\n\nVerifique se o seguinte código resolve corretamente a questão. Avalie o código e forneça feedback sobre sua correção e melhorias:\n{codigo}")
    resposta_llm = llm.invoke([message])
    parser = StrOutputParser()
    feedback_llm = parser.invoke(resposta_llm)

    try:
        with open("temp_code.py", "w") as f:
            f.write(codigo)

        result = subprocess.run(
            ["python", "temp_code.py"],
            capture_output=True,
            text=True,
            timeout=5 
        )
      
        if result.returncode == 0:
            if "incorreto" in feedback_llm.lower() or "não está correto" in feedback_llm.lower():
                esta_correto = False
            else:
                esta_correto = True
            return esta_correto, f"O código foi executado com sucesso. Aqui estão algumas sugestões:\n\n{feedback_llm}"

        else:
            return False, f"Erro ao executar o código. Saída do erro:\n{result.stderr}\n\nSugestão do LLM sobre o código:\n{feedback_llm}"

    except subprocess.TimeoutExpired:
        return False, "O código excedeu o limite de tempo de execução. Tente otimizá-lo para evitar loops infinitos ou longas execuções."

    except Exception as e:
        error_details = traceback.format_exc()
        return False, f"Ocorreu um erro inesperado ao avaliar o código:\n{error_details}\n\nSugestão do LLM sobre o código:\n{feedback_llm}"


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

def gerar_questionario_questao(conteudo):
    message_content = (
        f"Crie uma questão objetiva de múltipla escolha sobre o conteúdo '{conteudo}', adequada para iniciantes. "
        f"A questão deve ter exatamente quatro alternativas, com apenas uma das alternativas corretas."
        f"Inclua também o raciocínio necessário para identificar a resposta correta."
    )

    message = HumanMessage(content=message_content)
    resposta = llm.invoke([message])
    parser = StrOutputParser()
    questao_completa = parser.invoke(resposta)

    return {
        "questao": questao_completa
    }

def verificar_resposta_questionario(enunciado, alternativas, resposta):
    alternativas_str = "\n".join(alternativas)

    message_content = f"""
    Verifique se a resposta à questão abaixo está correta.

    Enunciado da Questão: {enunciado}
    Alternativas:
    {alternativas_str}

    Resposta do usuário: {resposta}

    Por favor, responda se a resposta está correta ou incorreta.
    Se estiver incorreta, explique detalhadamente o porquê, mas sem revelar a resposta correta.

    Formato de resposta esperado:
    - Correto: [sim/não]
    - Explicação: [forneça uma explicação detalhada]
    """

    message = HumanMessage(content=message_content)
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

