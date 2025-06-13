import mysql.connector
import os
import pandas as pd
from tqdm import tqdm


db = mysql.connector.connect(
    host="mysql",
    user="root",
    password=os.environ["DATABASE_PASSWORD"],
)

cursor = db.cursor()

cursor.execute("USE collaboration_network")

df = pd.read_csv(
    "/app/Back End/data/categorised_data/papers_categorised.csv",
    low_memory=False,
)


for index, row in tqdm(
    df.iterrows(), total=df.shape[0], desc="Inserting data into the Database"
):
    try:
        # Convert NaN/NaT to None for SQL NULL
        authors = str(row["Authors"]) if pd.notna(row["Authors"]) else None
        authors_id = str(row["Author(s) ID"]) if pd.notna(row["Author(s) ID"]) else None
        title = str(row["Title"]) if pd.notna(row["Title"]) else None
        year = int(row["Year"])  # Handle Year as integer
        keywords = (
            str(row["Author Keywords"]) if pd.notna(row["Author Keywords"]) else None
        )
        category = str(row["Category"]) if pd.notna(row["Category"]) else None
        doi = str(row["DOI"]) if pd.notna(row["DOI"]) else None
        citations = str(row["Cited by"]) if pd.notna(row["Cited by"]) else "0"
        svd = str(row["SVD"]) if pd.notna(row["SVD"]) else None

        # Parameterized query with placeholders (%s)
        query = """
           INSERT INTO PAPERS
           (Authors, Authors_ID, Title, Year, Author_Keywords, Category, Citations, DOI, SVD)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
       """
        cursor.execute(
            query,
            (authors, authors_id, title, year, keywords, category, citations, doi,svd),
        )
        db.commit()
    except mysql.connector.Error as e:
        print(f"Error at row {row['DOI']}: {e}")
        continue

cursor.close()
db.close()
