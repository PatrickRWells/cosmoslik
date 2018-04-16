import os, os.path as osp
from cosmoslik import *
from cosmoslik import mpi
from cosmoslik_plugins.samplers.metropolis_hastings import metropolis_hastings
from cosmoslik_plugins.likelihoods.priors import priors as _priors
from collections import OrderedDict
from numpy.random import uniform


class prior_sampler(metropolis_hastings):
    """
    Sample from the prior.
    """
    
    def __init__(self, params, 
                 output_extra_params=None,
                 num_samples=100, 
                 mpi_comm_freq=100, 
                 output_file=None):
    
        if output_extra_params is None: output_extra_params = []
        super().__init__(params,**arguments(exclude=['params']))

        self.output_extra_params = OrderedDict([k if isinstance(k,tuple) else (k,dtype('float').name) for k in output_extra_params])
        self.sampled = params.find_sampled()

        self.uniform_priors = {}
        _uniform_priors = _priors(params).uniform_priors
        for k in self.sampled:
            pr = [(n,l,u) for (n,l,u) in _uniform_priors if n==k]
            if len(pr)>2:
                raise Exception("Can't sample prior for parameters with multiple priors at once.")
            elif len(pr)==0:
                raise Exception("Prior for parameter '%s' is improper."%k)
            else:
                self.uniform_priors[k] = pr[0][1:]

        # todo: gaussian priors
        
    def draw_x(self):
        return [uniform(*self.uniform_priors[k]) for k in self.sampled]
                
    def _mcmc(self, _, lnl):
    
        for _ in range(int(self.num_samples/float(max(1,mpi.get_size()-1)))):
            cur_x = self.draw_x()
            cur_lnl, cur_extra = lnl(*cur_x)
            yield(sample(cur_x, cur_lnl, 1, cur_extra))
