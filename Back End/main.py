import sys
import json
from utils.database_management import (
    retrieve_edges,
    retrieve_papers,
)
from utils.helpers import categories
from utils.ml_tools.model_loader import model_loader
from utils.set_attributes import set_node_attributes, set_edge_attributes
from sklearn.metrics.pairwise import cosine_similarity
from networkx.readwrite import json_graph
import pandas as pd
from utils.helpers import send_message
import numpy as np
import pickle

HOST = "db"  # localhost
PORT = 5000
PATH = "/app/graph_files"


if __name__ == "__main__":
    search = sys.argv[1]
    category = None
    id = sys.argv[2]
    
    if search == "1":
        keywords = sys.argv[2]
        id = sys.argv[3]
        sentence_transformer, kmeans_model = model_loader()
        keywords = sentence_transformer.encode([keywords])
        category = categories(kmeans_model, keywords)

    collaboration_newtork = retrieve_edges(category)

    if search == "1":
        path = PATH + f"/graph_{category}.gexf"
    else:
        path = PATH + "/graph.gexf"

    node_data, G = set_node_attributes(set_edge_attributes(collaboration_newtork), path)
    graph = G.copy()
    graph = json_graph.node_link_data(graph)
    author_names = list(node_data.sort_values("score", ascending=False)[:10]["name"])
    author_ids = list(node_data.sort_values("score", ascending=False)[:10]["author_id"])

    '''
    with open(
        "/home/mario/Documents/Facultate/Licenta/Code/Back End/python_objects/whole_graph.pkl",
        "wb",
    ) as f:
        pickle.dump((node_data, G), f)
    '''
   
    
    author_graphs = [
        json_graph.node_link_data(
            G.subgraph([center_node] + list(G.neighbors(center_node))).copy()
        )
        for center_node in author_ids
    ]
    papers = pd.DataFrame(retrieve_papers(category=category))
    papers[2] = papers[2].apply(lambda x: json.loads(x))
    paper_vectors = np.array(papers[2].tolist())

    # Make sure 'keywords' is a 2D array (1 sample)
    if isinstance(keywords, list):
        keywords = np.array(keywords).reshape(1, -1)

    # Compute cosine similarity
    similarities = cosine_similarity(keywords, paper_vectors).flatten()

    # Store similarities for ranking
    papers["similarity"] = similarities

    # Optional: Sort and display top matches
    papers = papers.sort_values("similarity", ascending=False)[:10]
    print(list(papers[0]))

    message = {
        "type": "topic",
        "id": id,
        "content": {
            "graph": graph,
            "papers": list(papers[0]),
            "authors": {
                "author_names": author_names,
                "author_ids": author_ids,
                "author_graphs": author_graphs,
            },
            "category": str(category),
        },
    }
    send_message(message)
