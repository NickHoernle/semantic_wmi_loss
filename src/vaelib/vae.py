from __future__ import print_function
import argparse
import itertools
import torch
import torch.utils.data
from torch import nn, optim
from torch.nn import functional as F
from torchvision import datasets, transforms
from torchvision.utils import save_image
from torch.distributions import MultivariateNormal, Uniform, \
    TransformedDistribution, SigmoidTransform, Normal, Categorical

def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.normal_(m.weight,0,.05)
        m.bias.data.fill_(0)

class VAE(nn.Module):
    def __init__(self, data_dim, hidden_dim, condition=False, num_condition=0, **kwargs):
        super().__init__()

        input_dim = kwargs.get('input_dim', data_dim)
        # encoding layers
        self.encoder = nn.Sequential(
            # nn.Linear(input_dim, 500),
            # nn.LeakyReLU(.01),
            # nn.Linear(500, 250),
            # nn.LeakyReLU(.01),
            nn.Linear(input_dim, 40),
            nn.LeakyReLU(.01),
            nn.Linear(40, 40),
            nn.LeakyReLU(.01)
            )

        self.mu_enc = nn.Linear(250, hidden_dim)
        self.sig_enc = nn.Linear(250, hidden_dim)

        # decoder
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim+condition*num_condition, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 500),
            nn.LeakyReLU(.01),
            nn.Linear(500, data_dim),
        )
        self.hidden_dim = hidden_dim
        self.condition = condition
        self.num_condition = num_condition

        self.zeros = torch.zeros(hidden_dim)
        self.eye = torch.eye(hidden_dim)
        self.base = MultivariateNormal(self.zeros, self.eye)

        self.apply(init_weights)

    def encode(self, x, **kwargs):
        input = x
        # if self.condition:
        #     input = torch.cat((x, kwargs['condition_variable']), -1)
        latent_q = self.encoder(input)
        return self.mu_enc(latent_q), self.sig_enc(latent_q)

    def reparameterize(self, mu, logvar):

        sigma = torch.exp(logvar)
        # sigma = torch.ones_like(logvar)
        eps = torch.randn_like(sigma)
        z = mu + eps * sigma

        return z

    def decode(self, z, **kwargs):
        if self.condition:
            return self.decoder(torch.cat((z, kwargs['condition_variable']), -1))
        return self.decoder(z)

    def forward(self, x, **kwargs):
        q_mu, q_logvar = self.encode(x, **kwargs)

        z = self.reparameterize(q_mu, q_logvar)

        x_reconstructed = self.decode(z, **kwargs)

        return x_reconstructed, (q_mu, q_logvar)

    def reconstruct(self, z, **kwargs):
        return self.decode(z, **kwargs)

    def sample(self, num_samples):
        z = torch.randn((num_samples, self.hidden_dim))
        return self.decode(z)

    @classmethod
    def to_logits(cls, x):
        """Convert the input image `x` to logits.

        Args:
            x (torch.Tensor): Input image.
            sldj (torch.Tensor): Sum log-determinant of Jacobian.

        Returns:
            y (torch.Tensor): Dequantized logits of `x`.

        See Also:
            - Dequantization: https://arxiv.org/abs/1511.01844, Section 3.1
            - Modeling logits: https://arxiv.org/abs/1605.08803, Section 4.1
        """
        bounds = torch.tensor([0.9], dtype=torch.float32)
        y = (2 * x - 1) * bounds
        y = (y + 1) / 2
        y = y.log() - (1. - y).log()

        # Save log-determinant of Jacobian of initial transform
        ldj = F.softplus(y) + F.softplus(-y) \
              - F.softplus((1. - bounds).log() - bounds.log())
        sldj = ldj.flatten(1).sum(-1)

        return y, sldj

class VAE_Gaussian(VAE):
    def __init__(self, data_dim, hidden_dim, condition=False, num_condition=0, **kwargs):
        super().__init__(data_dim, hidden_dim, condition=condition, num_condition=num_condition, **kwargs)

        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim + condition * num_condition, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 500),
            nn.LeakyReLU(.01)
        )
        self.mu_dec = nn.Linear(500, data_dim)
        self.sig_dec = nn.Linear(500, data_dim)

    def decode(self, z, **kwargs):
        if self.condition:
            mid_var = self.decoder(torch.cat((z, kwargs['condition_variable']), -1))
        else:
            mid_var = self.decoder(z)
        return self.mu_dec(mid_var), self.sig_dec(mid_var)

class VAE_Categorical(VAE):
    def __init__(self, data_dim, hidden_dim, NUM_CATEGORIES, condition=False, num_condition=0):
        super().__init__(data_dim, hidden_dim, condition=condition, num_condition=num_condition)

        # encoding layers
        self.encoder = nn.Sequential(
            nn.Linear(data_dim + condition * num_condition, 500),
            nn.LeakyReLU(.01),
            nn.Linear(500, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01)
        )

        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim+NUM_CATEGORIES, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 250),
            nn.LeakyReLU(.01),
            nn.Linear(250, 500),
            nn.LeakyReLU(.01),
            nn.Linear(500, data_dim),
        )

        self.NUM_CATEGORIES = NUM_CATEGORIES
        self.category_prior = -torch.log(torch.tensor(self.NUM_CATEGORIES).float())
        self.apply(init_weights)
        self.means = nn.Parameter(torch.rand(NUM_CATEGORIES, hidden_dim))
        # self.means = torch.rand(NUM_CATEGORIES, hidden_dim)

        self.prior = torch.zeros(hidden_dim)
        self.post_cov = torch.eye(hidden_dim)

        self.base_dist = MultivariateNormal(self.prior, torch.eye(hidden_dim))
        self.tau = 2.
        self.reparameterize_means()

    def encode_means(self, x):
        mid_dim = self.encoder(x)
        q_mu = self.mu_enc(mid_dim)
        return q_mu, self.discriminator(q_mu)

    def decode_means(self, z):
        return self.decoder(z)

    def forward_means(self, x):
        q_mu, label_log_prob = self.encode_means(x)
        label_log_prob_sm = torch.log(torch.softmax(label_log_prob, dim=1) + 1e-10)
        return self.decode_means(q_mu), label_log_prob_sm

    def encode(self, x, **kwargs):
        input = x
        if self.condition:
            input = torch.cat((x, kwargs['condition_variable']), -1)

        mid_dim = self.encoder(input)

        return self.mu_enc(mid_dim), self.sig_enc(mid_dim)

    def get_parameters(self):
        return (itertools.chain(*[self.encoder.parameters(), self.mu_enc.parameters(), self.sig_enc.parameters()]),
                itertools.chain(*[self.decoder.parameters()]),
                itertools.chain(*[self.means]),)

    def reparameterize(self, mu, logvar):

        sigma = torch.exp(logvar)
        eps = torch.randn_like(sigma)
        z = mu + eps * sigma

        return z

    def reparameterize_means(self):
        self.samp_means = self.means + torch.randn_like(self.means)

    def discriminator(self, q_mu):
        log_prob = self.base_dist.log_prob(q_mu.unsqueeze(1).repeat(1, self.NUM_CATEGORIES, 1) -
                                           self.means.unsqueeze(0).repeat(len(q_mu), 1, 1))
        return log_prob

    def decode(self, latent_samp, **kwargs):

        if self.condition:
            return self.decoder(torch.cat((latent_samp, kwargs['condition_variable']), -1))
        return self.decoder(latent_samp)

    def forward(self, data_sample, **kwargs):

        (data, labels) = data_sample
        if type(labels) != type(None):
            return self.forward_labelled(data, labels, **kwargs)
        return self.forward_unlabelled(data, **kwargs)

    def forward_unlabelled(self, x, **kwargs):

        (q_mu, q_logvar) = self.encode(x, **kwargs)

        label_log_prob = self.discriminator(q_mu)

        # sample label
        sampled_labels = F.gumbel_softmax(label_log_prob, tau=self.tau, hard=False)
        log_pred_label_sm = torch.log(torch.softmax(label_log_prob, dim=1)+1e-10)

        means = (sampled_labels.unsqueeze(-1) * self.means.unsqueeze(0).repeat(len(q_mu), 1, 1)).sum(dim=1)

        z = self.reparameterize(q_mu, q_logvar)

        return self.decode(z, **kwargs), (z, means), (q_mu, q_logvar, log_pred_label_sm,  self.category_prior), sampled_labels

    def forward_labelled(self, x, one_hot_labels, **kwargs):

        (q_mu, q_logvar) = self.encode(x, **kwargs)

        means = (one_hot_labels.unsqueeze(-1) * self.means.unsqueeze(0).repeat(len(q_mu), 1, 1)).sum(dim=1)
        z = self.reparameterize(q_mu-means, q_logvar)

        label_log_prob = self.discriminator(q_mu)

        log_pred_label_sm = torch.log(torch.softmax(label_log_prob, dim=1)+1e-10)

        latent = torch.cat((z, one_hot_labels), dim=1)

        return self.decode(latent, **kwargs), (z, means), (q_mu, q_logvar, log_pred_label_sm), one_hot_labels

    def sample_labelled(self, labels):
        n_samps = len(labels)
        # z = (labels.unsqueeze(dim=2)*(self.means.repeat(n_samps, 1, 1)
        #             + self.base_dist.sample((n_samps,)).unsqueeze(dim=1).repeat(1,self.NUM_CATEGORIES,1))).sum(dim=1)
        z = self.base_dist.sample((n_samps,))
        latent = torch.cat((z, labels), -1)
        return self.decode(latent)


    @classmethod
    def convert_to_one_hot(cls, num_categories, labels):
        labels = torch.unsqueeze(labels, 1)
        one_hot = torch.FloatTensor(len(labels), num_categories).zero_()
        one_hot.scatter_(1, labels, 1)
        return one_hot

    @torch.no_grad()
    def update_means(self, sum_means, n, annealing):
        new_means = (sum_means/n.view(-1,1))
        self.means.copy_((1-annealing)*self.means + annealing*new_means)