import os
import torch
from torch import nn
import e3nn
from e3nn.nn.models.gate_points_2101 import Network
from e3nn import o3

class Net(nn.Module):
    def __init__(self, in_dim=14, bottleneck_dim=66, hidden_dim=128, out_dim=91, weights='autumn2025_TMQM.pt', device='cpu'):

        model_kwargs = {"irreps_in": f"{in_dim}x 0e", 
                        "irreps_hidden": [(mul, (l, p)) for l, mul in enumerate([8,3,2,1]) for p in [-1, 1]],
                        "irreps_out": "8x0e + 5x1o + 4x2e + 2x3o + 1x4e",
                        "irreps_node_attr": None, 
                        "irreps_edge_attr": o3.Irreps.spherical_harmonics(3), 
                        "layers": 4,
                        "max_radius": 3.5,
                        "number_of_basis": 10,
                        "radial_layers": 4,
                        "radial_neurons": 64,
                        "num_neighbors": 12.2298,
                        "num_nodes": 60,
                        "reduce_output": True
                       }
        
        super().__init__()
        self.atom_encoder = Network(**model_kwargs)
        self.linear1 = nn.Linear(bottleneck_dim, hidden_dim)
        self.layer_norm1 = nn.LayerNorm(hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.layer_norm2 = nn.LayerNorm(hidden_dim)
        self.linear3 = nn.Linear(hidden_dim, out_dim)
        self.k = torch.tensor([-2.4  , -2.2  , -2.   , -1.8  , -1.6  , -1.4  , -1.2  , -1.   , -0.887, -0.627,  0.627,  0.887,  1.087,  1.255,  1.403,  1.537, 1.66 ,  1.775,  1.882,  1.9  ,  2.   ,  2.1  ,  2.2  ,  2.3  , 2.4  ,  2.5  ,  2.6  ,  2.7  ,  2.8  ,  2.9  ,  3.   ,  3.1  , 3.2  ,  3.3  ,  3.4  ,  3.5  ,  3.6  ,  3.7  ,  3.8  ,  3.9  , 4.   ,  4.1  ,  4.2  ,  4.3  ,  4.4  ,  4.5  ,  4.6  ,  4.7  , 4.8  ,  4.9  ,  5.   ,  5.1  ,  5.2  ,  5.3  ,  5.4  ,  5.5  , 5.6  ,  5.7  ,  5.8  ,  5.9  ,  6.   ,  6.1  ,  6.2  ,  6.3  , 6.4  ,  6.5  ,  6.6  ,  6.7  ,  6.8  ,  6.9  ,  7.   ,  7.1  , 7.2  ,  7.3  ,  7.4  ,  7.5  ,  7.6  ,  7.7  ,  7.8  ,  7.9  , 8.   ,  8.1  ,  8.2  ,  8.3  ,  8.4  ,  8.5  ,  8.6  ,  8.7  , 8.8  ,  8.9  ,  9.   ], dtype=torch.float32, device=device)
        self.device = device
        self.load_weights()

    def forward(self, data):
        h = self.atom_encoder(data)
        h = self.layer_norm1(self.linear1(h).relu())
        h = self.layer_norm2(self.linear2(h).relu()) + h
        h = self.linear3(h)
        return h

    def load_weights(self, weights=):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        weights_path = os.path.join(current_dir, "weights", "autumn2025_TMQM.pt")
        self.load_state_dict(torch.load(weights_path, map_location=torch.device(self.device)))




