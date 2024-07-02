import networkx as nx

# Função para encontrar todas as trajetórias possíveis em um grafo
def encontrar_todas_trajetorias(G, inicio, fim, trajetoria=[]):
    trajetoria = trajetoria + [inicio]
    if inicio == fim:
        return [trajetoria]
    trajetorias = []
    for vizinho in G.neighbors(inicio):
        if vizinho not in trajetoria:
            trajetorias_extendidas = encontrar_todas_trajetorias(G, vizinho, fim, trajetoria)
            for trajetoria_extendida in trajetorias_extendidas:
                trajetorias.append(trajetoria_extendida)
    return trajetorias

# Criar um grafo direcionado
G = nx.DiGraph()

# Adicionar arestas ao grafo (exemplo de grafo com 2 arestas de início)
G.add_edge('A', 'B')
G.add_edge('A', 'C')
G.add_edge('E', 'B')  # Segunda aresta de início
G.add_edge('B', 'D')
G.add_edge('C', 'D')

# Descobrir os nós iniciais (nós sem predecessores)
inicios = [n for n in G.nodes() if G.in_degree(n) == 0]

# Descobrir os nós finais (nós sem sucessores)
fins = [n for n in G.nodes() if G.out_degree(n) == 0]

# Encontrar e imprimir todas as trajetórias possíveis dos nós iniciais para os nós finais
for inicio in inicios:
    for fim in fins:
        trajetorias = encontrar_todas_trajetorias(G, inicio, fim)
        print(f"Todas as trajetórias possíveis de {inicio} para {fim}:")
        for trajetoria in trajetorias:
            print(trajetoria)
