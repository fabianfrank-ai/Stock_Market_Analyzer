# just a bit of skiddadling right now, nothing too serious yet

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from networkx.algorithms import community as nx_comm # suggestion by ChatGPT in a brainstorming session
from scipy.spatial import ConvexHull
import plotly.io as pio
from data.fetch_data import fetch_stock_data

from core.indicators import atr

def create_network(df_correlation, threshold):
    '''Creates a network graph out of a correlation matrix'''

    G = nx.Graph()

    # add nodes to G
    nodes = df_correlation.index.to_list()

    G.add_nodes_from(nodes)


    # add edges based on threshold
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            corr_value = df_correlation.iloc[i, j]
            if abs(corr_value) >= threshold:
                G.add_edge(nodes[i], nodes[j], weight = corr_value)
    
    
    return G



# threshold is chosen for best performance and visibility
def plot_network(df_correlation, threshold):
    '''Plots the graph with plotly'''
    
    G = create_network(df_correlation, threshold)


    pio.templates.default = "plotly_dark"


    # use spring layout, most meaningful
    pos = nx.spring_layout(G, seed = 42, k = 6, method = "energy")
 
    
    # create lists for edges
    edge_x = []
    edge_y = []
    edge_info = []
    edge_colors = []
    

    # append the lists with data from the edges
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        weight = G[edge[0]][edge[1]]['weight']
        edge_info.append(f'{edge[0]} - {edge[1]}: {weight:.3f}')
        
        if weight > 0:
            edge_colors.extend(['green', 'green', None])
        else:
            edge_colors.extend(['red', 'red', None])
    

    # create lists for nodes
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    atr_node =[]
    node_data = fetch_stock_data(G.nodes, '6mo', '1d')
    print(G.nodes)
    print(node_data)
    # aoppend with data from teh nodes
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        
        #atr_node.append(node_data)
       
        adjacencies = list(G.neighbors(node))
        node_info = f'{node}<br>Connections: {len(adjacencies)}'
        if len(adjacencies) > 0:
            correlations = [G[node][adj]['weight'] for adj in adjacencies]
            avg_corr = np.mean(correlations)
            node_info += f'<br>Avg Correlation: {avg_corr:.3f}'
        node_text.append(node_info)
        
        # change colours based on amount of adjacencies(not yet implemented)
        node_colors.append(len(adjacencies))
    
    # DEBUG
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    
    
    # create plotly figure
    fig = go.Figure()
    clustering(G, pos, fig)
    

    # add edges
    fig.add_trace(go.Scatter(
        x = edge_x, y = edge_y,
        line = dict(width = 1, color = '#8888aa'),
        hoverinfo = 'none',
        mode = 'lines',
        name = 'Connections'))


    
    # add nodes
    fig.add_trace(go.Scatter(
        x = node_x, y = node_y,
        mode = 'markers+text',
        hoverinfo = 'text',
        text = list(G.nodes()),
        hovertext = node_text,
        textposition = "middle center",
        marker = dict(
            showscale = True,
            colorscale = 'Plotly3',
            color = node_colors,
            size = atr_node ,
            colorbar = dict(
                thickness = 15,
                len = 0.5,
                x = 1.1,
                title = "Connections"),
            line = dict(width = 2, color = 'white')
        ),
        name = 'Stocks'))
    
    


    # created with the help of claude since I usually never use plotly
    fig.update_layout(
        title = dict(       
            text = f'Stock Correlation Network (threshold: {threshold})',
            font = dict(size = 16)),
        autosize = True,
        showlegend = False,
        hovermode = 'closest',
        margin = dict(b = 20,l = 5,r = 5,t = 40),
        annotations = [ dict(
            showarrow = False,
            xref = "paper", yref = "paper",
            x = 0.005, y = -0.002,
            xanchor = 'left', yanchor = 'bottom',
            font = dict(color = 'gray', size = 10))],
        xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
        yaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
        plot_bgcolor = 'black',
        paper_bgcolor='black',
        font_color='white',
        hoverlabel=dict(
        bgcolor="white",
        font_color="black"))
    
    
    



    return fig





def clustering(G, pos, fig):
    '''Cluster the data'''
 
    
    # remove non-existing nodes and partition the existing ones (otherwise nx will literally scream at you in agony)
    # replaced louvain with greedy modularity because louvain failed consistently (do not ask me why, I went through enough)
    G_clean = G.copy() 
    G_clean.remove_nodes_from(list(nx.isolates(G_clean)))
    communities = nx_comm.greedy_modularity_communities(G_clean)
    partition = {node: cid for cid, comm in enumerate(communities) for node in comm}


    # Group the clusters
    clusters = {}
    for node, cid in partition.items():
        clusters.setdefault(cid, []).append(node)

    # Create a convec hull and a shape
    for cid, nodes in clusters.items():
        if len(nodes) >= 3:
    
            points = np.array([pos[node] for node in nodes])
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]

            x_hull = list(hull_points[:,0]) + [hull_points[0,0]]
            y_hull = list(hull_points[:,1]) + [hull_points[0,1]]

            # color code the clusters
            color = f"rgba({(cid*53)%256}, {(cid*97)%256}, {(cid*137)%256}, 0.2)"

            # add clusters as shape
            fig.add_shape(
                    type="path",
                    path="M " + " L ".join(f"{x},{y}" for x, y in zip(x_hull, y_hull)) + " Z",
                    fillcolor = color,
                    line=dict(color="rgba(100, 100, 255, 0.2)"),
                    layer="below")

        else:
            continue
   


  




   
