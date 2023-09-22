# Description: Distance to closest record metric
# Author: Anton D. Lautrup
# Date: 23-08-2023

import numpy as np

from ..core.metric import MetricClass

from ...utils.nn_distance import _knn_distance

class MedianDistanceToClosestRecord(MetricClass):
    """The Metric Class is an abstract class that interfaces with 
    SynthEval. When initialised the class has the following attributes:

    Attributes:
    self.real_data : DataFrame
    self.synt_data : DataFrame
    self.hout_data : DataFrame
    self.cat_cols  : list of strings
    self.num_cols  : list of strings

    self.nn_dist   : string keyword
    self.analysis_target: variable name
    """

    def name() -> str:
        """ Name/keyword to reference the metric"""
        return 'dcr'

    def type() -> str:
        """ Set to 'privacy' or 'utility' """
        return 'privacy'

    def evaluate(self) -> float | dict:
        """Distance to closest record, using the same NN stuff as NNAA"""
        
        distances = _knn_distance(self.synt_data,self.real_data,self.cat_cols,1,self.nn_dist)
        in_dists = _knn_distance(self.real_data,self.real_data,self.cat_cols,1,self.nn_dist)

        int_nn = np.median(in_dists)
        mut_nn = np.median(distances)

        dcr = mut_nn/int_nn
        self.results = {'mDCR': dcr}
        return self.results

    def format_output(self) -> str:
        """ Return string for formatting the output, when the
        metric is part of SynthEval. 
|                                          :                    |"""
        string = """\
| Median distance to closest record        :   %.4f           |""" % (self.results['mDCR'])
        return string

    def normalize_output(self) -> dict:
        """ To add this metric to utility or privacy scores map the main 
        result(s) to the zero one interval where zero is worst performance 
        and one is best.
        
        pass or return None if the metric should not be used in such scores.

        Return dictionary of lists 'val' and 'err' """
        return {'val': [np.tanh(self.results['mDCR'])], 'err': [0]}
