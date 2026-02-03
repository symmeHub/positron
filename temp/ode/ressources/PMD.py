################################################################################
# POINT MASS DYNAMICS
# Author: Ludovic Charleux, ludovic.charleux@univ-smb.fr, 01/2018
################################################################################
import numpy as np
from scipy import integrate, optimize
from scipy.integrate import odeint


def distances(P):
    """
    Return vectorials distance, scalar distance and normalized directions.
    """
    X, Y = P.T
    dX = X - X[:, np.newaxis]
    dY = Y - Y[:, np.newaxis]
    D = np.array([dX, dY]).swapaxes(0, 2)
    R = np.sqrt(D[:, :, 0] ** 2 + D[:, :, 1] ** 2)
    U = np.divide(
        D, R[:, :, np.newaxis], out=np.zeros_like(D), where=R[:, :, np.newaxis] != 0.0
    )
    return D, R, U


class PMD:
    """
    Point Mass Dynamics
    """

    def __init__(self, m, P, V, nk=10000):
        n = len(P)
        self._n = n
        self.X = np.zeros([nk, 4 * n])
        self.X.fill(np.nan)
        self.X[-1, : 2 * n] = np.array(P).flatten()
        self.X[-1, 2 * n :] = np.array(V).flatten()
        self.m = np.array(m)
        self.nk = nk

    def solve(self, dt, nt):
        time = np.linspace(0.0, dt, nt + 1)
        Xs = odeint(self.derivative, self.X[-1], time)
        nk = self.nk
        X = self.X
        X[: nk - nt] = X[nt:]
        X[-nt - 1 :] = Xs
        self.X = X

    def get_positions(self):
        """
        Returns the current positions.
        """
        n = len(self.m)
        return self.X[-1, : 2 * n].reshape(n, 2)

    def set_positions(self, P):
        """
        Sets the current positions.
        """
        n = len(self.m)
        self.X[-1, : 2 * n] = P.flatten()

    positions = property(get_positions, set_positions)

    def get_velocities(self):
        """
        Returns the current velocities.
        """
        n = len(self.m)
        return self.X[-1, 2 * n :].reshape(n, 2)

    velocities = property(get_velocities)

    def xy(self):
        n = self._n
        p = self.X[-1, : 2 * n].reshape(n, 2)
        return p[:, 0], p[:, 1]

    def trail(self, i):
        n = self._n
        X = self.X
        return X[:, 2 * i], X[:, 2 * i + 1]


class MetaForce:
    """
    A force metaclass to rule them all
    """

    def set_master(self, master):
        """
        Sets the PMD instance to work with
        """
        self.master = master

    def master_force(self):
        return self.force(P=self.master.positions, V=self.master.velocities)

    def master_potential(self):
        return self.potential(P=self.master.positions)
