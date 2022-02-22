import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class FNNModel(nn.Module):
    def __init__(self, args):
        super(FNNModel, self).__init__()
        self.n_token = args.n_token
        self.h_dim = args.h_dim
        self.n_gram = args.n_gram
        self.share_embedding = args.share_embedding
        self.share_embedding_strict = args.share_embedding_strict

        self.encoder = nn.Embedding(self.n_token, self.h_dim)
        self.fc1 = nn.Linear(self.h_dim * self.n_gram, self.h_dim)

        if not self.share_embedding:
            self.decoder = nn.Linear(self.h_dim, self.n_token)
        elif self.share_embedding_strict:
            # Strictly tied, no bias as embedding
            self.decoder = nn.Linear(self.h_dim, self.n_token, bias=False)
            self.decoder.weight = self.encoder.weight
        else:
            self.decoder = nn.Linear(self.h_dim, self.n_token)
            self.decoder.weight = self.encoder.weight

        self.drop = nn.Dropout(p=args.dropout)
        self.init_weights()

    # Init parameters
    def init_weights(self):
        std_var = 1.0 / math.sqrt(self.h_dim)
        nn.init.uniform_(self.encoder.weight, -std_var, std_var)
        nn.init.uniform_(self.fc1.weight, -std_var, std_var)
        nn.init.zeros_(self.fc1.bias)

        if not self.tie_weights:
            nn.init.uniform_(self.decoder.weight, -std_var, std_var)
            nn.init.zeros_(self.decoder.bias)
        elif not self.tie_no_bias:
            nn.init.zeros_(self.decoder.bias)

    def forward(self, x):
        output = self.drop(self.encoder(x))
        output = self.fc1(output.view(-1, self.h_dim * self.n_gram))
        output = self.decoder(output)
        return output
