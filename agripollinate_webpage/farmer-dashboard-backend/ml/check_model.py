import torch

ckpt = torch.load('best.pt', map_location='cpu', weights_only=False)
print("Model info:", ckpt.keys())
if 'train_args' in ckpt:
    print("Training args:", ckpt['train_args'])
