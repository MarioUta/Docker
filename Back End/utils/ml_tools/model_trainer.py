import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from k_means_constrained import KMeansConstrained


def model_trainer(files):
    df = pd.DataFrame()
    for file in files:
        file_df = pd.read_csv(file)
        df = pd.concat([df, file_df])

    author_keywords = df["Author Keywords"]
    author_keywords = list(author_keywords)

    formatted_list = []

    for i in author_keywords:
        if isinstance(i, str):
            for j in i.split(";"):
                formatted_list.append(
                    str(
                        j.strip()
                        .replace("<sub>", "")
                        .replace("</sub>", "")
                        .replace("<sup>", "")
                        .replace("</sup>", "")
                        .lower()
                    )
                )

    formatted_list = list(set(formatted_list))
    formatted_list.remove("")
    print(len(formatted_list))
    sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
    categorised_data = pd.DataFrame({"keyword": formatted_list})
    keywords_encoded = sentence_transformer.encode(categorised_data["keyword"].tolist())
    
    n_clusters = 300
    kmeans = KMeansConstrained(
        max_iter=30,
        n_clusters=n_clusters,
        size_min=100,  
        size_max=1000,  # Maximum samples per cluster
        random_state=42,
        verbose=1,  # Enable console logging
        n_init=3
    )
    kmeans.fit(keywords_encoded)

    with open(
        "/app/Back End/python_objects/ml_models/kmeans_model.pkl",
        "wb",
    ) as f:
        pickle.dump(kmeans, f)


if __name__ == "__main__":
    documents_list = [
        "/app/Back End/data/climateChange.csv",
        "/app/Back End/data/EcosystemsServices.csv",
        "/app/Back End/data/Eutrophication.csv",
        "/app/Back End/data/InvasiveSpecies.csv",
    ]
    model_trainer(documents_list)
