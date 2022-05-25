curl -OL https://raw.githubusercontent.com/wil9fd/CSV2RUX/master/CSV2RUX.zip

powershell Expand-Archive CSV2RUX.zip

del CSV2RUX.zip

move CSV2RUX %HOMEPATH%

@echo on
set VBS=createSCUT.vbs 
set SRC_LNK="CSV2RUX"
set ARG1_APPLCT="%HOMEPATH%\CSV2RUX\CSV2RUX.exe"
set ARG2_APPARG="--profile-directory=QuteQProfile 25QuteQ"
set ARG3_WRKDRC="%HOMEPATH%\CSV2RUX"
set ARG4_ICOLCT="%HOMEPATH%\CSV2RUX\icon.ico"
cscript %VBS% %SRC_LNK% %ARG1_APPLCT% %ARG2_APPARG% %ARG3_WRKDRC% %ARG4_ICOLCT%

cmd /k