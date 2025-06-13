import pandas as pd
import mysql.connector
import os


CONNECTION = mysql.connector.connect(
    host="db",
    user="root",
    password=os.environ["DATABASE_PASSWORD"],
)

CURSOR = CONNECTION.cursor()


def retrieve_edges(category=None):
    CURSOR.execute("USE collaboration_network")
    if category is not None:
        query = (
            "SELECT sub.author_1 as author_1, sub.author_2 as author_2, count(*) as weight\n"
            "FROM (\n"
            "   Select	author_1,	author_2\n"
            "   FROM	EDGES\n"
            f"  WHERE 	category = {category}\n"
            ") sub\n"
            "GROUP BY	author_1,	author_2;\n"
        )
    else:
        query = (
            "SELECT author_1, author_2, count(*) as weight\n"
            "FROM EDGES\n"
            "GROUP BY	author_1,	author_2;\n"
        )

    CURSOR.execute(query)
    rows = CURSOR.fetchall()
    collaboration_network = pd.DataFrame(
        rows, columns=[col[0] for col in CURSOR.description]
    )
    return collaboration_network


def retrieve_nodes(author_ids):
    CURSOR.execute("USE collaboration_network")
    placeholders = ", ".join(["%s"] * len(author_ids))
    query = f"""
    SELECT * 
    FROM NODES 
    WHERE author_id IN ({placeholders})"""

    CURSOR.execute(query, tuple(author_ids))
    rows = CURSOR.fetchall()
    nodes_data = pd.DataFrame(rows, columns=[col[0] for col in CURSOR.description])
    return nodes_data


def retrieve_papers(category=None):
    CURSOR.execute("USE collaboration_network")
    if category is not None:
        query = f"""
            SELECT Title, DOI, SVD
            from PAPERS
            where Category = {category};
            """

    else:
        query = """
            SELECT Title, DOI, SVD
            FROM PAPERS;
        """

    CURSOR.execute(query)
    rows = [(row[0], row[1], row[2]) for row in CURSOR.fetchall()]
    return rows
