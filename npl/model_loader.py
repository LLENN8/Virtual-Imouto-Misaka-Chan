import numpy as np
import json
import os
import torch
import torch.nn as nn
from torch.utils.data import *
from npl.model import *
from npl.npl_nltk import *

def load_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # open data.pth and Load model
    with open(os.path.join(os.path.dirname(__file__),'intents.json'), 'r') as json_data:
        intents = json.load(json_data)

    FILE = "data.pth"
    data = torch.load(FILE)

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = LSTMNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    return intents, all_words, tags, model

