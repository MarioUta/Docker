import pickle
from sentence_transformers import SentenceTransformer

def model_loader():

    sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')

    with open(
        "/app/Back End/python_objects/ml_models/kmeans_model.pkl",
        "rb",
    ) as file:
        kmeans_model = pickle.load(file)

    return sentence_transformer, kmeans_model
