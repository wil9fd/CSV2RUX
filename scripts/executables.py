#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 14:28:42 2022

@author: wil9fd
"""

from pandas import set_option
import GUI, conversions
from sys import stdout, __stdout__
from os import devnull




class Execs():
    
    def __init__(self):       
        super(Execs,self).__init__()
        
    def csv2rux(self):
        '''
        This function acts as a parent function to the smaller functions to be called 
        for from the GUI run button
        
        '''
        print('########WRITING########\n')
        
        # Show all of dataframe 
        set_option("display.max_rows", None, "display.max_columns", None)
        
        conversions.Funcs.import_inputs(self)
        conversions.Funcs.get_delimiter(self)
        conversions.Funcs.open_file(self)
        conversions.Funcs.test_id(self)
        conversions.Funcs.test_delimiter(self) 
        try:
            conversions.Funcs.sort_lines(self)
            conversions.Funcs.fix_space_confusion(self)
            conversions.Funcs.convert2ddd(self)
            conversions.Funcs.remove_dups(self, 'QINSY Polyline (Route)')
            conversions.Funcs.reverse_survey(self)
            conversions.Funcs.alternate_lines(self)
            conversions.Funcs.remove_dups(self, 'QINSY Line')
            conversions.Funcs.turn_radius(self)
            conversions.Funcs.get_time(self)
            conversions.Funcs.format_rux(self)
            conversions.Funcs.write_rux(self)
            conversions.Funcs.make_fledfile(self)
            
        except Exception:
            GUI.InputDialog.general_error(self)
            
        print('\n########WRITTEN########\n\n')
        
    def auto_fill(self):
        def blockPrint():
            stdout = open(devnull, 'w')

        # Restore
        def enablePrint():
            stdout = __stdout__
        set_option("display.max_rows", None, "display.max_columns", None)

        '''
        Calls functions that automatically fill GUI inputs

        '''        
        # Show all of dataframe 
        set_option("display.max_rows", None, "display.max_columns", None)
        blockPrint()
        conversions.Funcs.import_inputs(self)
        conversions.Funcs.get_delimiter(self)
        conversions.Funcs.fill_delimiter(self)
        conversions.Funcs.open_file(self)
        conversions.Funcs.test_id(self)
        conversions.Funcs.get_informat(self)
        conversions.Funcs.test_delimiter(self)   
        enablePrint()
        
        
    def plot(self):
        def blockPrint():
            stdout = open(devnull, 'w')

        def enablePrint():
            stdout = __stdout__
        set_option("display.max_rows", None, "display.max_columns", None)
        
        try:
            blockPrint()
            conversions.Funcs.import_inputs(self)
            conversions.Funcs.get_delimiter(self)
            conversions.Funcs.open_file(self)
            conversions.Funcs.sort_lines(self)
            conversions.Funcs.test_id(self)
            conversions.Funcs.test_delimiter(self)
            conversions.Funcs.fix_space_confusion(self)
            conversions.Funcs.convert2ddd(self)
            conversions.Funcs.remove_dups(self, 'QINSY Polyline (Route)')
            conversions.Funcs.reverse_survey(self)
            conversions.Funcs.alternate_lines(self)
            conversions.Funcs.remove_dups(self, 'QINSY Line')
            conversions.Funcs.turn_radius(self)
            conversions.Funcs.get_time(self)
            conversions.Funcs.format_rux(self)
            enablePrint()
            conversions.Funcs.make_plot(self)
            # Turn signals back on to allow further changes if line inputs are changed
            self.sortlines.blockSignals(False)
            self.alternatelines.blockSignals(False)
            self.linedirection.blockSignals(False)
            
        except Exception:
            GUI.InputDialog.general_error(self)

        enablePrint()

