"""
ExactSolver
-----------

An exact solver that calculates the energy of all possible samples.
"""
import itertools

import numpy as np

from dimod.binary_quadratic_model_convert import to_numpy_matrix
from dimod.classes.sampler import Sampler
from dimod.compatibility23 import zip_
from dimod.decorators import bqm_index_labels
from dimod.response import Response
from dimod.vartypes import Vartype

__all__ = ['ExactSolver']


class ExactSolver(Sampler):
    """A simple exact solver, intended for testing and debugging.

    Notes:
        This solver starts to become slow for problems with 18 or more
        variables.

    """
    @bqm_index_labels
    def sample(self, bqm):
        M = to_numpy_matrix(bqm.binary)

        sample = np.zeros((len(bqm),), dtype=bool)

        response = Response(Vartype.BINARY)

        # now we iterate, flipping one bit at a time until we have
        # traversed all samples. This is a Gray code.
        # https://en.wikipedia.org/wiki/Gray_code
        def iter_samples():
            sample = np.zeros((len(bqm)), dtype=bool)
            energy = 0.0

            yield sample.copy(), energy

            for i in range(1, 1 << len(bqm)):
                v = _ffs(i)

                # flip the bit in the sample
                sample[v] = not sample[v]

                # for now just calculate the energy, but there is a more clever way by calculating
                # the energy delta for the single bit flip, don't have time, pull requests
                # appreciated!
                energy = sample.dot(M).dot(sample.transpose())

                yield sample.copy(), float(energy) + bqm.offset

        samples, energies = zip_(*iter_samples())

        response.add_samples_from(np.asarray(samples), energies)

        # finally make sure the response matches the given vartype, in-place.
        response.change_vartype(bqm.vartype)

        return response


def _ffs(x):
    """Gets the index of the least significant set bit of x."""
    return (x & -x).bit_length() - 1
