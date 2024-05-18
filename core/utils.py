from typing import Union
import torch
import numpy

PRECISION_INT = 4
PRECISION_DEC = 4
MAX_LENGTH = 20

def pretty_print(data: Union[torch.Tensor, numpy.ndarray, str]) -> str:
    if isinstance(data, str):
        return data

    if isinstance(data, torch.Tensor):
        data = data.detach().cpu().numpy()
        if data.ndim == 0:
            return str(data.item())
        elif data.ndim == 1:
            return _pretty_print_row(data)
        elif data.ndim == 2:
            return _pretty_print_matrix(data)
        else:
            return f'Array of shape {data.shape}'


def _pretty_print_row(row: numpy.ndarray) -> str:
    processed_row = []
    length = len(row)
    for i in range(min(length, MAX_LENGTH) - 1):
        val = row[i]
        processed_row.append(f'{val: {PRECISION_INT}.{PRECISION_DEC}f}')
    if length > MAX_LENGTH:
        processed_row.append('...')
    if length > 0:
        processed_row.append(f'{row[-1]: {PRECISION_INT}.{PRECISION_DEC}f}')
    return ' '.join(processed_row)

def _pretty_print_matrix(matrix: numpy.ndarray) -> str:
    processed_matrix = []
    length = len(matrix)
    for i in range(min(length, MAX_LENGTH) - 1):
        val = matrix[i]
        processed_matrix.append(_pretty_print_row(val))
    if length > MAX_LENGTH:
        processed_matrix.append('...')
    if length > 0:
        processed_matrix.append(_pretty_print_row(matrix[-1]))
    return '\n'.join(processed_matrix)
