#!/usr/bin/env python
import matplotlib.pyplot as plt
import networkx as nx
import code

def normalize(values, bounds):
    return [bounds['desired']['lower'] + (x - bounds['actual']['lower']) * (bounds['desired']['upper'] - bounds['desired']['lower']) / (bounds['actual']['upper'] - bounds['actual']['lower']) for x in values]

def plot(chain):
    from markov_chain_modeling import get_key
    plt.style.use('dark_background')
    init = 'atat'
    G = nx.DiGraph()
    maxsize = chain.connections[get_key(init, 1, chain.order)].maxsize()
    for ch,weight in zip(chain.connections[get_key(init, 1, chain.order)].elements, chain.connections[get_key(init, 1, chain.order)].cummulative_weights):
        if ch not in ['\x00', '\x02']:
            n_weight = normalize([weight], {'desired':{'lower':0,'upper':255}, 'actual':{'lower':0., 'upper':maxsize}})[0]
            print(ch, n_weight, weight)
            hex_n_weight = '{0:0{1}X}'.format(int(n_weight),2)
            hex_n_weight_invert = '{0:0{1}X}'.format(255-int(n_weight),2)
            color = f'#ffffff{hex_n_weight_invert}'
            G.add_edge(init, ch, weight=weight, color=color)
            # for ch2,weight2 in zip(chain.connections[get_key(init+ch, 1, chain.order)].elements, chain.connections[get_key(init+ch, 1, chain.order)].cummulative_weights):
            #     if ch2 not in ['\x00', '\x02']:
            #         G.add_edge(ch, ch2, weight=weight2)
    edges = G.edges()
    raw_weights = [G[u][v]['weight'] for u,v in edges]
    colors = [G[u][v]['color'] for u,v in edges]
    normalized_weights = normalize(raw_weights, {'desired':{'lower':1,'upper':10}, 'actual':{'lower':0, 'upper':maxsize}})
    pos = nx.spring_layout(G, k=100.00, iterations=200)
    nx.draw_networkx_nodes(G, pos, node_size=180, node_color='white')
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=colors, width=normalized_weights, arrowstyle='-|>', arrowsize=10)
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif', font_color='black')
    plt.axis('off')
    plt.show()
