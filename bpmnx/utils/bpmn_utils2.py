import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use um backend não interativo
import matplotlib.pyplot as plt

# Definir o caminho do arquivo XML
xml_file = 'static/bpmn.xml'

# Definir a função para extrair todos os elementos e atributos
def extract_elements_from_bpmn(xml_file, element_tags, namespaces):
    # Analisar o arquivo XML
    tree = ET.parse(xml_file)
    # Obter o elemento raiz
    root = tree.getroot()
    # Criar uma lista vazia para armazenar os elementos
    elements = []
    # Iterar sobre todos os elementos possíveis e adicioná-los à lista
    for tag in element_tags:
        elements += root.findall(f'.//bpmn:{tag}', namespaces)
    return elements

# Definir namespaces
namespaces = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

# Lista de todos os elementos que podem ser extraídos do BPMN
# conforme a especificação BPMN 2.0 (https://www.omg.org/spec/BPMN/2.0/)
# nem todos necessariantemente serão utilizados
element_tags = [
    'definitions', 'import', 'extension',
    'process', 'subProcess', 'transaction', 'adHocSubProcess', 'callActivity',
    'sequenceFlow', 'messageFlow', 'association',
    'startEvent', 'endEvent', 'intermediateThrowEvent', 'intermediateCatchEvent', 'boundaryEvent',
    'task', 'manualTask', 'userTask', 'serviceTask', 'scriptTask', 'businessRuleTask', 'sendTask', 'receiveTask',
    'exclusiveGateway', 'parallelGateway', 'inclusiveGateway', 'complexGateway', 'eventBasedGateway',
    'dataObject', 'dataObjectReference', 'dataStore', 'dataStoreReference', 'dataInput', 'dataOutput',
    'textAnnotation', 'group',
    'collaboration', 'participant', 'messageFlow',
    'choreography', 'choreographyTask', 'subChoreography',
    'conversation', 'subConversation', 'callConversation',
    'BPMNShape', 'BPMNEdge', 'BPMNPlane',
    'conditionalEventDefinition', 'errorEventDefinition', 'escalationEventDefinition',
    'messageEventDefinition', 'signalEventDefinition', 'timerEventDefinition',
    'cancelEventDefinition', 'compensateEventDefinition', 'terminateEventDefinition', 'linkEventDefinition'
]

# Definir a função para construir o grafo e armazenar artefatos e elementos gráficos em dicionários
def build_bpmn_graph_and_dictionaries(xml_file, graph_elements, artifact_elements, graphic_elements):
    elements = extract_elements_from_bpmn(xml_file, element_tags, namespaces)    
    G = nx.DiGraph()  # Grafo para armazenar elementos principais do BPMN
    artifacts = {}    # Dicionário para armazenar artefatos
    graphics = {}     # Dicionário para armazenar elementos gráficos
        
    for elem in elements:
        elem_id = elem.get('id')
        elem_type = elem.tag.split('}')[1]
        attributes = elem.attrib
        
        if elem_type in graph_elements:
            G.add_node(elem_id, type=elem_type, **attributes)
            if elem_type in ['sequenceFlow', 'messageFlow', 'association']:
                source = elem.get('sourceRef')
                target = elem.get('targetRef')
                G.add_edge(source, target, type=elem_type, **attributes)
        elif elem_type in artifact_elements:
            artifacts[elem_id] = {'type': elem_type, **attributes}
        elif elem_type in graphic_elements:
            graphics[elem_id] = {'type': elem_type, **attributes}
    return G, artifacts, graphics

# Definir os elementos a serem armazenados no grafo
graph_elements = [
    'process', 'subProcess', 'transaction', 'adHocSubProcess', 'callActivity',
    'sequenceFlow', 'messageFlow', 'association',
    'startEvent', 'endEvent', 'intermediateThrowEvent', 'intermediateCatchEvent', 'boundaryEvent',
    'task', 'manualTask', 'userTask', 'serviceTask', 'scriptTask', 'businessRuleTask', 'sendTask', 'receiveTask',
    'exclusiveGateway', 'parallelGateway', 'inclusiveGateway', 'complexGateway', 'eventBasedGateway',
    'collaboration', 'participant', 'choreography', 'choreographyTask', 'subChoreography',
    'conversation', 'subConversation', 'callConversation',
    'conditionalEventDefinition', 'errorEventDefinition', 'escalationEventDefinition',
    'messageEventDefinition', 'signalEventDefinition', 'timerEventDefinition',
    'cancelEventDefinition', 'compensateEventDefinition', 'terminateEventDefinition', 'linkEventDefinition'
]
# Definir os elementos a serem armazenados na lista de Artefatos
artifact_elements = [
    'dataObject', 'dataObjectReference', 'dataStore', 'dataStoreReference', 'dataInput', 'dataOutput',
    'textAnnotation', 'group'
]

# Definir os elementos a serem armazenados na lista de Elementos gráficos
graphic_elements = [
    'BPMNShape', 'BPMNEdge', 'BPMNPlane'
]

# Construir o grafo e armazenar artefatos e elementos gráficos em dicionários
(
    bpmn_graph,
    bpmn_artifacts,
    bpmn_graphics
) = build_bpmn_graph_and_dictionaries(xml_file, graph_elements, artifact_elements, graphic_elements)

# Visualização dos resultados
print("\nGrafo BPMN estruturado:")

print("\nNós (nodes):\n")
for node, data in bpmn_graph.nodes(data=True):
    print(node, data)

print("\nVértices (edges, links):\n")
print(bpmn_graph.edges(data=True))

print("\nArtefatos BPMN extraído:")
for key, value in bpmn_artifacts.items():
    print(f"{key}: {value}")

print("\nElementos Gráficos BPMN extraídos:")
for key, value in bpmn_graphics.items():
    print(f"{key}: {value}")
# Certifique-se de que o Graphviz está instalado e acessível no seu sistema
try:
    # Tenta usar o PyGraphviz para o layout 'dot'
    pos = nx.nx_agraph.graphviz_layout(bpmn_graph, prog='dot')
except ImportError:
    try:
        # Como alternativa, usa o PyDot se o PyGraphviz não estiver disponível
        pos = nx.nx_pydot.graphviz_layout(bpmn_graph, prog='dot')
    except ImportError:
        print("PyGraphviz ou PyDot não está instalado, usando spring_layout como fallback")
        pos = nx.spring_layout(bpmn_graph)  # Fallback para spring_layout se necessário

# Aumente o tamanho da figura para melhorar a legibilidade
fig, ax = plt.subplots(figsize=(40, 36))  # Ajuste o tamanho conforme necessário
nx.draw(bpmn_graph, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=12, ax=ax)

# Salve o desenho em um arquivo com espaço aumentado
plt.savefig("static/grafo.png")

# Exiba uma mensagem informando onde o arquivo foi salvo
print("O desenho do grafo foi salvo no arquivo 'static/grafo.png'")