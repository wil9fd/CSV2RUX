#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 13:11:51 2022

@author: wil9fd
"""

from os import path


# Python script import
import executables, conversions

# Externally installed packages
from PyQt5.QtGui import QIcon
from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QWidget, QMessageBox, QErrorMessage, QPushButton, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QFileDialog, QGridLayout

# Base python packages
from traceback import format_exc
from pathlib import Path
from ctypes import windll

#### START ####

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)



class InputDialog(QWidget):
    def __init__(self):       
        super(InputDialog,self).__init__()
        
        # GUI labels
        in_name_lab = QLabel("Input ASCII file:")
        out_name_lab = QLabel("Output RUX File:")
        del_lab = QLabel("Delimiter: \n(Only change if coordinates are D.D°)")
        in_lab = QLabel("Input format:")
        out_lab = QLabel("Output format:")
        rev_lab = QLabel("Reverse survey direction:")
        sort_lab = QLabel("Sort lines by label?")
        alt_lab = QLabel("Reverse alternating lines?")
        dir_lab = QLabel("Specify first line direction:")
        file_lab = QLabel("Create one RUX file per line?")
        fled_lab = QLabel("Make Fledermaus linefile?")
        speed_lab = QLabel("Estimated ship speed:\n(optional)")
        radius_lab = QLabel("Input turn radius:")
        
        # GUI input types
        self.inputFile = QLineEdit(self)
        self.outputFile = QLineEdit(self)
        self.delimiter = QComboBox(self)
        self.informat = QComboBox(self)
        self.outformat = QComboBox(self)
        self.reversesurvey = QComboBox(self)
        self.sortlines = QComboBox(self)
        self.alternatelines = QComboBox(self)
        self.linedirection = QComboBox(self)
        self.fledermausfile = QComboBox(self)
        self.multiruxfile = QComboBox(self)
        self.shipspeed = QDoubleSpinBox(self)
        self.turnradius = QDoubleSpinBox(self)
        self.completiontime = QLineEdit(self)
        self.totaldist = QLineEdit(self)

        # Input file search button
        inputButton = QPushButton("...")
        inputButton.clicked.connect(self.selectInfile)
        inputButton.setToolTip('Browse input file')
        
        # Run button
        runButton = QPushButton("Save")
        runButton.clicked.connect(self.write)
        runButton.setToolTip('Save to RUX file')
        
       # Set layout as grid
        self.mainLayout = QGridLayout(self)

        # Define inputs
        self.mainLayout.addWidget(in_name_lab, 0, 0)
        self.mainLayout.addWidget(self.inputFile, 0, 1)
        self.mainLayout.addWidget(inputButton, 0, 2)
        
        self.mainLayout.addWidget(out_name_lab, 1, 0)
        self.mainLayout.addWidget(self.outputFile, 1, 1)
        
        self.mainLayout.addWidget(del_lab, 2, 0)
        self.mainLayout.addWidget(self.delimiter)
        self.delimiter.addItems([",", "[space]", ";" ])
        self.delimiter.setToolTip('Select delimiter')
        
        self.mainLayout.addWidget(in_lab, 3, 0)
        self.mainLayout.addWidget(self.informat)
        self.informat.addItems(['QINSY Polyline (Route)', 'QINSY Line','CSV waypoint list'])
        self.informat.setToolTip('''Note that lines must be labeled
with a numeric value corresponding
to the order in which they should be
run. Routes should already have waypoints
ordered correctly on export.''')
        
        self.mainLayout.addWidget(out_lab, 4, 0)
        self.mainLayout.addWidget(self.outformat)
        self.outformat.addItems(['Route', 'Line'])
        self.outformat.setToolTip('''Both will end up as routes in 
ECDIS but with slight RUX 
formatting differences.''')

        self.mainLayout.addWidget(rev_lab, 5, 0)
        self.mainLayout.addWidget(self.reversesurvey)
        self.reversesurvey.addItems(['No', 'Yes'])
        self.reversesurvey.setToolTip('''Entire survey direction will be reversed.''')
    
        
        self.mainLayout.addWidget(sort_lab, 6, 0)
        self.mainLayout.addWidget(self.sortlines)
        self.sortlines.clear()
        
        self.mainLayout.addWidget(alt_lab, 7, 0)
        self.mainLayout.addWidget(self.alternatelines)
        self.alternatelines.clear()
    
        self.mainLayout.addWidget(dir_lab, 8, 0)
        self.mainLayout.addWidget(self.linedirection)
        self.linedirection.clear()
        
        self.mainLayout.addWidget(fled_lab, 9, 0)
        self.mainLayout.addWidget(self.fledermausfile)
        self.fledermausfile.addItems(['No', 'Yes'])
        
        self.mainLayout.addWidget(file_lab, 10, 0)
        self.mainLayout.addWidget(self.multiruxfile)
        self.multiruxfile.addItems(['No', 'Yes'])
        
        self.mainLayout.addWidget(speed_lab, 11, 0)
        self.mainLayout.addWidget(self.shipspeed, 11, 1)
        self.shipspeed.setValue(8)
        
        self.mainLayout.addWidget(radius_lab, 12, 0)
        self.mainLayout.addWidget(self.turnradius, 12, 1)
        self.turnradius.setValue(0.1)
        
        self.mainLayout.addWidget(runButton, 13, 1)
        self.setWindowIcon(QIcon('.\\Icon.png'))
        
        #########################
        #PLOTTING WINDOW DISPLAY#
        self.mainLayout.addWidget(QLabel('Total Survey Distance:'), 0, 5)
        self.totaldist.setReadOnly(True)
        self.mainLayout.addWidget(self.totaldist, 0, 6)
        
        self.mainLayout.addWidget(QLabel('Est. Comp. Time (H:M:S):'), 0, 7)
        self.completiontime.setReadOnly(True)
        self.mainLayout.addWidget(self.completiontime, 0, 8)
        
        
        self.graphWidget = PlotWidget()
        self.mainLayout.addWidget(self.graphWidget,1,5,-1,10)
        # plot data: x, y values
        self.graphWidget.showGrid(x = True, y = True)
        self.graphWidget.setLabel('left', 'Latitude', units ='D.D°')
        self.graphWidget.setLabel('bottom', 'Longitude', units ='D.D°')
        self.graphWidget.plot([0], [0])
        self.graphWidget.show()
        #########################

        self.mainLayout.setRowMinimumHeight(2,40)        
        self.mainLayout.addWidget(QLabel(),3,0)        
        self.mainLayout.setRowStretch(3,1)
        self.mainLayout.setColumnMinimumWidth(1,200 )
        self.mainLayout.setSpacing(5)
        
        self.setLayout(self.mainLayout)
        
        # Call isLine function 
        self.informat.currentIndexChanged.connect(self.isLine)

        # Re-plot the route when relevant parameters or file is changed        
        self.inputFile.textChanged.connect(self.replot)
        self.delimiter.currentTextChanged.connect(self.replot)
        self.reversesurvey.currentTextChanged.connect(self.replot)
        self.sortlines.currentTextChanged.connect(self.replot)
        self.alternatelines.currentTextChanged.connect(self.replot)
        self.linedirection.currentTextChanged.connect(self.replot)
        self.shipspeed.valueChanged.connect(self.replot)

        conversions.Funcs.get_settings(self)

    def replot(self):
        # Only re-plot once for each changed parameter
        self.sortlines.blockSignals(True)
        self.alternatelines.blockSignals(True)
        self.linedirection.blockSignals(True)
        try:
            return executables.Execs.plot(self)
        except Exception: 
            return
        
    
    def isLine(self):
        # If the informat is line make the exclusive options available
        if self.informat.currentIndex() == 1:
            # Add options for line input
            self.sortlines.addItems(['No', 'Yes'])
            self.sortlines.setToolTip('''If this is a line plan this will sort the
    lines based on line number (label).''')

            self.alternatelines.addItems(['No', 'Yes'])
            self.alternatelines.setToolTip('If this is a line plan, this will reverse every other line.')

            self.linedirection.addItems(['W->E', 'E->W', 'S->N', 'N->S'])
            self.linedirection.setToolTip('Specify the desired direction of first line.')
        else:
            self.alternatelines.clear()
            self.sortlines.clear()
            self.linedirection.clear()        
        
        

    def selectInfile(self):
        '''
        Make only csv and txt files visible
        Input the path of the in file
        Create the output file name based on the input
        Calls the autofill function based on the input file
        If autofill fails just stop filling

        '''
        inputFile = QFileDialog.getOpenFileName(self, 'OpenFile',self.pwd,'ASCII Files (*.csv *.txt)')
        inputPath = Path(inputFile[0])
        self.input_root = str(inputPath.root)
        print(self.input_root)
        self.inputFile.setText(str(inputPath))
        outputFile = Path(path.dirname(str(inputPath)) + '\\' + inputPath.stem + '.rux')
        self.outputFile.setText(str(outputFile))
        try:
            return executables.Execs.auto_fill(self), executables.Execs.plot(self)
        except Exception: 
            return
        
       

    
    def delimiter_error(self):    
        self.warning_dialog = QMessageBox()
        self.warning_dialog.setIcon(QMessageBox.Warning)
        self.warning_dialog.setText("The detected or input delimiter may be incorrect:")
        self.warning_dialog.setWindowTitle("Delimiter Warning")
        self.warning_dialog.setDetailedText("The detected isn't always correct, usually with spaces and DDMM format. \nIt is recommended to double check the input delimiter.")
        self.warning_dialog.addButton(QPushButton('Continue'), QMessageBox.YesRole)
        self.warning_dialog.addButton(QMessageBox.Close)
        self.delim_button = self.warning_dialog.exec()
        
    def fled_error(self, drive):    
        self.warning_dialog = QMessageBox()
        self.warning_dialog.setIcon(QMessageBox.Warning)
        self.warning_dialog.setText("The CSV2RUX settings cannot be found or are incorrect. The Fledermaus file will be written to {:} directory.".format(drive))
        self.warning_dialog.setWindowTitle("Fledermaus File Warning")
        self.warning_dialog.addButton(QPushButton('Continue'), QMessageBox.YesRole)
        self.warning_dialog.addButton(QMessageBox.Close)
        self.delim_button = self.warning_dialog.exec()
    
        
    def file_error(self):
        self.ferror_dialog = QErrorMessage()
        self.ferror_dialog.setWindowTitle("Error")
        self.ferror_dialog.showMessage('ERROR: Filename cannot be found')
        
    def general_error(self):
        self.gerror_dialog = QMessageBox()
        self.gerror_dialog.setIcon(QMessageBox.Critical)
        self.gerror_dialog.setWindowTitle("Error")
        self.gerror_dialog.setText('ERROR: Please double check the delimiter and input format')
        self.gerror_dialog.setDetailedText(format_exc())
        self.gerror_dialog.exec()
        
    def write(self):
        try:
            return executables.Execs.csv2rux(self)
        except Exception: 
            return       