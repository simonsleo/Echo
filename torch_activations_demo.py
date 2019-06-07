'''
Script for demonstration of the custom activation functions
implemented in the Echo package for classification of Fashion MNIST dataset.
'''

# import basic libraries
import numpy as np
import pandas as pd
from collections import OrderedDict

# import custom packages
import argparse

# import pytorch
import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
from torchvision import datasets, transforms

# import custom activations
from Echo.Activation.Torch.weightedTanh import weightedTanh
import Echo.Activation.Torch.functional as Func

# activation names constants
WEIGHTED_TANH = 'weighted_tanh'

# create class for basic fully-connected deep neural network
class Classifier(nn.Module):
    def __init__(self, activation = 'weighted_tanh'):
        super().__init__()

        # get activation the function to use
        self.activation = activation

        # initialize layers
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 10)

    def forward(self, x):
        # make sure the input tensor is flattened
        x = x.view(x.shape[0], -1)

        # apply custom activation function
        if (self.activation == WEIGHTED_TANH):
            x = Func.weighted_tanh(self.fc1(x), weight = 1)

        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.log_softmax(self.fc4(x), dim=1)

        return x

def main():
    '''
    Demonstrate custom activation functions to classify Fashion MNIST
    '''
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Argument parser')

    # Add argument to choose one of the activation functions
    parser.add_argument('--activation', action='store', default = WEIGHTED_TANH,
                        help='Activation function for demonstration.',
                        choices = [WEIGHTED_TANH])

    # Add argument to choose the way to initialize the model
    parser.add_argument('--model_initialization', action='store', default = 'class',
                        help='Model initialization mode: use custom class or use Sequential.',
                        choices = ['class', 'sequential'])

    # Parse command line arguments
    results = parser.parse_args()
    activation = results.activation
    model_initialization = results.model_initialization

    # Define a transform
    transform = transforms.Compose([transforms.ToTensor()])

    # Download and load the training data for Fashion MNIST
    trainset = datasets.FashionMNIST('~/.pytorch/F_MNIST_data/', download=True, train=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

    # Download and load the test data for Fashion MNIST
    testset = datasets.FashionMNIST('~/.pytorch/F_MNIST_data/', download=True, train=False, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=True)

    print("Create model with {activation} function.\n".format(activation = activation))

    # Initialize the model
    if (model_initialization == 'class'):
        # Initialize the model using defined Classifier class
        model = Classifier()
    else:
        # Initialize the model using nn.Sequential
        model = nn.Sequential(OrderedDict([
                              ('fc1', nn.Linear(784, 256)),
                              ('wtahn1', weightedTanh(weight = 1)), # use custom activation function
                              ('fc2', nn.Linear(256, 128)),
                              ('bn2', nn.BatchNorm1d(num_features=128)),
                              ('relu2', nn.ReLU()),
                              ('dropout', nn.Dropout(0.3)),
                              ('fc3', nn.Linear(128, 64)),
                              ('bn3', nn.BatchNorm1d(num_features=64)),
                              ('relu3', nn.ReLU()),
                              ('logits', nn.Linear(64, 10)),
                              ('logsoftmax', nn.LogSoftmax(dim=1))]))

    # Train the model
    print("Training the model on Fashion MNIST dataset.\n")

    criterion = nn.NLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)

    epochs = 5

    for e in range(epochs):
        running_loss = 0
        for images, labels in trainloader:
            images = images.view(images.shape[0], -1)
            log_ps = model(images)
            loss = criterion(log_ps, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
        else:
            print(f"Training loss: {running_loss}")

if __name__ == '__main__':
    main()