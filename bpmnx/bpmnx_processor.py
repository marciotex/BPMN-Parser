#Para garantir que o script run_results.py encontre os módulos corretamente, você deve ajustar o PythonPATH 
# no início do seu script para incluir o diretório do seu aplicativo Django. Aqui está como você pode fazer isso:
import os
import sys

# Adicione o diretório do seu projeto Django ao PythonPATH
django_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(django_project_path)

# Agora você pode importar os módulos do seu aplicativo Django, com caminho absoluto
from bpmnx.utils.bpmn_utils import parse_xml
#from bpmn_utils import parse_xml
from bpmnx.utils.data_utils import process_bpmn_data

# O os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) obtém o diretório pai do diretório
#  atual (onde está o run_result.py), que é o diretório raiz do seu projeto Django (BPMN-Parser). 
# sys.path.append(django_project_path) adiciona esse diretório ao PythonPATH, permitindo que o Python 
# encontre os módulos dentro do seu aplicativo Django (parser).

def run_results(filename=None):
    # Diretório onde o arquivo BPMN será salvo por padrão
    default_xmlpath = "static/upload/bpmn.xml"

    # Se o filename não foi passado como argumento, use o default_xmlpath
    if filename is None:
        filename = default_xmlpath

    try:
        myroot = parse_xml(filename)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    lanes_data, task_data, event_data, processes_data, total_time, cycle_time, gateways_name, sum_events, sum_tasks, sum_lanes, sum_processes, flows = process_bpmn_data(myroot)

    print("Lanes:", lanes_data)
    print("Tasks:", task_data)
    print("Events:", event_data)
    print("Processes:", processes_data)
    print("Gateways:", gateways_name)
    print("Flows:", flows)
    print("Total Time:", total_time)
    print("Sum Events:", sum_events)
    print("Sum Tasks:", sum_tasks)
    print("Sum Lanes:", sum_lanes)
    print("Sum Processes:", sum_processes)
    print("Cycle Time:", cycle_time)

if __name__ == "__main__":
    # Verifica se um argumento de linha de comando foi fornecido
    if len(sys.argv) > 1:
        filename = sys.argv[1]  # O primeiro argumento após o nome do script é o nome do arquivo
    else:
        filename = None  # Caso nenhum argumento seja fornecido, use o arquivo padrão

    run_results(filename)
