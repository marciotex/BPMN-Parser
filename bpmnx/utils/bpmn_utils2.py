import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import warnings  # Import the warnings library

# Define the XML file path
xml_file = 'static/bpmn.xml'

# Define the function to extract all elements and attributes
def extract_elements_from_bpmn(xml_file, element_tags, namespaces):
    # Parse the XML file
    tree = ET.parse(xml_file)
    # Get the root element
    root = tree.getroot()
    # Create an empty list to store the extracted elements
    elements = []
    # Dictionary to count all relevant elements in the XML
    total_elements = {tag: len(root.findall(f'.//bpmn:{tag}', namespaces)) for tag in element_tags}
    # Dictionary to keep track of extracted elements
    extracted_elements_count = {tag: 0 for tag in element_tags}
    # Iterate over all possible elements and add them to the list
    for tag in element_tags:
        found_elements = root.findall(f'.//bpmn:{tag}', namespaces)
        elements += found_elements
        extracted_elements_count[tag] += len(found_elements)
    # Compare the count with the extracted elements
    missing_elements = {tag: total_elements[tag] - extracted_elements_count[tag] for tag in element_tags if total_elements[tag] != extracted_elements_count[tag]}
    if missing_elements:
        # Issue a warning if there is a discrepancy
        missing_elements_str = ', '.join([f"{tag}: {count}" for tag, count in missing_elements.items()])
        warnings.warn(f"Some elements were not extracted: {missing_elements_str}.")
    return elements

# Define namespaces
namespaces = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

# List of all elements that can be extracted from BPMN
# according to the BPMN 2.0 specification (https://www.omg.org/spec/BPMN/2.0/)
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
    'conditionalEventDefinition', 'errorEventDefinition', 'escalationEventDefinition',
    'messageEventDefinition', 'signalEventDefinition', 'timerEventDefinition',
    'cancelEventDefinition', 'compensateEventDefinition', 'terminateEventDefinition', 'linkEventDefinition'
]

# Define the function to build the graph and store artifacts and graphic elements in dictionaries
def build_bpmn_graph_and_dictionaries(xml_file, graph_elements, artifact_elements, graphic_elements):
    elements = extract_elements_from_bpmn(xml_file, element_tags, namespaces)    
    G = nx.DiGraph()  # Graph to store main BPMN elements
    artifacts = {}    # Dictionary to store artifacts
    graphics = {}     # Dictionary to store graphic elements
        
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

# Define the elements to be stored in the graph
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
# Define the elements to be stored in the Artifacts list
artifact_elements = [
    'dataObject', 'dataObjectReference', 'dataStore', 'dataStoreReference', 'dataInput', 'dataOutput',
    'textAnnotation', 'group'
]

# Define the elements to be stored in the Graphic Elements list
graphic_elements = [
    'BPMNShape', 'BPMNEdge', 'BPMNPlane'
]

# Build the graph and store artifacts and graphic elements in dictionaries
(
    bpmn_graph,
    bpmn_artifacts,
    bpmn_graphics
) = build_bpmn_graph_and_dictionaries(xml_file, graph_elements, artifact_elements, graphic_elements)

# Visualization of the results
print("\nStructured BPMN Graph:")

print("\nNodes:\n")
for node, data in bpmn_graph.nodes(data=True):
    print(node, data)

print("\nEdges (links):\n")
print(bpmn_graph.edges(data=True))

print("\nExtracted BPMN Artifacts:")
for key, value in bpmn_artifacts.items():
    print(f"{key}: {value}")

print("\nExtracted BPMN Graphic Elements:")
for key, value in bpmn_graphics.items():
    print(f"{key}: {value}")
# Make sure Graphviz is installed and accessible on your system
try:
    # Try to use PyGraphviz for the 'dot' layout
    pos = nx.nx_agraph.graphviz_layout(bpmn_graph, prog='dot')
except ImportError:
    try:
        # Alternatively, use PyDot if PyGraphviz is not available
        pos = nx.nx_pydot.graphviz_layout(bpmn_graph, prog='dot')
    except ImportError:
        print("PyGraphviz or PyDot is not installed, using spring_layout as a fallback")
        pos = nx.spring_layout(bpmn_graph)  # Fallback to spring_layout if necessary

# Increase the figure size for better readability
fig, ax = plt.subplots(figsize=(40, 36))  # Adjust the size as needed
nx.draw(bpmn_graph, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=12, ax=ax)

# Save the drawing to a file with increased spacing
plt.savefig("static/graph.png")

# Display a message indicating where the file was saved
print("The graph drawing has been saved in the file 'static/graph.png'")