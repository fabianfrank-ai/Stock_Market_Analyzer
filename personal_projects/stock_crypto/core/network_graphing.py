# just a bit of skiddadling right now, nothing too serious yet

import pandas as pd
import networkx as nx
import plotly.graph_objects as go

from core.market_screener import correlations

def network_graph():
    G = nx.random_geometric_graph(100, 0.125)
    edges = []
    df_correlations = correlations()

    # filter for strong correlations and create nodes based on tickers, create edges if value is bigger than threshold
    threshold = 0.6

    for i, node1 in enumerate(df_correlations.columns):

        for j, node2 in enumerate(df_correlations.columns):

            if i < j:

                 corr_value = df_correlations.iloc[i, j]

            if abs(corr_value) >= threshold:
                edges.append((node1, node2, corr_value))


    # add nodes and edges to graph
    for edge in edges:
        node1, node2, weight = edge
        G.add_edge(node1, node2, weight = weight) 

    
    for ticker in df_correlations.columns:
        G.add_node(ticker)
    


    # trace edges and nodes for plotting
    edge_trace = go.Scatter(
    x = edge_x, y = edge_y,
    line = dict(width = 0.5, color = '#888'),
    hoverinfo = 'none',
    mode = 'lines')

    node_trace = go.Scatter(
    x = node1, y = node2,
    mode = 'markers',
    hoverinfo = 'text',
    marker = dict(
        showscale = True,
        colorscale = 'Electric',
        reversescale = True,
        color = [],
        size = 10,
        colorbar = dict(
            thickness = 15,
            title = dict(
              text = 'Node Connections',
              side = 'right'
            ),
            xanchor = 'left',
        ),
        line_width = 2))


    # Colour the node points
    node_adjacencies = []
    node_text = []

    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text




    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title=dict(
                    text="<br>Network graph made with Python",
                    font=dict(
                        size=16
                    )
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plotly.com/python/network-graphs/'> https://plotly.com/python/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    fig.show()





   