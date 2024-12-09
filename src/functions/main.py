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

def corrigir_codigo(questao: str, codigo: str) -> dict:
    """
    Corrige e avalia um código Python submetido, retornando se está correto e um feedback estruturado no formato JSON.

    Args:
    - questao: A descrição da tarefa/questão que o código deve resolver.
    - codigo: O código Python submetido pelo usuário.

    Returns:
    - dict: Um dicionário contendo as chaves "esta_correto" e "feedback".
    """
    def limpar_markdown_para_json(texto: str) -> dict:
        """
        Remove formatação de Markdown e estrutura o feedback em JSON.
        """
        texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
        texto = re.sub(r"`(.*?)`", r"\1", texto)
        texto = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)
        texto = texto.strip()

        partes = re.split(r"Feedback:|Correção:|Melhorias:", texto)
        partes = [p.strip() for p in partes if p.strip()]

        feedback = {
            "resumo": partes[0] if len(partes) > 0 else "",
            "correcao": partes[1] if len(partes) > 1 else "",
            "melhorias": partes[2] if len(partes) > 2 else ""
        }

        return feedback

    if not codigo.strip():
        return {
            "esta_correto": False,
            "feedback": {
                "resumo": "Nenhum código foi fornecido.",
                "correcao": "",
                "melhorias": ""
            }
        }

    message = HumanMessage(content=f"Você recebeu a seguinte questão: {questao}\n\nVerifique se o seguinte código resolve corretamente a questão. Avalie o código e forneça feedback sobre sua correção e melhorias:\n{codigo}")
    resposta_llm = llm.invoke([message])
    feedback_llm = limpar_markdown_para_json(resposta_llm.content.strip())

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
            esta_correto = "incorreto" not in resposta_llm.content.lower() and "não está correto" not in resposta_llm.content.lower()
            return {
                "esta_correto": esta_correto,
                "feedback": feedback_llm
            }

        else:
            return {
                "esta_correto": False,
                "feedback": {
                    "resumo": "Erro ao executar o código.",
                    "correcao": result.stderr.strip(),
                    "melhorias": feedback_llm.get("melhorias", "")
                }
            }

    except subprocess.TimeoutExpired:
        return {
            "esta_correto": False,
            "feedback": {
                "resumo": "O código excedeu o limite de tempo de execução.",
                "correcao": "",
                "melhorias": "Tente otimizá-lo para evitar loops infinitos ou longas execuções."
            }
        }

    except Exception as e:
        error_details = traceback.format_exc()
        return {
            "esta_correto": False,
            "feedback": {
                "resumo": "Ocorreu um erro inesperado ao avaliar o código.",
                "correcao": error_details,
                "melhorias": feedback_llm.get("melhorias", "")
            }
        }



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

def gerar_questionario_questao(conteudos: str):
    """
    Gera uma questão objetiva de múltipla escolha baseada no conteúdo fornecido.
    """
    message_content = (
        f"Crie uma questão objetiva de múltipla escolha sobre os conteúdos '{conteudos}', adequada para iniciantes. "
        f"A questão deve ter exatamente quatro alternativas, com apenas uma das alternativas corretas. "
        f"A alternativa correta deve ser selecionada aleatoriamente entre 'A', 'B', 'C' e 'D'. "
        f"Cada alternativa deve incluir uma descrição explicando por que está certa ou errada. "
        f"Inclua também o raciocínio geral necessário para identificar a resposta correta e retorne no formato JSON puro. "
        f"O formato deve ser exatamente este: "
        f"{{"
        f"  'question': 'Pergunta...', "
        f"  'alternatives': ["
        f"    {{'id': 'A', 'text': 'Alternativa A', 'description': 'Explicação para A'}}, "
        f"    {{'id': 'B', 'text': 'Alternativa B', 'description': 'Explicação para B'}}, "
        f"    {{'id': 'C', 'text': 'Alternativa C', 'description': 'Explicação para C'}}, "
        f"    {{'id': 'D', 'text': 'Alternativa D', 'description': 'Explicação para D'}}"
        f"  ], "
        f"  'correctAnswer': 'Uma das alternativas (A, B, C ou D)', "
        f"  'reasoning': 'Explicação geral sobre a resposta correta.'"
        f"}}"
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

    if not all(isinstance(alt, dict) and "id" in alt and "text" in alt and "description" in alt for alt in questao_completa["alternatives"]):
        raise ValueError("Erro: Cada alternativa deve ser um objeto contendo 'id', 'text' e 'description'.")

    if questao_completa["correctAnswer"] not in ['A', 'B', 'C', 'D']:
        raise ValueError("Erro: A resposta correta deve ser uma das alternativas 'A', 'B', 'C' ou 'D'.")

    return {
        "question": questao_completa["question"],
        "alternatives": questao_completa["alternatives"],
        "correctAnswer": questao_completa["correctAnswer"],
        "reasoning": questao_completa["reasoning"]
    }

def gerar_desafio_para_usuario():
    """
    Gera um desafio técnico baseado nos conteúdos aprendidos nas fases anteriores e retorna como JSON.
    """
    conteudo_aprendido = (
        "O usuário aprendeu os seguintes conteúdos: "
        "1. Algoritmo, Variáveis, Constantes, Tipos de dados, Operadores Aritméticos e Lógicos; "
        "2. Comando print, Declaração de variáveis, Tipos de variáveis, Máscara de formatação, Input; "
        "3. Operadores aritméticos, relacionais e lógicos, Estruturas de decisão (if, elif, else), Laços de repetição (for, while); "
        "4. Funções e sua sintaxe."
    )
    
    desafio_prompt = (
        f"Baseado nos conteúdos aprendidos pelo usuário ({conteudo_aprendido}), crie um desafio técnico que "
        f"envolva Python e que o usuário possa utilizar como um projeto para o portfólio. "
        f"O desafio deve ser criativo, relevante e adequado para um iniciante que aprendeu os tópicos mencionados. "
        f"Garanta que o desafio inclua uma breve descrição do que deve ser desenvolvido, os requisitos principais e "
        f"uma explicação de como ele pode ser útil ou interessante para o portfólio. "
        f"Formato esperado de resposta (apenas JSON, sem Markdown): "
        f"{{"
        f"  \"descricao\": \"Descrição breve do desafio\","
        f"  \"requisitos\": [\"Requisito 1\", \"Requisito 2\", \"...\"],"
        f"  \"explicacao\": \"Explicação de como o projeto é útil para o portfólio\""
        f"}}"
    )
    
    message = HumanMessage(content=desafio_prompt)
    resposta = llm.invoke([message])
    
    try:
        desafio_json = parse_markdown_to_json(resposta.content)
    except ValueError as e:
        raise ValueError(f"Erro ao processar o desafio gerado: {e}")

    return desafio_json


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
