from utils.database_management import retrieve_nodes
import matplotlib as mpl
import networkx as nx
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


MIN_THICKNESS = 15
MAX_THICKNESS = 30


def set_edge_attributes(collaboration_newtork):
    collaboration_newtork["weight"] = collaboration_newtork["weight"] - 1
    G = nx.from_pandas_edgelist(collaboration_newtork, "author_1", "author_2", "weight")
    colors = [
        "#000000",
        "#000000",  # Black (start)
        "#FFFF00",  # Yellow (middle)
        "#FF0000",  # Red (end)
    ]
    collaboration_newtork["weight"] = collaboration_newtork["weight"].astype(int)

    max_weight = max(list(collaboration_newtork["weight"]))
    custom_cmap = LinearSegmentedColormap.from_list("my_cmap", colors)
    colors = custom_cmap(np.linspace(0, 1, max_weight + 1))
    opacity = np.linspace(0.1, 1, max_weight + 1)
    color_map = [
        {
            "r": int(color[0] * 255),
            "g": int(color[1] * 255),
            "b": int(color[2] * 255),
            "a": a,
        }
        for color, a in zip(colors, opacity)
    ]

    edge_attributes = pd.DataFrame()
    edge_attributes["author_1"] = collaboration_newtork["author_1"]
    edge_attributes["author_2"] = collaboration_newtork["author_2"]
    edge_attributes["weight"] = collaboration_newtork["weight"] * 10

    edge_attributes["color"] = collaboration_newtork["weight"].apply(
        lambda x: color_map[x]
    )

    edge_viz_dict = {
        (row["author_1"], row["author_2"]): {
            "viz": {
                "color": row["color"],
            }
        }
        for _, row in edge_attributes.iterrows()
    }

    nx.set_edge_attributes(G, edge_viz_dict)
    return G


def set_node_attributes(G, path=None):
    pos = nx.random_layout(G)
    node_data = retrieve_nodes(G.nodes())
    node_data = node_data.fillna("18.0")
    coordinates = pd.DataFrame.from_dict(pos)
    coordinates = coordinates.T.reset_index().rename(
        columns={"index": "author_id", 0: "x", 1: "y"}
    )
    node_data["x"] = coordinates["x"]
    node_data["y"] = coordinates["y"]

    n_lines = 300
    cmap = mpl.colormaps["viridis"]
    colors = cmap(np.linspace(0, 1, n_lines))
    rgb_colors = [
        {"color": {"r": int(r * 255), "g": int(g * 255), "b": int(b * 255), "a": a}}
        for r, g, b, a in colors
    ]

    color = pd.DataFrame()
    color["author_id"] = node_data["author_id"]
    color["category"] = node_data["category"].astype(float).astype(int)
    color["color"] = color["category"].apply(lambda i: rgb_colors[i])
    node_data["score"] = node_data["score"].astype(float).astype(int)
    scoring = np.linspace(5, 20, max(node_data["score"]) + 1)
    node_data["score"] = node_data["score"].apply(lambda i: scoring[i])

    nx.set_node_attributes(
        G,
        pd.Series(node_data["name"].values, index=node_data["author_id"]).to_dict(),
        "label",
    )

    nx.set_node_attributes(
        G,
        pd.Series(node_data["score"].values, index=node_data["author_id"]).to_dict(),
        "size",
    )

    nx.set_node_attributes(
        G,
        pd.Series(node_data["category"].values, index=node_data["author_id"]).to_dict(),
        "category",
    )

    nx.set_node_attributes(
        G,
        pd.Series(coordinates["x"].values, index=node_data["author_id"]).to_dict(),
        "x",
    )

    nx.set_node_attributes(
        G,
        pd.Series(coordinates["y"].values, index=node_data["author_id"]).to_dict(),
        "y",
    )

    nx.set_node_attributes(
        G,
        pd.Series(color["color"].values, index=node_data["author_id"]).to_dict(),
        "viz",
    )

    #if path:
    #    nx.write_gexf(G, path)

    return node_data, G
