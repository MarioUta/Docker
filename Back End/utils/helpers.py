import websocket
import json

from sklearn.metrics import pairwise_distances_argmin_min

def categories(kmeans_model, keyword):
    closest_cluster_index, _ = pairwise_distances_argmin_min(keyword, kmeans_model.cluster_centers_)
    return int(closest_cluster_index[0])

def send_message(message):
    try:
        ws = websocket.create_connection("ws://127.0.0.1:5000")
        ws.send(json.dumps(message))
        ws.close()
    except Exception as e:
        print("Failed to send WebSocket message:", e)