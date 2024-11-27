from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import subprocess
import traceback
import json
import re
from typing import Tuple

def init_llm():
    load_dotenv()
    chave_api = os.getenv("API_KEY")

    return ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", api_key=chave_api)

llm = init_llm()

def parse_markdown_to_json(text: str) -> dict:
    text = re.sub(r"```json|```", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON: {e}")

def gerar_questao(conteudo):
    message = HumanMessage(
        content=f"""Crie uma questão de programação em Python para um iniciante sobre o conteúdo: '{conteudo}'.
        A resposta deve estar no formato de JSON puro, sem quaisquer marcações de Markdown.
        Formato desejado:
        {{
            "titulo": "Título da questão",
            "objetivo": "Objetivo da questão",
            "instrucao": "Instrução detalhada",
            "exemplo": "Um exemplo ou dica se aplicável"
        }}
        Certifique-se de que a resposta seja apenas o JSON, sem formatação adicional."""
    )
    resposta = llm.invoke([message])
    questao_completa = parse_markdown_to_json(resposta.content)

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
    feedback_llm = resposta_llm.content

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
    return resposta.content

def classificar_nivel_estudante(resposta1, resposta2, resposta3):
    message = HumanMessage(
        content=(
            f"Classifique o nível de programação do estudante como iniciante, intermediário ou avançado "
            f"baseado nas seguintes informações:\n"
            f"- Nível de conhecimento: '{resposta1}'\n"
            f"- Linguagem de programação com a qual já teve contato: '{resposta2}'\n"
            f"- Objetivo ao aprender programação: '{resposta3}'\n"
            f"Responda apenas com o nível e uma breve justificativa."
        )
    )
    resposta = llm.invoke([message])
    return resposta.content

def gerar_questionario_questao(conteudo: str):
    """
    Gera uma questão objetiva de múltipla escolha baseada no conteúdo fornecido.
    """
    message_content = (
        f"Crie uma questão objetiva de múltipla escolha sobre o conteúdo '{conteudo}', adequada para iniciantes. "
        f"A questão deve ter exatamente quatro alternativas, com apenas uma das alternativas corretas. "
        f"Inclua também o raciocínio necessário para identificar a resposta correta e retorne no formato JSON puro. "
        f"O formato deve ser exatamente este: "
        f"{{'question': 'Pergunta...', 'alternatives': [{{'id': 'A', 'text': 'Alternativa A'}}, ...], 'correctAnswer': 'B', 'reasoning': 'Explicação...'}}"
    )

    message = HumanMessage(content=message_content)
    resposta = llm.invoke([message])

    if not resposta or not resposta.content.strip():
        raise ValueError("Erro: o modelo não retornou uma resposta.")

    conteudo_resposta = resposta.content.strip()
    conteudo_resposta = re.sub(r'^```json\s*', '', conteudo_resposta)
    conteudo_resposta = re.sub(r'```$', '', conteudo_resposta)

    try:
        questao_completa = json.loads(conteudo_resposta)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar a resposta em JSON: {str(e)} - Resposta recebida: {conteudo_resposta}")

    if not isinstance(questao_completa, dict):
        raise ValueError("Erro: A resposta não é um objeto JSON válido.")

    if "question" not in questao_completa or "alternatives" not in questao_completa or "correctAnswer" not in questao_completa or "reasoning" not in questao_completa:
        raise ValueError(f"Erro: A estrutura da resposta está incompleta ou incorreta. Resposta recebida: {questao_completa}")

    if not isinstance(questao_completa["alternatives"], list) or len(questao_completa["alternatives"]) != 4:
        raise ValueError("Erro: A lista de alternativas deve conter exatamente quatro alternativas.")

    if not all(isinstance(alt, dict) and "id" in alt and "text" in alt for alt in questao_completa["alternatives"]):
        raise ValueError("Erro: Cada alternativa deve ser um objeto contendo 'id' e 'text'.")

    return {
        "question": questao_completa["question"],
        "alternatives": questao_completa["alternatives"],
        "correctAnswer": questao_completa["correctAnswer"],
        "reasoning": questao_completa["reasoning"]
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
    resposta_str = resposta_da_ia.content

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
