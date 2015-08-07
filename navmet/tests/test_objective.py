
from numpy.testing import assert_equal

import numpy as np

from navmet import path_length
from navmet import chc


def test_path_lenth():
    traj = [(x, 1) for x in range(10)]
    assert_equal(path_length(traj), 9.0)


def test_chc():
    traj1 = [(x, x) for x in range(10)]
    traj2 = [(9, x) for x in range(10, 20)]
    assert_equal(chc(traj1), np.pi/4)
    assert_equal(chc(traj2), np.pi)
    assert_equal(chc(traj1+traj2), 2*np.pi)
