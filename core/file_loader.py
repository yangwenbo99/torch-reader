
def load_file(file_path):
    if file_path.endswith('.pt'):
        import torch
        return torch.load(file_path)
    elif file_path.endswith('.npy'):
        import numpy as np
        return np.load(file_path, allow_pickle=True)
    else:
        raise ValueError("Unsupported file format")