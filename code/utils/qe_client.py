import json

import requests

url = "http://127.0.0.1:8000/api/scores"

# data example:

# data = [
#     {
#         "src": "How to Demonstrate Your Strategic Thinking Skills",
#         "mt": "Cómo demostrar su capacidad de pensamiento estratégico",
#     },
#     {
#         "src": "Why is Accuracy important in the workplace?",
#         "mt": "¿Por qué es importante la precisión en el trabajo",
#     },
#     {
#         "src": "When faced with a large amount of analysis ask for support setting up a team to approach the issue in different ways.",
#         "mt": "Cuando se enfrente a una gran cantidad de análisis, pida ayuda para crear un equipo que aborde la cuestión de diferentes maneras.",
#     },
# ]


def prepare_data(bitexts):
    return [{"src": k, "mt": v} for k, v in bitexts.items()]


def add_scores(bitexts):
    data = prepare_data(bitexts)

    payload = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, data=payload)

    if response.status_code == 200:
        return json.loads(response.text)
