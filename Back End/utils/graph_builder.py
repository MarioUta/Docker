from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from tqdm import tqdm
import pandas as pd
from collaborators import Author, Paper
import mysql.connector
import os

CONNECTION = mysql.connector.connect(
    host="db",
    user="root",
    password=os.environ["DATABASE_PASSWORD"],
    ssl_disabled=True,
)
CURSOR = CONNECTION.cursor()
CURSOR.execute("USE collaboration_network")


def graph_builder(df: pd.DataFrame, MAX_THREADS=5, BATCH_SIZE=100):
    nodes = []
    collaboration_network = pd.DataFrame()

    def process_row(row):
        collaborators = str(row["Authors"]).split(";")
        author_ids = [i.strip() for i in str(row["Authors_ID"]).split(";")]
        title = str(row["Title"])
        doi = str(row["DOI"])

        authors_formatted = [
            (" ".join(author.split(" ")[:-1]).strip(), author.split(" ")[-1])
            for author in collaborators
        ]

        authors = []
        row_nodes = []
        for name, id in zip(authors_formatted, author_ids):
            author = Author(name[0], name[1], id)
            authors.append(author)
            row_nodes.append(author)

        category = float(row["Category"])
        citations = float(row["Citations"])
        title = str(row["Title"])
        paper = Paper(title, doi, category, citations, *authors)

        new_edges = pd.DataFrame(columns=["author_1", "author_2"])
        if len(paper.authors) >= 2:
            pairs = combinations([f"{a.id}" for a in paper.authors], 2)
            new_edges = pd.DataFrame(pairs, columns=["author_1", "author_2"])
            new_edges["category"] = category
            new_edges["title"] = title
            new_edges["doi"]=doi
        return row_nodes, new_edges

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results_iter = executor.map(process_row, (row for _, row in df.iterrows()))
        results_iter = tqdm(results_iter, total=df.shape[0], desc="Processing DF")

        batch = []
        for result in results_iter:
            batch.append(result)

            if len(batch) >= BATCH_SIZE:
                # Process nodes batch
                nodes_batch = [node for rn, _ in batch for node in rn]
                nodes.extend(nodes_batch)

                # Process edges batch
                edges_batch = pd.concat([ne for _, ne in batch], ignore_index=True)
                collaboration_network = pd.concat(
                    [collaboration_network, edges_batch], ignore_index=True
                )
                batch = []

        # Process remaining records in the last batch
        if batch:
            nodes_batch = [node for rn, _ in batch for node in rn]
            nodes.extend(nodes_batch)

            edges_batch = pd.concat([ne for _, ne in batch], ignore_index=True)
            collaboration_network = pd.concat(
                [collaboration_network, edges_batch], ignore_index=True
            )

    return collaboration_network, nodes


if __name__ == "__main__":
    CURSOR.execute("SELECT * FROM PAPERS")
    rows = CURSOR.fetchall()
    papers = pd.DataFrame(rows, columns=[col[0] for col in CURSOR.description])
    collaboration_network, nodes = graph_builder(papers)

    edge_data = [
        tuple(x)
        for x in collaboration_network[
            ["author_1", "author_2", "category", "title","doi"]
        ].to_numpy()
    ]
    query = """
    INSERT INTO EDGES
    (author_1, author_2, category, title, doi)
    VALUES (%s, %s, %s, %s, %s)
    """
    print("Inserting Edges")
    CURSOR.executemany(query, edge_data)

    nodes = {
        node.id: [
            node.get_category(),
            node.get_score(),
            node.initials + " " + node.last_name,
        ]
        for node in nodes
    }
    node_data = [(n, nodes[n][0], nodes[n][1], nodes[n][2]) for n in nodes]
    query = """
    INSERT INTO NODES
    (author_id, category, score, name)
    VALUES (%s, %s, %s, %s)
    """
    print("Inserting Nodes")
    CURSOR.executemany(query, node_data)
    CURSOR.execute("commit")
    CURSOR.close()
    CONNECTION.close()
