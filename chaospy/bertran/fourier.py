"""
Use recursive method for calculating Fourier coefficients.
"""
import numpy as np

from chaospy.bertran.operators import (
    add, multi_index, rank, parent, child
)


class FourierRecursive(object):
    """Calculate Fourier coefficients using Bertran's recursive formula."""

    def __init__(self, dist):
        """
        Initiate module.

        Distribution to create orthogonal basis on
        coef = E[v[n]*P[i]*P[j]]/E[P[j]**2]
        where v is basis polynomial and P are orthogonal polynomials
        """
        self.dist = dist
        self.dim = len(dist)
        self.hist = {}

    def mom_111(self, idxi, idxj, idxk):
        """Backend moment for i, j, k == 1, 1, 1."""
        if (idxi, idxj, idxk) in self.hist:
            return self.hist[idxi, idxj, idxk]

        if idxi == idxk == 0 or idxi == idxj == 0:
            out = 0

        elif add(idxi, idxk, self.dim) < idxj \
                or add(idxi, idxj, self.dim) < idxk:
            out = 0

        elif add(idxi, idxj, self.dim) == idxk:
            out = 1

        elif idxj == idxk == 0:
            out = self.dist.mom(multi_index(idxi, self.dim))

        elif idxk == 0:
            out = self.mom_110(idxi, idxj, idxk)

        else:
            out = self.mom_recurse(idxi, idxj, idxk)

        self.hist[idxi, idxj, idxk] = out

        return out

    def mom_110(self, idxi, idxj, idxk):
        """Backend moment for i, j, k == 1, 1, 1."""
        rank_ = min(
            rank(idxi, self.dim),
            rank(idxj, self.dim),
            rank(idxk, self.dim)
        )
        par, axis0 = parent(idxj, self.dim)
        gpar, _ = parent(par, self.dim, axis0)
        idxi_child = child(idxi, self.dim, axis0)
        oneup = child(0, self.dim, axis0)

        out = self(idxi_child, par, 0)
        for k in range(gpar, idxj):
            if rank(k, self.dim) >= rank_:
                out -= self.mom_111(oneup, par, k) * self.mom_111(idxi, k, 0)
        return out

    def mom_recurse(self, idxi, idxj, idxk):
        """Backend mement main loop."""
        rank_ = min(rank(idxi, self.dim), rank(idxj, self.dim), rank(idxk, self.dim))
        par, axis0 = parent(idxk, self.dim)
        gpar, _ = parent(par, self.dim, axis0)
        idxi_child = child(idxi, self.dim, axis0)
        oneup = child(0, self.dim, axis0)

        out1 = self.mom_111(idxi_child, idxj, par)
        out2 = self.mom_111(child(oneup, self.dim, axis0), par, par)
        for k in range(gpar, idxk):
            if rank(k, self.dim) >= rank_:
                out1 -= self.mom_111(oneup, k, par) \
                    * self.mom_111(idxi, idxj, k)
                out2 -= self.mom_111(oneup, par, k) \
                    * self(oneup, k, par)
        return out1 / out2

    def __call__(self, idxi, idxj, idxk):
        """
        Calculate coefficient.

        idxi : int
            Single index for basis reference
        idxj : int
            Single index for for orthogonal poly in nominator
        idxk : int
            Single index for for orthogonal poly in denominator
        """
        return self.mom_111(idxi, idxj, idxk)


if __name__ == "__main__":
    import chaospy as cp
    import doctest
    doctest.testmod()
