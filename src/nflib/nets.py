"""
Various helper network modules
"""

import torch
import torch.nn.functional as F
from torch import nn

from nflib.made import MADE

def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.normal_(m.weight,0,.05)
        m.bias.data.fill_(0)

class LeafParam(nn.Module):
    """ 
    just ignores the input and outputs a parameter tensor, lol 
    todo maybe this exists in PyTorch somewhere?
    """
    def __init__(self, n):
        super().__init__()
        self.p = nn.Parameter(torch.zeros(1,n))
    
    def forward(self, x):
        return self.p.expand(x.size(0), self.p.size(1))

class PositionalEncoder(nn.Module):
    """
    Each dimension of the input gets expanded out with sins/coses
    to "carve" out the space. Useful in low-dimensional cases with
    tightly "curled up" data.
    """
    def __init__(self, freqs=(.5,1,2,4,8)):
        super().__init__()
        self.freqs = freqs
        
    def forward(self, x):
        sines = [torch.sin(x * f) for f in self.freqs]
        coses = [torch.cos(x * f) for f in self.freqs]
        out = torch.cat(sines + coses, dim=1)
        return out

class MLP(nn.Module):
    """ a simple 4-layer MLP """

    def __init__(self, nin, nout, nh, nlayers=2):
        super().__init__()
        layers = [nn.Linear(nin, nh), nn.LeakyReLU(0.2)]
        for i in range(nlayers):
            layers += [nn.Linear(nh, nh), nn.LeakyReLU(0.2)]
        layers += [nn.Linear(nh, nout)]
        self.net = nn.Sequential(*layers)
        self.apply(init_weights)

    def forward(self, x):
        return self.net(x)

    def state_dict(self, destination=None, prefix='', keep_vars=False):
        original_dict = super().state_dict(destination, prefix, keep_vars)
        return original_dict

    def load_state_dict(self, state_dict, strict=True):
        super().load_state_dict(state_dict, strict)

class PosEncMLP(nn.Module):
    """ 
    Position Encoded MLP, where the first layer performs position encoding.
    Each dimension of the input gets transformed to len(freqs)*2 dimensions
    using a fixed transformation of sin/cos of given frequencies.
    """
    def __init__(self, nin, nout, nh, freqs=(.5,1,2,4,8)):
        super().__init__()
        self.net = nn.Sequential(
            PositionalEncoder(freqs),
            MLP(nin * len(freqs) * 2, nout, nh),
        )
    def forward(self, x):
        return self.net(x)

class ARMLP(nn.Module):
    """ a 4-layer auto-regressive MLP, wrapper around MADE net """

    def __init__(self, nin, nout, nh):
        super().__init__()
        self.net = MADE(nin, [nh, nh, nh], nout, num_masks=1, natural_ordering=True)
        
    def forward(self, x):
        return self.net(x)
