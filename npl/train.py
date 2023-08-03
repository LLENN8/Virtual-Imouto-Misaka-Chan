import numpy as np
import json
import os
import torch
import torch.nn as nn
from torch.utils.data import *
from model import *
from npl_nltk import *
import torch.optim as optim


# Load intents data from JSON file
with open(os.path.join(os.path.dirname(__file__), 'intents.json'), 'r') as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []

# Loop through each sentence in intents patterns
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)  # Add to tag list
    for pattern in intent['patterns']:
        # Tokenize each word in the sentence
        w = tokenize(pattern)
        all_words.extend(w)  # Add to words list
        xy.append((w, tag))  # Add to xy pair

# Stem and lower each word
ignore_words = ['?', '.', '!', ',']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))  # Remove duplicates and sort
tags = sorted(set(tags))

#print for checked tags, all_words
print(len(xy), "patterns")
print(len(tags), "tags:", tags)
print(len(all_words), "unique stemmed words:", all_words)

X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    # X: bag of words for each pattern_sentence
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    # y: PyTorch CrossEntropyLoss 
    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Hyperparameters
num_epochs = 1000
batch_size = 8
learning_rate = 0.001
input_size = len(X_train[0])
hidden_size = 16
output_size = len(tags)
print(input_size, output_size)

class ChatDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.n_samples = len(X_data)
        self.x_data = torch.from_numpy(X_data).float()
        self.y_data = torch.from_numpy(y_data).long()
        
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]
    
    def __len__(self):
        return self.n_samples

dataset = ChatDataset(X_train, y_train)
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = LSTMNet(input_size, hidden_size, output_size, dropout_prob=0.2, weight_decay=1e-5).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Train the model
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.unsqueeze(1).to(device)  # Reshape input to (batch_size, sequence_length, input_size)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(words)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
    if (epoch+1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

print(f'Final loss: {loss.item():.4f}')

print("Training finished!")

#saving model into data.pth
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)

print(f'Training complete. File saved to {FILE}')

