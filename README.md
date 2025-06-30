## IA asssistente
Esse assistente está usando o LangChain para criar um modelo do gemini e gerar um assistente para auxiliar o aprendizado em Python
## Instalação
É necessário o Python instalado na sua maquina e o pip. </br>

Após clonar o projeto você tem que instalar as dependências com o seguinte comando:

```bash
$ pip install -r requirements.txt
```

Após instalar as dependências crie um arquivo ".env" na raiz e coloque sua API_KEY fornecida no <a href="https://ai.google.dev/gemini-api?gad_source=1&gclid=CjwKCAjwlbu2BhA3EiwA3yXyu1H_Yn8ngmHneYhX_mk2mjXbT5huMuZ7uU_HGPnZBhyD3YF_R38z-xoC4dgQAvD_BwE&hl=pt-br"> Gemini </a>

```bash
$ API_KEY=""
```
## Rotas
Atualmente tem 3 rotas:

```bash
 api/gerar-questao/
```
Gera questões de acordo com o nível do estudante e do conteúdo 
```bash
 api/corrigir-codigo/
```
Corrige códigos dos estudantes

```bash
 api/dar-feedback/
```

Fornece feedback do código e possiveis melhorias
