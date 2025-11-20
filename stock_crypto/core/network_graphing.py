# just a bit of skiddadling right now, nothing too serious yet

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import urllib.request
# suggestion by ChatGPT in a brainstorming session
from networkx.algorithms import community as nx_comm
from scipy.spatial import ConvexHull
import plotly.io as pio
from data.fetch_data import fetch_stock_data

def get_company_info():
    '''Fetches company names and sectors for S&P 500 companies from Wikipedia'''

    # fetch the wikipedia page
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    tables = pd.read_html(html)

    # extract company names, sectors and tickers
    company_names = tables[1]['Security'].tolist()  
    company_sector = tables[1]['GICS Sector'].tolist()
    sp500_tickers = tables[1]['Symbol'].tolist()
    # wikipedia uses dots in some ticker symbols, but yfinance needs dashes (e.g. BF.B -> BF-B)
    sp500_tickers = [t.replace(".", "-") for t in sp500_tickers]

    # create a dictionary mapping tickers to names and sectors
    company_info = {}
    for i, ticker in enumerate(sp500_tickers):
        # map ticker to name and sector
        company_info[ticker] = {
            'name': company_names[i],
            'sector': company_sector[i]
        }
    return company_info

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
                G.add_edge(nodes[i], nodes[j], weight=corr_value)

    return G


# threshold is chosen for best performance and visibility
def plot_network(df_correlation, threshold):
    '''Plots the graph with plotly'''

    G = create_network(df_correlation, threshold)

    pio.templates.default = "plotly_dark"

    # use spring layout, most meaningful
    pos = nx.spring_layout(G, seed=42, k=6, method="energy")

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

 
    # aoppend with data from teh nodes
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # get adjacencies and average correlation
        adjacencies = list(G.neighbors(node))
        node_info = f'{node}<br>Connections: {len(adjacencies)}'
        if len(adjacencies) > 0:
            correlations = [G[node][adj]['weight'] for adj in adjacencies]
            avg_corr = np.nanmean(correlations) if len(correlations) else 0.0
            node_info += f'<br>Avg Correlation: {avg_corr:.3f}'

       
        node_text.append(node_info)

        # change colours based on amount of adjacencies(not yet implemented)
        node_colors.append(len(adjacencies))

    # create plotly figure
    fig = go.Figure()
    clustering(G, pos, fig)

    # add edges with data
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#8888aa'),
        hoverinfo='none',
        mode='lines',
        name='Connections'))
   
    # add nodes with data
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=list(G.nodes()),
        hovertext=node_text,
        textposition="middle center",
        marker=dict(
            showscale=True,
            colorscale = 'jet',
            color=node_colors,
            size=20,
            colorbar=dict(
                thickness=15,
                len=0.5,
                x=1.1,
                title="Connections"),
        ),
        name='Stocks'))

    # created with the help of claude since I usually never use plotly, also very tiring/boring to do all of it by myself
    fig.update_layout(
        title=dict(
            text=f'Stock Correlation Network (threshold: {threshold})',
            font=dict(size=16)),
        autosize=True,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[dict(
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002,
            xanchor='left', yanchor='bottom',
            font=dict(color='gray', size=10))],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='black',
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
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html
    G_clean = G.copy()
    G_clean.remove_nodes_from(list(nx.isolates(G_clean)))
    communities = nx_comm.greedy_modularity_communities(G_clean)
    partition = {node: cid for cid, comm in enumerate(
        communities) for node in comm}

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

            x_hull = list(hull_points[:, 0]) + [hull_points[0, 0]]
            y_hull = list(hull_points[:, 1]) + [hull_points[0, 1]]

            # color code the clusters
            color = f"rgba({(cid*53) % 256}, {(cid*97) % 256}, {(cid*137) % 256}, 0.2)"

            # add clusters as shape
            fig.add_shape(
                type="path",
                path="M " + " L ".join(f"{x},{y}" for x,
                                       y in zip(x_hull, y_hull)) + " Z",
                fillcolor=color,
                line=dict(color="rgba(100, 100, 255, 0.2)"),
                layer="below")

        else:
            continue
