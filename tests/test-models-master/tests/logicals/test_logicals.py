from __future__ import division                                 
import numpy as np                                              
from pysd import functions                                      
from pysd import builder                                        
                                                                
class Components(builder.ComponentClass):                       
                                                                
    def and_output(self):
        """Type: Flow or Auxiliary
        """
        return self.if_true_input_and_false_input_then_1_else_0() 

    def false_input(self):
        """Type: Flow or Auxiliary
        """
        return 0 

    def not_output(self):
        """Type: Flow or Auxiliary
        """
        return self.if_not_false_input_then_1_else_0() 

    def or_output(self):
        """Type: Flow or Auxiliary
        """
        return self.if_true_input_or_false_input_then_1_else_0() 

    def true_input(self):
        """Type: Flow or Auxiliary
        """
        return 1 

    def initial_time(self):
        """Type: Flow or Auxiliary
        """
        return 0 

    def final_time(self):
        """Type: Flow or Auxiliary
        """
        return 1 

    def time_step(self):
        """Type: Flow or Auxiliary
        """
        return 1 

