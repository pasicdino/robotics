import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import main


class Controller(nn.Module):
    def __init__(self):
        super(Controller, self).__init__()
        self.fc1 = nn.Linear(12, 24)  # 12 input sensors, 24 hidden units
        self.fc2 = nn.Linear(24, 2)  # 24 hidden units to 2 output motors

        # Initialize placeholders for weights and biases
        self.custom_fc1_weight = None
        self.custom_fc1_bias = None
        self.custom_fc2_weight = None
        self.custom_fc2_bias = None

    def forward(self, x):
        # Convert input to tensor if it's not already a tensor
        if not isinstance(x, torch.Tensor):
            x = torch.tensor(x, dtype=torch.float32)

        # Use custom weights and biases if they are set
        if self.custom_fc1_weight is not None and self.custom_fc1_bias is not None:
            x = torch.relu(torch.nn.functional.linear(x, self.custom_fc1_weight, self.custom_fc1_bias))
        else:
            x = torch.relu(self.fc1(x))

        if self.custom_fc2_weight is not None and self.custom_fc2_bias is not None:
            x = torch.nn.functional.linear(x, self.custom_fc2_weight, self.custom_fc2_bias)
        else:
            x = self.fc2(x)
        return x

    def set_weights(self, weights):
        # Convert list to numpy array for reshaping
        weights = np.array(weights)

        # Extract weights and biases
        w1 = weights[0:336].reshape(24, 14)  # Changed shape to 24x14 for fc1
        b1 = weights[336:360]  # 24 biases for fc1
        w2 = weights[360:408].reshape(2, 24)  # 2x24 weights for fc2
        b2 = weights[408:410]  # 2 biases for fc2

        # Set custom weights and biases
        self.custom_fc1_weight = torch.tensor(w1, dtype=torch.float32)
        self.custom_fc1_bias = torch.tensor(b1, dtype=torch.float32)
        self.custom_fc2_weight = torch.tensor(w2, dtype=torch.float32)
        self.custom_fc2_bias = torch.tensor(b2, dtype=torch.float32)

    def simulate(self, weights):
        self.set_weights(weights)
        return main.runset(self)
