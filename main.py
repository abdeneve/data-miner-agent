import os
import json
from typing import TypedDict, Annotated, List, Optional
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. Definição de Esquemas (Estruturas de Saída)
# ==========================================
class PatientRecord(BaseModel):
    patient_id: str = Field(description="Identificador do paciente, ex: Paciente_0")
    insurance_name: Optional[str] = Field(None, description="Seguro ou convênio, ex: Unimed. Apenas se for explícito ou dedutível.")
    insurance_number: Optional[str] = Field(None, description="Número da carteirinha ou convênio, ex: 123456")
    appointment_date: Optional[str] = Field(None, description="Dia desejado para a consulta. Ex: 'sexta-feira', 'na próxima semana'. Pode ser um conceito, não necessariamente uma data exata.")
    status: str = Field(description="O status final informado pela clínica, ex: Confirmada, Remarcada, Cancelada. Se for 'Consulta confirmada', coloque 'Confirmada'.")


# ==========================================
# 2. Definição do Estado do LangGraph
# ==========================================
class GraphState(TypedDict):
    # O caminho para o arquivo de entrada
    input_file: str
    
    # A saída final onde salvaremos
    output_file: str
    
    # A lista de blocos de texto (um para cada conversa)
    conversations: List[str]
    
    # Todos os registros extraídos
    extracted_records: List[dict]


# ==========================================
# 3. Modelos (O minerador)
# ==========================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# O LLM forçando a saída estruturada
structured_llm = llm.with_structured_output(PatientRecord)


# ==========================================
# 4. Nós do LangGraph
# ==========================================

def load_and_split_node(state: GraphState) -> GraphState:
    """Lê o log e separa as conversas."""
    print("-> Carregando logs e separando conversas...")
    
    try:
        with open(state["input_file"], "r", encoding="utf-8") as f:
            content = f.read()
            
        # O arquivo está dividido em blocos separados por 2 quebras de linha (\n\n)
        blocks = content.strip().split("\n\n")
        
        # Filtrar blocos vazios, por precaução
        blocks = [b.strip() for b in blocks if b.strip()]
        
        print(f"-> Foram encontradas {len(blocks)} conversas para analisar.")
        
        # Iniciamos as variáveis de estado
        state["conversations"] = blocks
        state["extracted_records"] = []
        return state
        
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        state["conversations"] = []
        return state


def extract_data_node(state: GraphState) -> GraphState:
    """Extrai as entidades de cada conversa usando LLM estruturado."""
    
    conversations = state.get("conversations", [])
    extracted_records = state.get("extracted_records", [])
    
    print(f"-> Minerando dados de {len(conversations)} conversas (removendo ruído)...")
    
    # Opcional: Para evitar rate limits massivos (se houvesse muitos blocos), enviaremos um a um.
    for i, convo in enumerate(conversations):
        try:
            # Você pode observar o progresso
            if (i+1) % 10 == 0:
                print(f"   Analisando {i+1} de {len(conversations)}...")
                
            prompt = f"""Você estará analisando registros de chat clínicos entre uma Clínica e um Paciente. 
Há muito "ruído" como imagens anexadas e áudios, ou interações automáticas. Ignore-os.

Encontre este registro, limpe o ruído e extraia os dados específicos solicitados no esquema estruturado.

<Conversa>
{convo}
</Conversa>
"""        
            
            result: PatientRecord = structured_llm.invoke(prompt)
            # Acumulamos o dict
            extracted_records.append(result.model_dump())
            
        except Exception as e:
            print(f"Erro ao extrair dados no registro {i}: {e}")
            
    state["extracted_records"] = extracted_records
    return state


def aggregate_and_save_node(state: GraphState) -> GraphState:
    """Salva tudo em um JSON final."""
    
    output_file = state.get("output_file")
    records = state.get("extracted_records", [])
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
            
        print(f"-> Extraídos e inseridos {len(records)} registros com sucesso.")
        print(f"-> Salvos em: {output_file}")
        
    except Exception as e:
        print(f"Erro ao salvar arquivo {output_file}: {e}")
        
    return state


# ==========================================
# 5. Configurar e invocar o Grafo
# ==========================================

workflow = StateGraph(GraphState)

workflow.add_node("load_and_split", load_and_split_node)
workflow.add_node("extract_data", extract_data_node)
workflow.add_node("save_to_json", aggregate_and_save_node)

workflow.add_edge(START, "load_and_split")
workflow.add_edge("load_and_split", "extract_data")
workflow.add_edge("extract_data", "save_to_json")
workflow.add_edge("save_to_json", END)

app = workflow.compile()


if __name__ == "__main__":
    if not os.path.exists("output"):
        os.makedirs("output")
        
    # Inicializar estado inicial
    inputs = {
        "input_file": "input/logs_clinica_br.txt",
        "output_file": "output/log_estruturado.json",
        "conversations": [],
        "extracted_records": []
    }
    
    print("Iniciando Agente...")
    app.invoke(inputs)
    print("Fim.")
