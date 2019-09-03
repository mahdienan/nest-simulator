# -*- coding: utf-8 -*-
#
# test_dumping.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests for topology hl_api dumping functions.


NOTE: These tests only test whether the code runs, it does not check
      whether the results produced are correct.
"""

import unittest
import nest

import sys

import os
import os.path

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False


class PlottingTestCase(unittest.TestCase):
    def nest_tmpdir(self):
        """Returns temp dir path from environment, current dir otherwise."""
        if 'NEST_DATA_PATH' in os.environ:
            return os.environ['NEST_DATA_PATH']
        else:
            return '.'

    def test_DumpNodes(self):
        """Test dumping nodes."""
        nest.ResetKernel()
        l = nest.Create('iaf_psc_alpha',
                        positions=nest.spatial.grid(rows=3, columns=3,
                                                    extent=[2., 2.],
                                                    edge_wrap=True))
        nest.DumpLayerNodes(l, os.path.join(self.nest_tmpdir(),
                                            'test_DumpNodes.out.lyr'))
        self.assertTrue(True)

    @unittest.skipIf(not HAVE_NUMPY, 'NumPy package is not available')
    def test_DumpConns(self):
        """Test dumping connections."""
        cdict = {'connection_type': 'divergent'}
        nest.ResetKernel()
        l = nest.Create('iaf_psc_alpha',
                        positions=nest.spatial.grid(rows=1, columns=2,
                                                    extent=[2., 2.],
                                                    edge_wrap=True))
        nest.ConnectLayers(l, l, cdict)

        filename = os.path.join(self.nest_tmpdir(), 'test_DumpConns.out.cnn')
        nest.DumpLayerConnections(l, l, 'static_synapse', filename)
        npa = np.genfromtxt(filename)
        reference = np.array([[1.,  1.,  1.,  1.,  0.,  0.],
                              [1.,  2.,  1.,  1., -1.,  0.],
                              [2.,  1.,  1.,  1., -1.,  0.],
                              [2.,  2.,  1.,  1.,  0.,  0.]])
        print(np.array_equal(npa, reference))
        self.assertTrue(True)

    @unittest.skipIf(not HAVE_NUMPY, 'NumPy package is not available')
    def test_DumpConns_diff(self):
        """Test dump connections between different layers."""
        cdict = {'connection_type': 'divergent'}
        nest.ResetKernel()
        pos = nest.spatial.grid(rows=1, columns=1,
                                extent=[2., 2.],
                                edge_wrap=True)
        l1 = nest.Create('iaf_psc_alpha', positions=pos)
        l2 = nest.Create('iaf_psc_alpha', positions=pos)
        nest.ConnectLayers(l1, l2, cdict)

        print('Num. connections: ', nest.GetKernelStatus('num_connections'))

        filename = os.path.join(self.nest_tmpdir(), 'test_DumpConns.out.cnn')
        nest.DumpLayerConnections(l1, l2, 'static_synapse', filename)
        print('filename:', filename)
        npa = np.genfromtxt(filename)
        reference = np.array([1.,  2.,  1.,  1.,  0.,  0.])
        self.assertTrue(np.array_equal(npa, reference))

    @unittest.skipIf(not HAVE_NUMPY, 'NumPy package is not available')
    def test_DumpConns_syn(self):
        """Test dump connections with specific synapse."""
        cdict = {'connection_type': 'divergent'}
        nest.ResetKernel()
        pos = nest.spatial.grid(rows=1, columns=1,
                                extent=[2., 2.],
                                edge_wrap=True)
        l1 = nest.Create('iaf_psc_alpha', positions=pos)
        l2 = nest.Create('iaf_psc_alpha', positions=pos)
        l3 = nest.Create('iaf_psc_alpha', positions=pos)
        nest.ConnectLayers(l1, l2, cdict)

        syn_model = 'stdp_synapse'
        cdict.update({'synapse_model': syn_model})
        nest.ConnectLayers(l2, l3, cdict)

        print('Num. connections: ', nest.GetKernelStatus('num_connections'))

        filename = os.path.join(self.nest_tmpdir(), 'test_DumpConns.out.cnn')
        nest.DumpLayerConnections(l2, l3, syn_model, filename)
        print('filename:', filename)
        npa = np.genfromtxt(filename)
        reference = np.array([2., 3.,  1.,  1.,  0.,  0.])
        self.assertTrue(np.array_equal(npa, reference))


def suite():
    suite = unittest.makeSuite(PlottingTestCase, 'test')
    return suite


if __name__ == "__main__":

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())

    try:
        import matplotlib.pyplot as plt

        plt.show()
    except ImportError:
        pass
