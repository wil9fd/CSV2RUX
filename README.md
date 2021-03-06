# CSV2RUX

## Install
* First download and extract the zip file. 
* Copy the extracted file to a safe place i.e. C:/Users/Name 
* Create a shortcut of the CSV2RUX.exe file and copy it to the desktop

## Uninstall 
* Delete the CSV2RUX folder, zipped folder and shortcut

## Update
* Updates are done by uninstalling and reinstalling

## Intro
CSV2RUX is an application developed in python that converts csv route, line and waypoint lists exported via QINSy to a RUX html format which can be read onto the bridge EDCIS system.

## Functionality 
CSV2RUX uses delimiter and input format interpreters among other functions to automatically read in an input file, and plot it. 

## Notes
The order of lat and lon columnwise is unimportant ONLY IN THE SOUTHERN HEMISHPERE. Else columns should be ordered lat,lon. 


### DEV

## The program file
The program file is created by PyInstaller and the included spec file. A venv with the required packages (pandas, geopy, lxml, numpy, PyQt5, pyinstaller, pyqtgraph, utm) should be created to reduce the application's file size. This venv path should be included in the `pathex` variable in the .spec file. After the scripts have been changed, a new application folder must be made, zipped and pushed along with the code changes. 

There is an `update.bat` to streamline the process of updating. The paths must be modified by the developer to be used. 

## General XML info
Rux files are an XML format (extensible markup language). The element names (KM_Route, WayPoints, WayPoint) are all case sensitive (don't ask me how I know it's too painful). The indentation of an XML is purely aesthetic, the formatting of an XML is far more important i.e. ```<element>value</element>``` or ```<element attribute="value"/>```. Further specific information about RUX formatting can be found at: https://stm-stmvalidation.s3.eu-west-1.amazonaws.com/uploads/20190322122013/ECDIS-Annex-S-version-1.1-STM-Extended_29032017_Final_Proposal.pdf

### Contact
For more information contact samson.williams@csiro.au