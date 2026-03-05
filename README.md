# Data Miner Agent

Um agente inteligente construído com **Python**, **LangChain** e **LangGraph**, projetado para analisar e extrair dados estruturados de logs brutos de bate-papo de clínicas (como o WhatsApp).

Este agente examina as interações entre a clínica e os pacientes, ignora o ruído (como imagens anexadas, áudios e interações automáticas) e extrai informações essenciais sobre cada consulta, salvando o resultado final em um formato estruturado (JSON).

## 🚀 Funcionalidades

- **Leitura de Logs em Massa**: Carrega registros de bate-papo de um arquivo de texto e os divide em conversas individuais.
- **Extração com IA (LLM)**: Utiliza o modelo `gpt-4o-mini` da OpenAI para remover o "ruído" do bate-papo e focar no que importa.
- **Saída Estruturada**: Garante que os dados sejam formatados corretamente utilizando o Pydantic, extraindo:
  - Identificador do paciente (`patient_id`)
  - Nome do plano de saúde/convênio (`insurance_name`)
  - Número da carteirinha do convênio (`insurance_number`)
  - Data desejada para a consulta (`appointment_date`)
  - Status da consulta (`status`)
- **Pipeline baseada em Grafos**: A lógica de processamento é orquestrada usando o LangGraph (`StateGraph`), permitindo um fluxo de trabalho modular e rastreável.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **LangChain & LangGraph**: Para a orquestração do agente e fluxo dos dados.
- **OpenAI API**: Modelo `gpt-4o-mini` utilizado como o cérebro extrator.
- **Pydantic**: Para definição do esquema estruturado (`PatientRecord`).
- **Python-dotenv**: Para o gerenciamento seguro de variáveis de ambiente.

## 📁 Estrutura de Diretórios e Arquivos

- `main.py`: O script principal onde o fluxo do LangGraph e o modelo LLM são configurados e executados.
- `input/logs_clinica_br.txt`: O arquivo de entrada contendo o log não estruturado das conversas do bate-papo (as conversas devem estar separadas por uma linha em branco).
- `output/log_estruturado.json`: O arquivo de saída (gerado automaticamente) contendo os dados limpos e estruturados de todas as conversas.
- `.env`: Arquivo de variáveis de ambiente usado para armazenar a sua chave de API da OpenAI (não deve ser comitado).

## ⚙️ Como Executar

1. **Clone o repositório** ou navegue até a pasta do projeto.
2. **Instale as dependências** do Python (veja as importações no `main.py`). Recomendamos a criação de um ambiente virtual:
   ```bash
   pip install langchain-openai pydantic langgraph python-dotenv
   ```
3. **Configure as variáveis de ambiente**:
   - Crie um arquivo `.env` na raiz do seu projeto.
   - Adicione sua chave da API da OpenAI da seguinte forma:
     ```env
     OPENAI_API_KEY=sk-sua_chave_de_api_aqui
     ```
4. **Prepare os arquivos de entrada**:
   - Certifique-se de que existe um arquivo `input/logs_clinica_br.txt` com as suas conversas a verificar.
5. **Execute o agente**:
   ```bash
   python main.py
   ```
6. **Verifique os resultados**:
   - O arquivo final será gerado no diretório `output/log_estruturado.json`.

## 🧠 Arquitetura do LangGraph

O agente é estruturado em três nós principais (`workflow`):
1. `load_and_split`: Lê o arquivo de entrada (`logs_clinica_br.txt`) e divide os blocos de texto, cada qual representando uma conversa.
2. `extract_data`: Itera ao longo das conversas, faz chamadas para a OpenAI para invocar a resposta e transforma a saída não estruturada num objeto alinhado com o `PatientRecord`.
3. `save_to_json`: Agrupa os dicionários de registros extraídos e os salva com segurança no arquivo `log_estruturado.json`.

---
Desenvolvido para extração inteligente e automação de fluxos de trabalho médicos/clínicos.
