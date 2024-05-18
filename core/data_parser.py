import torch
import numpy as np

def parse_data(data):
    if isinstance(data, dict):
        return {k: parse_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [parse_data(item) for item in data]
    elif isinstance(data, (torch.Tensor, np.ndarray)):
        return data.shape
    else:
        return str(data)
