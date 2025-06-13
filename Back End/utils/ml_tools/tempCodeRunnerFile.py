import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
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
    tfidf = TfidfVectorizer()
    categorised_data = pd.DataFrame({"keyword": formatted_list})
    keywords_encoded = tfidf.fit_transform(categorised_data["keyword"])
    svd = TruncatedSVD(n_components=100, random_state=42)
    svd_reduced = svd.fit_transform(keywords_encoded)
    
    n_clusters = 100
    kmeans = KMeansConstrained(
        n_clusters=n_clusters,  
        size_max=7000,  # Maximum samples per cluster
        random_state=42,
    )
    kmeans.fit(svd_reduced)

    with open(
        "/app/Back End/python_objects/ml_models/kmeans_model.pkl",
        "wb",
    ) as f:
        pickle.dump(kmeans, f)
    with open(
        "/app/Back End/python_objects/ml_models/tfidf_model.pkl",
        "wb",
    ) as f:
        pickle.dump(tfidf, f)
    with open(
        "/app/Back End/python_objects/ml_models/svd_model.pkl",
        "wb",
    ) as f:
        pickle.dump(svd, f)


if __name__ == "__main__":
    documents_list = [
        "/app/Back End/data/climateChange.csv",
        "/app/Back End/data/EcosystemsServices.csv",
        "/app/Back End/data/Eutrophication.csv",
        "/app/Back End/data/InvasiveSpecies.csv",
    ]
    model_trainer(documents_list)
