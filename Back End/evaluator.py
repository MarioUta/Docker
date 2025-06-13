from utils.database_management import retrieve_papers
from utils.ml_tools.model_loader import model_loader
from utils.helpers import categories
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import json
import numpy as np


def jaccard_similarity(str1, str2):
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0


def string_matcher_search(word):
    papers = pd.DataFrame(retrieve_papers(), columns=["title", "doi", "paper"])
    papers["similarity"] = papers["title"].apply(lambda x: jaccard_similarity(word, x))
    papers = papers.sort_values("similarity", ascending=False)[:10]
    # print(papers[["title","similarity"]])
    return list(papers["title"])


def pcgs(word):
    sentence_transformer, kmeans_model = model_loader()
    keywords = sentence_transformer.encode([word])
    category = categories(kmeans_model, keywords)
    papers = pd.DataFrame(retrieve_papers(category=category))
    papers[2] = papers[2].apply(lambda x: json.loads(x))
    paper_vectors = np.array(papers[2].tolist())
    if isinstance(keywords, list):
        keywords = np.array(keywords).reshape(1, -1)
    similarities = cosine_similarity(keywords, paper_vectors).flatten()
    papers["similarity"] = similarities
    papers = papers.sort_values("similarity", ascending=False)[:10]
    # print(papers[[0,"similarity"]])
    return list(papers[0])


if __name__ == "__main__":
    word = "the alps"
    [print(result) for result in string_matcher_search(word)]
    print()
    [print(result) for result in pcgs(word)]

