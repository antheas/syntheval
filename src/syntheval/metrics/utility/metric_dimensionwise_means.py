# Description: Dimensionwise means difference
# Author: Anton D. Lautrup
# Date: 23-08-2023

import numpy as np
import pandas as pd

from ..core.metric import MetricClass

from scipy.stats import sem
from sklearn.preprocessing import MinMaxScaler

from ...utils.plot_metrics import plot_dimensionwise_means

class MetricClassName(MetricClass):
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
        return 'dwm'

    def type() -> str:
        """ Set to 'privacy' or 'utility' """
        return 'utility'

    def evaluate(self) -> float | dict:
        """Function for calculating DWM, plotting an appropriate diagram"""
        try:
            scaler = MinMaxScaler().fit(pd.concat((self.real_data[self.num_cols],self.synt_data[self.num_cols]),axis=0))
            r_scaled = scaler.transform(self.real_data[self.num_cols])
            f_scaled = scaler.transform(self.synt_data[self.num_cols])

            dim_means = np.array([np.mean(r_scaled,axis=0),np.mean(f_scaled,axis=0)]).T
            means_diff = dim_means[:,0]-dim_means[:,1]
            
            mean_errors = np.array([sem(r_scaled),sem(f_scaled)]).T
            diff_error = np.sqrt(np.sum(mean_errors**2,axis=1))

            if self.verbose: plot_dimensionwise_means(dim_means, mean_errors, self.num_cols)
            self.results = {'avg': np.mean(abs(means_diff)), 'err': np.sqrt(sum(diff_error**2))/len(diff_error)}
            return self.results
        except ValueError:
            print("No nummerical columns provided for DWM.")
            return {}

    def format_output(self) -> str:
        """ Return string for formatting the output, when the
        metric is part of SynthEval. 
|                                          :                    |"""
        string = ""
        if self.results != {}:
            string = """\
| Average dimensionwise means diff. (nums) :   %.4f  %.4f   |""" % (self.results['avg'], self.results['err'])
        return string

    def normalize_output(self) -> list:
        """ This function is for making a dictionary of the most quintessential
        nummerical results of running this metric (to be turned into a dataframe).

        The required format is:
        metric  dim  val  err  n_val  n_err
            name1  u  0.0  0.0    0.0    0.0
            name2  p  0.0  0.0    0.0    0.0
        """
        if self.results != {}:
            val_non_lin     = np.exp(-25*self.results['avg'])
            val_non_lin_err = 25*val_non_lin*self.results['err']
            return [{'metric': 'avg_dwm_diff', 'dim': 'u', 
                     'val': self.results['avg'], 
                     'err': self.results['err'], 
                     'n_val': 1-self.results['avg'], 
                     'n_err': self.results['err'], 
                    #  'idx_val': val_non_lin, 
                    #  'idx_err': val_non_lin_err
                     }]
        else: pass

