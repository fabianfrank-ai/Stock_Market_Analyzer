"""
Creates a networking graph with clustering via plotly, so everything is interactable.
Further explanation can be found in the notebook
"""
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import urllib.request

# suggestion by ChatGPT in a brainstorming session, explained it in the corresponding notebook
from networkx.algorithms import community as nx_comm
from scipy.spatial import ConvexHull
import plotly.io as pio


class network_graph:
    '''
    This class creates a networking graph if you enter a correlation dataframe and threshold via plotly
    '''

    def __init__(self, correlations, threshold):
        self.correlations = correlations
        self.threshold = threshold

        self.fig = go.Figure()
        self.plot_network()

    def get_company_info(self):
        '''
        Fetches company names and sectors for S&P 500 companies from Wikipedia
        We need that for the hover text to get further insight and judge the eg clusters better
        '''

        # fetch the wikipedia page
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        tables = pd.read_html(html)

        # extract company names, sectors and tickers, also more robust by checking all tables
        for table in tables:
            try:
                company_names = table['Security'].tolist()
                company_sector = table['GICS Sector'].tolist()
                sp500_tickers = table['Symbol'].tolist()
            except Exception:
                pass

        # wikipedia uses dots in some ticker symbols, but yfinance needs dashes (e.g. BF.B -> BF-B)
        sp500_tickers = [t.replace(".", "-") for t in sp500_tickers]

        # create a dictionary mapping tickers to names and sectors
        self.company_info = {}
        for i, ticker in enumerate(sp500_tickers):
            # map ticker to name and sector
            self.company_info[ticker] = {
                'name': company_names[i],
                'sector': company_sector[i]
            }

    def create_network(self):
        '''
        Creates a network graph out of a correlation matrix
        Returns a Graph G that can be used to create further stuff
        If there are questions about plotly have a look at notebooks/network_guide.ipynb
        '''

        self.G = nx.Graph()

        # add nodes to G
        nodes = self.correlations.index.to_list()

        self.G.add_nodes_from(nodes)

        # add edges based on threshold
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                corr_value = self.correlations.iloc[i, j]
                if abs(corr_value) >= self.threshold:
                    self.G.add_edge(nodes[i], nodes[j], weight=corr_value)

    # threshold is chosen for best performance and visibility

    def plot_network(self):
        '''
        Plots the graph with plotly

        If there are questions about plotly have a look at notebooks/network_guide.ipynb
        '''
        self.create_network()
        pio.templates.default = "plotly_dark"

        # use spring layout, most meaningful
        self.pos = nx.spring_layout(self.G, seed=42, k=6, method="energy")

        # create lists for edges
        edge_x = []
        edge_y = []
        edge_info = []
        edge_colors = []

        # append the lists with data from the edges
        for edge in self.G.edges():
            x0, y0 = self.pos[edge[0]]
            x1, y1 = self.pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            weight = self.G[edge[0]][edge[1]]['weight']
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

        self.get_company_info()

        # aoppend with data from teh nodes
        for node in self.G.nodes():
            x, y = self.pos[node]
            node_x.append(x)
            node_y.append(y)

            # get adjacencies and average correlation
            adjacencies = list(self.G.neighbors(node))
            node_info = f'{node}<br> Company: {self.company_info.get(node, {}).get("name", "N/A")} <br> Sector: {self.company_info.get(node, {}).get("sector", "N/A")} <br> Connections: {len(adjacencies)}'
            if len(adjacencies) > 0:
                correlations = [self.G[node][adj]['weight']
                                for adj in adjacencies]
                avg_corr = np.nanmean(correlations) if len(
                    correlations) else 0.0
                node_info += f'<br>Avg Correlation: {avg_corr:.3f}'

            node_text.append(node_info)

            # change colours based on amount of adjacencies(not yet implemented)
            node_colors.append(len(adjacencies))

        # create plotly figure
        self.clustering()

        # add edges with data
        self.fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#8888aa'),
            hoverinfo='none',
            mode='lines',
            name='Connections'))

        # add nodes with data
        self.fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=list(self.G.nodes()),
            hovertext=node_text,
            textposition="middle center",
            marker=dict(
                showscale=True,
                colorscale='jet',
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
        self.fig.update_layout(
            title=dict(
                text=f'Stock Correlation Network (threshold: {self.threshold})',
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

    def clustering(self):
        '''Cluster the data using greedy modularity'''

        # remove non-existing nodes and partition the existing ones (otherwise nx will literally scream at you in agony)
        # replaced louvain with greedy modularity because louvain failed consistently
        # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html
        G_clean = self.G.copy()
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

                points = np.array([self.pos[node] for node in nodes])
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]

                x_hull = list(hull_points[:, 0]) + [hull_points[0, 0]]
                y_hull = list(hull_points[:, 1]) + [hull_points[0, 1]]

                # color code the clusters
                color = f"rgba({(cid*53) % 256}, {(cid*97) % 256}, {(cid*137) % 256}, 0.2)"

                # add clusters as shape
                self.fig.add_shape(
                    type="path",
                    path="M " + " L ".join(f"{x},{y}" for x,
                                           y in zip(x_hull, y_hull)) + " Z",
                    fillcolor=color,
                    line=dict(color="rgba(100, 100, 255, 0.2)"),
                    layer="below")

            else:
                continue
