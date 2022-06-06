#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 14:28:42 2022

@author: wil9fd
"""

# Python script import
import GUI

# Externally installed packages
from utm import from_latlon
from geopy import distance
from pyqtgraph import PlotWidget
from pandas import read_csv, concat, DataFrame
from numpy import inf, sqrt, arange, array2string
from lxml.etree import Element, SubElement, ElementTree
from PyQt5.QtGui import QFont, QPainterPath, QTransform
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QDoubleSpinBox, QComboBox

# Base python packages
from re import split 
from csv import Sniffer
from pathlib import Path
from os import mkdir, path



#### START ####

class Funcs():
    
    def __init__(self):       
        super(Funcs,self).__init__()
        
        
    def import_inputs(self):
        '''
        Imports inputs from GUI to respective instance variables.

        '''
        # Create blank dict for inputs
        self.inputs = {}
        # Loop through each variable from GUI Inputs
        for key in vars(self):
            # Get the variables and values from the line edits (text edits)
            if isinstance(getattr(self, key), QLineEdit):
                self.inputs.update({key: getattr(self, key).text()})
            # As above but for comboboxes
            elif isinstance(getattr(self, key), QComboBox):
                self.inputs.update({key: getattr(self, key).currentText()})
            # As above but for double spin boxes
            elif isinstance(getattr(self, key), QDoubleSpinBox):
                self.inputs.update({key: getattr(self, key).textFromValue(getattr(self, key).value())})
       
        # Print all input variables and values   
        for key, value in self.inputs.items():
            print(key, ' : ', value) 
    
    def get_settings(self):
                    # Find the settings file
            settings_file_str = r'C:\Program Files\CSIRO\CSV2RUX\application\CSV2RUX_settings.txt'

            # Try read the settings file
            try:
                with open(settings_file_str, 'r') as settings_file:
                    settings_lines = settings_file.readlines()
                    settings = []
                    for line in settings_lines:
                        # Split the string by = 
                        settings.append(line.split(' = '))
                    # Set the variables to their respective directories
                    self.pwd = settings[0][1]
                    self.fmDir = settings[1][1]
                
            except Exception:
                # If this fails show the error 
                GUI.InputDialog.fled_error(self,'D:\\')
                self.fmDir = 'D:\\'
                self.pwd = self.fmDir
                
            if Path(self.fmDir).exists() is False:
                # If the path in settings doesn't exist set it to D
                GUI.InputDialog.fled_error(self, 'C:\\')
                self.fmDir = 'C:\\'
                self.pwd = self.fmDir
        
    def get_delimiter(self):
        '''
        Saves the detected delimiter from the Pandas delimiter sniffer as an instance variable

        Raises
        ------
        Exception
            File error.

        '''
        # Select the delimiter to be input into the Pandas file reader 
        # Uses index and specially ordered list to align input and list           
        self.delimiter_list = [',',r'\s+',';'] 
        self.input_delimiter = self.delimiter_list[self.delimiter.currentIndex()]
        
        # Attempt to open the file.
        # If failed raise file error 
        try:
            # If the file exists:
            if Path(self.inputs['inputFile']).exists() is True:
                # Read it with pandas
                self.input_df = read_csv(self.inputs['inputFile'], sep = self.input_delimiter, header=None)
                # Open the csv and sniff out the delimiter
                with open(self.inputs['inputFile'], 'r') as csvfile:
                    # Save the sniffed delimiter as an instance variable
                    self.dialect = Sniffer().sniff(csvfile.readline())
        except Exception:
            # If this fails: run the file_error function in the GUI.py file
            GUI.InputDialog.file_error(self)
            raise Exception
    
    
    def fill_delimiter(self): 
        '''
        Automatically fills in the delimiter input based on the sniffed delimiter

        '''    
        # Get the index of the special ordered list based on the sniffed delimiter 
        self.delim_index = [',',' ',';'].index(str(self.dialect.delimiter))
        # Set the input dialog delimiter index to the matching value
        self.delimiter.setCurrentIndex(self.delim_index)
        # Set the input delimiter based on the self.delimiter_list defined in get_delimiter()
        self.input_delimiter = self.delimiter_list[self.delimiter.currentIndex()]
        
        
    def open_file(self): 
        '''
        Checks if file path exists:
            RAISES: File error
        '''        
        # If the file exists:
        if Path(self.inputs['inputFile']).exists() is True:
            # Read it with pandas
            self.input_df = read_csv(self.inputs['inputFile'], sep = self.input_delimiter, header=None)
            # Open the csv and sniff out the delimiter
            with open(self.inputs['inputFile'], 'r') as csvfile:
                # Save the sniffed delimiter as an instance variable
                self.dialect = Sniffer().sniff(csvfile.readline())
        else:
            # If the file doesn't exist: run the file_error function in the GUI.py file
            GUI.InputDialog.file_error(self)
            raise Exception
            # Show the error
        
        print('\n\nInput_df After Reading')
        print(self.input_df)

    
    
    def test_id(self):
        '''
        Test if the input dataframe has an id based on if the first column has 
        a true float only (float but not int) value.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        # Test if value can be float
        def isfloat(x):
            try:
                float(x)
            except (TypeError, ValueError):
                return False
            else:
                return True
        # Test if value can be int
        def isint(x):
            try:
                a = float(x)
                b = int(a)
            except (TypeError, ValueError):
                return False
            else:
                return a == b
        # Test if value can be float but not int
        # i.e. true float
        def is_true_float(num):
            if isint(num) is False and isfloat(num) is True:
                return True
            else:
                return False
        # If the first column contains a true float then the dataframe has no id
        if any([is_true_float(num) for num in split(';|\s', str(self.input_df[0]))]) is True: 
            self.has_id = False
        else:
            self.has_id = True
            
    
    def get_informat(self):
        '''
        Tests the dataframe for which input type is being used and updates the GUI 
        real time to match.

        '''
        
        if self.has_id == True:
            '''
            IF the size of the df is an id column and two pairs of lats and lons
            
            AND the values of the first lat lon columns (excluding the first values)
            match the values of the second lat lon columns (excluding the last value)
            
            THE input type is route
            
            ELSE IF they don't match it's Line
            
            ELSE IF the size is two columns and an id it's Waypoint list
            '''
            if self.input_df.shape[1] > 4 and self.input_df.iloc[0:-2,[3,4]].values.tolist() == self.input_df.iloc[1:-1,[1,2]].values.tolist():
                self.informat.setCurrentIndex(0)
            elif self.input_df.shape[1] > 4 and self.input_df.iloc[0:-2,[3,4]].values.tolist() != self.input_df.iloc[1:-1,[1,2]].values.tolist():
                self.informat.setCurrentIndex(1)
            elif self.input_df.shape[1] == 3:
                self.informat.setCurrentIndex(2)
        
        elif self.has_id == False: 
            '''
            SAME as above minus the id column
            '''
            if self.input_df.shape[1] > 3 and self.input_df.iloc[0:-2,[2,3]].values.tolist() == self.input_df.iloc[1:-1,[0,1]].values.tolist():
                self.informat.setCurrentIndex(0)
            elif self.input_df.shape[1] > 3 and self.input_df.iloc[0:-2,[2,3]].values.tolist() != self.input_df.iloc[1:-1,[0,1]].values.tolist():
                self.informat.setCurrentIndex(1)
            elif self.input_df.shape[1] < 3:
                self.informat.setCurrentIndex(2)
                
                
    def test_delimiter(self):
        '''
        Tests if the input delimiter and detected delimiter match.

        Raises
        ------
        Exception
            Delimiter error.
        '''
        # Set the input delimiter to the current GUI input
        self.inputs['delimiter'] = self.delimiter.currentText()
        # Convert the readable format [space] to true format ' '
        if self.inputs['delimiter'] == '[space]':
            self.inputs['delimiter'] = ' '
        # Flag that delimiter test has happened
        self.delimtest = True
        # If inout and detected DON'T match
        if str(self.dialect.delimiter) != self.inputs['delimiter']:
            # Call the delimiter_error function in the GUI.py file
            GUI.InputDialog.delimiter_error(self)
            # If dialog box is closed 
            if self.delim_button == QMessageBox.Close:
                # Raise to return and stop processing else continue on
                raise Exception
        
        
    def sort_lines(self):
        '''
        Sorts the dataframe based on the id if it included one initially
        '''
        
        if self.inputs['sortlines'] == 'Yes' and self.has_id == True:
            # Sort dataframe by first column
            self.input_df = self.input_df.sort_values(self.input_df.columns[0], ascending=True)
            # Reset the row indices 
            self.input_df.reset_index(drop=True, inplace=True)
            
            print('\n\n Input_df After Sorting')
            print(self.input_df)
                

    
    def fix_space_confusion(self):
        '''
        Space delimiters separate the lat and lon values from their direction flag (E,W,S,N)
        which maked the dataframe bigger than usual (a bit of a hack)
        
        This function zips the direction flag back to it's respective column
        '''
        # Copy the dataframe 
        temp_copy = self.input_df.copy()
        # Set the delimiter back to the input value for ease of understanding
        self.inputs['delimiter'] = self.delimiter.currentText()
        
        # If the delimiter is space and there is a float 
        # (lat or lon value without direction flag) this isn't a problem so pass
        if self.inputs['delimiter'] == '[space]' and any(isinstance(item, float) for item in self.input_df.iloc[:,1].values.tolist()):
            pass
        
        # If the dataframe is fatter than normal, using a space and had an id
        elif self.has_id is True and self.input_df.shape[1] >= 5 and self.inputs['delimiter'] == '[space]':
            # Get the number of columns 
            ncols = self.input_df.shape[1]
            # Make a list from 0 to number of columns
            col_list = [*range(0,ncols,1)]
            # Cut the number down by each direction flag
            new_ncols = int((ncols+1)/2)
            # Make a matrix of the new columns, every lat lon column, and every flag column
            column_matrix = zip(col_list[1:new_ncols], col_list[1::2], col_list[2::2])
            
            # For each triad in the matrix
            for i,j,k in column_matrix:
                # Populate the original dataframe's reduced columns with the value + direction flag as a string
                self.input_df.iloc[:,i] = temp_copy.iloc[:,j] +' '+ temp_copy.iloc[:,k]    
                # Drop the extra columns
                self.input_df = self.input_df.drop(self.input_df.columns[new_ncols:ncols], axis=1)
                  
        elif self.has_id is False and self.input_df.shape[1] >= 4 and self.inputs['delimiter'] == '[space]':
            # Same as above but adjusted for absence of id
            ncols = self.input_df.shape[1]
            col_list = [*range(0,ncols,1)]
            new_ncols = int(ncols/2)
            column_matrix = zip(col_list[0:new_ncols], col_list[0::2], col_list[1::2])
            
            for i,j,k in column_matrix:
                self.input_df.iloc[:,i] = temp_copy.iloc[:,j] +' '+ temp_copy.iloc[:,k]    
                self.input_df = self.input_df.drop(self.input_df.columns[new_ncols:ncols], axis=1)
                
        print('\n\n Input_df After Fixing Spaces')
        print(self.input_df)
        

        
    def convert2ddd(self):
        '''
        Takes the dd;mm;ss.s and dd;mm.m formats and convers them to dd.d

        Returns
        -------
        element : TYPE
            DESCRIPTION.

        '''
        
        def dms2ddd(element):
            # Split deg min sec string by ; and space to get values and diraction flags
            deg, minutes, seconds, direction =  split(';|\s', element)
            # converts to decimal degree
            element = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
            return element
            
        def dmm2ddd(element):
            # As above but for deg and min only 
            deg, minutes, direction =  split(';|\s', element)
            element = (float(deg) + float(minutes)/60) * (-1 if direction in ['W', 'S'] else 1)
            return element
        
        # Get the lat and lon values only excluding id to a new dataframe
        if self.has_id is False:
            self.LL_df = self.input_df.copy()
        else:
            self.LL_df = self.input_df.iloc[:,1:].copy()
        
        # Get the first value of the new dataframe 
        LL = str(self.LL_df.iloc[0,0])
        # Split it
        LL = split(';', LL)
        
        # If it's in three parts the format is deg min sec                            
        if len(LL) == 3:
            self.LLformat = 'dms'
            # Convert each value using the above function
            self.LL_df = self.LL_df.applymap(lambda x: dms2ddd(x)) 
        # If in two it's deg min
        elif len(LL) == 2:
            self.LLformat = 'dmm'
            # Same for deg min format
            self.LL_df = self.LL_df.applymap(lambda x: dmm2ddd(x))   
        # If in ddd then do nothing
        elif len(LL) == 1:
            self.LLformat = 'ddd'

        # Round values to 8 dp
        self.LL_df.round(8)
                   
        # If lon columns are before lats then switch order 
        # CAN ONLY BE DONE IN SOUTHERN HEMISPHERE
        if any(abs(val_1) > 90 for val_1 in self.LL_df.iloc[:,0].values.tolist()) or any(abs(val_2) < 0 for val_2 in self.LL_df.iloc[:,1].values.tolist()):
            self.LL_df = self.LL_df[[2,1,4,3]]
            
        # Reindex the columns by shape
        self.LL_df.columns = range(self.LL_df.shape[1])
                 
        print('\n\n LL_df After calculation')
        print(self.LL_df)
        
        # If the file didn't have an id then give it a blank one
        if self.has_id == False:
            self.input_df.insert(0, column = 'WPName', value = '')
        
        # Concatenate the new ddd lat lon values back onto the original dataframe
        self.input_df = concat([self.input_df.iloc[:,0], self.LL_df], axis=1, ignore_index=True)
        
        # If the dataframe is a big one
        if self.input_df.columns.size > 3:
            # Label the columns as such
            self.input_df.columns = ['WPName', 'Lat0', 'Lon0', 'Lat1', 'Lon1']
        else:
            self.input_df.columns = ['WPName', 'Lat', 'Lon']
            
        print('\n\n Input_df After ddd conversion')
        print(self.input_df) 
    
   
    def remove_dups(self, informat):
        '''
        Removes the duplicate point values found in route formats.

        '''
        # If dataframe is big and informat is route
        if self.input_df.shape[1] == 5 and self.informat.currentText() == informat:
            # Zip together the values of the id and first to columns with the id and last two columns 
            self.df_tuple_list = list(zip(self.input_df.iloc[:,[0,1,2]].values.tolist(), self.input_df.iloc[:,[0,3,4]].values.tolist()))
            # Convert the zipped list of tuples of lists to list of lists
            self.df_value_list = [item for i in self.df_tuple_list for item in i]
            # Convert the list of lists to the original dataframe with column names
            self.input_df = DataFrame(self.df_value_list, columns = ['WPName','Lat','Lon'])
            # drop the duplicate values keeping the first instance of them
            self.input_df.drop_duplicates(subset = ['Lat','Lon'], keep='first', inplace=True)
            # reset the row index
            self.input_df.reset_index(drop=True, inplace=True)
            
            # Some id values are integers, the above process converts them to float(ugly)
            # So try and convert to integer, if it doesn't work then no biggie just ignore
            try:
                self.input_df['WPName'] = self.input_df['WPName'].astype('int64')
            except:
                pass
            
            print('\n\n Input_df After Dup Removal')    
            print(self.input_df)
        
    
    def reverse_survey(self):
        '''
        Reverses the direction of the entire survey.
        
        If line input then swap lat lon pairs column-wise
        then flip entire dataframe topside down 
        
        If route or waypoint just flip topside down

        '''
        if self.inputs['reversesurvey'] == 'Yes':
            # If dataframe is big (line now)
            if self.input_df.shape[1] == 5:
                # Swap the lat lon column pairs
                self.input_df = self.input_df[['WPName', 'Lat1', 'Lon1', 'Lat0', 'Lon0']]
            # Flip the dataframe on it's head
            self.input_df = self.input_df[::-1]
            # Reset the index
            self.input_df.reset_index(inplace=True, drop=True)
            
            print('\n\n Input_df After Reversing')    
            print(self.input_df)

                

    def alternate_lines(self):
        '''
        Alternates the line direction (line input only),
        based on desired direction of first line.

        '''
        
        def rev_line_dirs(df, VAL_1, VAL_2):
            df_copy = df.copy()
            
            # For each even indexed line
            for line in df.iloc[::2,:].iterrows(): 
                # If the lats or lons are not in the desired order
                if line[1][VAL_1] > line[1][VAL_2]:
                    # Reverse them
                    df.iloc[line[0],[1,2]] = df_copy.iloc[line[0],[3,4]].values
                    df.iloc[line[0],[3,4]] = df_copy.iloc[line[0],[1,2]].values

            # For each odd indexed linw
            for line in df.iloc[1::2,:].iterrows():
                # If the lats or lons are not in the desired order (opposite of evens)
                if line[1][VAL_1] < line[1][VAL_2]:
                    # Reverse them
                    df.iloc[line[0],[1,2]] = df_copy.iloc[line[0],[3,4]].values
                    df.iloc[line[0],[3,4]] = df_copy.iloc[line[0],[1,2]].values
       
        def rev_list_dirs(df):
            '''
            Plan to reverse the order of waypoint or route list by 
            swapping first and second value based on desired direction
            then extrapolating through dataframe by pairs. (Might not be worth it)
            '''
            pass
            
            
        # If the input is a line 
        if self.input_df.shape[1] == 5 and self.inputs['alternatelines'] == 'Yes':
            # Choose which columns to compare and order based on the input direction
            # We want the first column lon to be smaller than second column lon
            if self.inputs['linedirection'] == 'W->E':
                VAL_1 = 2
                VAL_2 = 4
            # Reverse for east to west
            elif self.inputs['linedirection'] == 'E->W':
                VAL_1 = 4
                VAL_2 = 2
            # Same as west to east but with lats  
            elif self.inputs['linedirection'] == 'S->N':
                VAL_1 = 1
                VAL_2 = 3
            # Reverse of above
            elif self.inputs['linedirection'] == 'N->S':
                VAL_1 = 3
                VAL_2 = 1
            
            # Reverse the directions
            rev_line_dirs(self.input_df, VAL_1, VAL_2)
            # Rename the columns again 
            self.input_df.columns = ['WPName', 'Lat0', 'Lon0', 'Lat1', 'Lon1']
            
        # Just the framework for the waypoint reversal
        elif self.input_df.shape[1] == 3 and self.inputs['alternatelines'] == 'Yes':
            rev_list_dirs(self.input_df)
                
            print('\n\n Input_df After Alternating')    
            print(self.input_df)
              
    
    def reverse_line(self):
        '''
        Reverse specific line based on plotted route
        '''
        pass  
        
    def turn_radius(self): 
        
        rad_list = ["{:.4f}".format(self.turnradius.value())] * len(self.input_df)
        self.input_df.insert(self.input_df.shape[1], column = 'TurnRadius', value = rad_list)
        
    def calculate_radius(self):
        '''
        Calculates the turn radius between each point and adds it as a column to the dataframe

        '''
        def define_circle(p1, p2, p3):
            """
            Returns the center and radius of the circle passing the given 3 points.
            In case the 3 points form a line, returns (None, infinity).
            """
            temp = p2[0] * p2[0] + p2[1] * p2[1]
            bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
            cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
            det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])
        
            if abs(det) < 1.0e-6:
                return inf
        
            # Center of circle
            cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
            cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det
        
            radius = sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
            
            return radius
        
        # Get the lats and lons into a list 
        self.point_list = self.input_df.iloc[:,[1,2]].values
        # Make an empty list for the turn radii
        self.radius_list = [' '] * len(self.input_df)
        
        # The radius needs 3 points for the calculation so the start and end points are excluded
        for index in range(1,(len(self.input_df)-1)):
            # Convert the lats and lons of each point to a list of E,N
            ll_1 = list(from_latlon(self.point_list[index-1][0], self.point_list[index-1][1]))
            ll_2 = list(from_latlon(self.point_list[index][0], self.point_list[index][1]))
            ll_3 = list(from_latlon(self.point_list[index+1][0], self.point_list[index+1][1]))
            
            # Make a list of radii in nautical miles
            self.radius_list[index] = define_circle([ll_1[0],ll_1[1]],
                                               [ll_2[0],ll_2[1]],
                                               [ll_3[0],ll_3[1]])/1852
        # Add column of radii to dataframe
        self.input_df.insert(self.input_df.shape[1], column = 'TurnRadius', value = self.radius_list)
        
        print('\n\n Input_df After Radii')    
        print(self.input_df)
        
        
    def get_time(self):
        '''
        Returns the estimated time to complete the survey
        '''
        
        # Create empty list
        self.total_dist = [None] * len(self.input_df)
        self.point_list = self.input_df.iloc[:,[1,2]].values
        # For all but the last point:
        # Calculate the distance between it and the next point in nautical miles on the wgs-84 ellipsoid
        for index in range(len(self.point_list)-1):
            self.total_dist[index] = distance.distance([self.point_list[index][0], self.point_list[index][1]], 
                                                       [self.point_list[index+1][0], self.point_list[index+1][1]], 
                                                       ellipsoid='WGS-84').km/1.852
        # Sum distances
        self.sum_dist = sum(filter(None,self.total_dist))
        # Estimate time till completion based on ship speed (knots)
        self.survey_time = self.sum_dist/self.shipspeed.value()
        
        print('\n\n Total Distance (naut-miles)')    
        print(self.sum_dist)
        print('\n\n Ship Speed (knots)')    
        print(self.shipspeed.value())
        print('\n\n Total Survey Time:')    
        print(self.survey_time)
        
        # Create hr:min:sec string
        Hours = self.survey_time
        Minutes = 60 * (Hours % 1)
        Seconds = 60 * (Minutes % 1)
        
        self.time_str = str("%d:%02d:%02d" % (Hours, Minutes, Seconds))        
        
    def format_rux(self):
        # Insert new first column as id from 1 as first
        self.input_df.insert(0, column = 'Id', value = arange(self.input_df.shape[0])+1)
        
        # If there was no id
        if self.has_id == False:
            # Set the wpname as id too
            self.input_df['WPName'] = arange(self.input_df.shape[0])+1
            
        # Rename the columns 
        self.input_df.columns = ['Id', 'WPName','Lat','Lon','TurnRadius']
        
        print('\n\n Input_df After Naming')    
        print(self.input_df)
    
    
        
    def make_plot(self):
        
        symbol_list = []
        
        for value in self.input_df["Id"].tolist():
            
            mysymbol = QPainterPath()
            mysymbol.addText(0, 0, QFont("San Serif", 10), str(value))
            br = mysymbol.boundingRect()
            scale = min(1. / br.width(), 1. / br.height())
            tr = QTransform()
            tr.scale(scale, scale)
            tr.translate(-br.x() - br.width()/2., -br.y() - br.height()/2.)
            mysymbol = tr.map(mysymbol)
            
            symbol_list.append(mysymbol)
        
        # Create a plotting widget
        self.graphWidget = PlotWidget()
        # Set the size to scale with the whole grid layout (right)
        self.mainLayout.addWidget(self.graphWidget,1,5,-1,10)
        self.graphWidget.showGrid(x = True, y = True)
        self.graphWidget.setLabel('left', 'Latitude', units ='D.D°')
        self.graphWidget.setLabel('bottom', 'Longitude', units ='D.D°')
        self.graphWidget.plot(self.input_df['Lon'].tolist(), 
                              self.input_df['Lat'].tolist(), 
                              symbol = symbol_list)
        
        self.graphWidget.show()
        
        # Show the time to completion estimate
        self.completiontime.setText(self.time_str)
        self.totaldist.setText('{:.2f} Naut-Miles'.format(self.sum_dist))
        
    
    def write_rux(self):
        '''
        Creates an xml file from the input pandas dataframe and filename given.
        '''
        def df2rux(df_range, df, outname):
            
            # Create root node with required attributes       
            root = Element('KM_Route', 
                         nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance"},
                         version="1.1", 
                         RtName="SISJob")
            
            # Iterator loop in case of line output
            for points in df_range:
                
                # If the input is Route input use whole df
                if df_range == range(1):
                    new_df = df
                # Else if it's line input iterate through each pair of points 1-2, 3-4 etc.
                elif df_range == range(0, self.input_df.shape[0]-1, 2):
                    new_df = df.loc[[points,points+1]]
                
                # Create sub element of root node with waypoint count
                waypoints = SubElement(root,'Waypoints',
                                             WpCount = str(new_df.shape[0])) 
                
                # Iterate over dataframe and create waypoint nodes with attributes as df column values
                for index, row in new_df.iterrows():
                    waypoint = SubElement(waypoints, 'Waypoint',
                                                Id = str(row['Id']),
                                                WPName = str(row['WPName']),
                                                Lat = str(row['Lat']),
                                                Lon = str(row['Lon']),
                                                TurnRadius = str(row['TurnRadius']))
            # Create the xml tree from root
            tree = ElementTree(root)
            # Write it to file
            tree.write(outname, pretty_print = True, encoding='UTF-8', xml_declaration=True)
            
            
        
        # If only one rux is wanted and route is output make it
        if self.inputs['multiruxfile'] == 'No' and self.inputs['outformat'] == 'Route':
            df2rux(range(1), self.input_df, self.inputs['outputFile'])
        
        # If only one rux is wanted and line is output make it
        elif self.inputs['multiruxfile'] == 'No' and self.inputs['outformat'] == 'Line':
            df2rux(range(0, self.input_df.shape[0]-1, 2), self.input_df, self.inputs['outputFile'])
 
                
        # If multiple rux's are wanted then create a new folder and store them in there
        elif self.inputs['multiruxfile'] == 'Yes':
            # Get the file's name without root or extension
            self.file_tag = Path(self.inputs['outputFile']).stem
            # Create the name for the folder by adding the file tag to the root directory
            folder_name = Path(path.dirname(self.inputs['outputFile']) + "\\" + self.file_tag)
            
            # IF the folder doesn't already exist make it
            if folder_name.exists() is False:
                mkdir(path.dirname(self.inputs['outputFile']) + "\\" + self.file_tag)
            
            # For each consecutive pair of waypoints make a new rux file
            for index in range(self.input_df.shape[0]-1):
                new_file_name = str(folder_name) + '\\' + str(self.file_tag) + '_{:}-{:}.rux'.format(index+1,index+2)
                df2rux(range(1),self.input_df.iloc[[index,index+1],:],new_file_name)

    def write_rux_txt(self):
        with open(self.inputs['outputFile'], 'w') as rux_file:
            rux_file.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
            rux_file.write('<KM_Route xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" RtName="SISJob">\n')
            rux_file.write()
    
    
    def make_fledfile(self):
        '''
        Write fledermaus line file
        '''
        if self.inputs['fledermausfile'] == 'Yes':            
            # Get the file tag from the output name
            self.file_tag = Path(self.inputs['outputFile']).stem
            # Create the path for the fledermaus file
            fm_filename = self.fmDir +'\\'+ self.file_tag + '_fmline.txt'
            # Create it
            with open(fm_filename, 'w') as fm_file:
                # Write it
                fm_file.write('X,Y\n')
                # For the lats and lons in points_list
                for lat,lon in self.point_list: 
                    # Convert the numpy arrays to strings and format it to a string with new line indicator
                    fm_file.write(str('{:},{:}\n'.format(array2string(lat),array2string(lon))))
                fm_file.write('9999,9999')

                