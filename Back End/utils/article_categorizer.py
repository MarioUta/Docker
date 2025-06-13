import numpy as np
import pandas as pd
import pickle
from tqdm import tqdm
import json
from helpers import categories
from sentence_transformers import SentenceTransformer



def categoriser(files):
    df = pd.DataFrame()
    for file in files:
        file_df = pd.read_csv(file)
        df = pd.concat([df, file_df])

    author_keywords = df[["Author Keywords", "DOI"]]
    author_keywords["Author Keywords"] = author_keywords["Author Keywords"].astype(str)
    author_keywords["Author Keywords"] = author_keywords["Author Keywords"].apply(
        lambda x: ";".join(
            [
                keyword.strip()
                .replace("<sub>", "")
                .replace("</sub>", "")
                .replace("<sup>", "")
                .replace("</sup>", "")
                .lower()
                for keyword in x.split(";")
                if pd.notna(x)
            ]
        )
    )

    author_keywords.loc["Category"] = np.nan
    author_keywords.loc["SVD"] = np.nan
    with open(
        "/app/Back End/python_objects/ml_models/kmeans_model.pkl",
        "rb",
    ) as file:
        kmeans_model = pickle.load(file)


    author_keywords = author_keywords[pd.notna(author_keywords["Author Keywords"])]

    sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
    for i, row in tqdm(
        author_keywords.iterrows(),
        total=author_keywords.shape[0],
        desc="Categorising articles",
    ):
        keywords_encoded = sentence_transformer.encode(row["Author Keywords"].split(";"))

        word_categories = np.array(keywords_encoded)

        def f(row):
            return categories(kmeans_model, [row])

        word_categories = np.apply_along_axis(f, axis=1, arr=word_categories)
        category = max(word_categories, key=lambda x: list(word_categories).count(x))

        author_keywords.loc[i, "Category"] = category
        svd=sentence_transformer.encode([row["Author Keywords"]])
        svd=np.array(svd)
        author_keywords.loc[i, "SVD"] = json.dumps(svd[0].tolist())

    author_keywords = author_keywords[["DOI", "Category", "SVD"]]
    author_keywords = author_keywords[pd.notna(author_keywords["DOI"])]

    df["Category"] = np.nan
    df["SVD"] = np.nan
    for _, row in tqdm(
        author_keywords.iterrows(),
        total=author_keywords.shape[0],
        desc="Joining tables",
    ):
        index = df.index[df["DOI"] == row["DOI"]].to_list()[0]
        df.loc[index, "Category"] = row["Category"]
        df.loc[index, "SVD"] = row["SVD"]

    df.to_csv(
        "/app/Back End/data/categorised_data/papers_categorised.csv",
        index=False,
    )


if __name__ == "__main__":
    documents_list = [
        "/app/Back End/data/climateChange.csv",
        "/app/Back End/data/EcosystemsServices.csv",
        "/app/Back End/data/Eutrophication.csv",
        "/app/Back End/data/InvasiveSpecies.csv",
    ]
    categoriser(documents_list)
