#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:36:29 2022

@author: wil9fd
"""
# Python script import
import GUI

# Externally installed packages
from PyQt5.QtWidgets import QApplication

# Base python packages


#### START ####
if __name__=="__main__":
    import sys
    app    = QApplication(sys.argv)
    myshow = GUI.InputDialog()
    myshow.setWindowTitle("CSV2RUX")
    myshow.show()
    sys.exit(app.exec_())