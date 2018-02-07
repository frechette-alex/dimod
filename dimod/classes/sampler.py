"""
dimod Sampler API
=================

"""

from dimod.binary_quadratic_model_convert import to_qubo, to_ising, from_qubo, from_ising
from dimod.decorators import patch_sample_kwargs
from dimod.exceptions import InvalidSampler
from dimod.vartypes import Vartype

__all__ = ['Sampler']


class Sampler(object):
    """todo

    """
    def __init__(self, default_sample_kwargs=None):
        if default_sample_kwargs is not None:
            self.default_sample_kwargs = default_sample_kwargs
        else:
            self.default_sample_kwargs = {}
        self.sample_kwargs = {}

    @patch_sample_kwargs
    def sample(self, bqm, **sample_kwargs):
        """todo"""
        try:
            if bqm.vartype is Vartype.SPIN:
                Q, offset = to_qubo(bqm)
                response = self.sample_qubo(Q, **sample_kwargs)
                response.change_vartype(Vartype.SPIN, offset, copy=False)
                return response
            elif bqm.vartype is Vartype.BINARY:
                h, J, offset = to_ising(bqm)
                response = self.sample_ising(h, J, **sample_kwargs)
                response.change_vartype(Vartype.BINARY, offset, copy=False)
                return response
            else:
                raise RuntimeError("binary quadratic model has an unknown vartype")
        except RecursionError:
            msg = ("A RecursionError has been occured. This most often happens when trying to use "
                   "the Sampler base class as a sampler.")
            raise InvalidSampler(msg)
        except RuntimeError as err:
            # in python 2 RecursionError is RuntimeError
            raise NotImplementedError

    @patch_sample_kwargs
    def sample_ising(self, h, J, **sample_kwargs):
        """todo"""
        bqm = from_ising(h, J)
        response = self.sample(bqm, **sample_kwargs)
        response.change_vartype(Vartype.SPIN, copy=False)
        return response

    @patch_sample_kwargs
    def sample_qubo(self, Q, **sample_kwargs):
        """todo"""
        bqm = from_qubo(Q)
        response = self.sample(bqm, **sample_kwargs)
        response.change_vartype(Vartype.BINARY, copy=False)
        return response