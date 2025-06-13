import pickle
import sys
from utils.helpers import send_message
from networkx.readwrite import json_graph


def jaccard_similarity(str1, str2):
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0


if __name__ == "__main__":
    id = sys.argv[2]
    with open(
        "/app/Back End/python_objects/whole_graph.pkl",
        "rb",
    ) as f:
        node_data, G = pickle.load(f)
    keyword = sys.argv[1]
    node_data["similarity"] = node_data["name"].apply(
        lambda x: jaccard_similarity(x, keyword)
    )
    top_matches = node_data.sort_values(by="similarity", ascending=False).head(10)
    author_names = list(top_matches["name"])
    author_ids = list(top_matches["author_id"])
    author_graphs = [
        json_graph.node_link_data(
            G.subgraph([center_node] + list(G.neighbors(center_node))).copy()
        )
        for center_node in author_ids
    ]
    message = {
        "type": "author",
        "id": id,
        "content": {
            "authors": {
                "author_names": author_names,
                "author_ids": author_ids,
                "author_graphs": author_graphs,
            },
        },
    }
    send_message(message)
