call C:\Users\wil9fd\csv2rux_dev\venv_csv2rux\Scripts\activate.bat
pyinstaller --clean -y CSV2RUX.spec
call deactivate

del CSV2RUX.zip
powershell Compress-Archive C:\Users\wil9fd\csv2rux_python_v1.0.0\dist\CSV2RUX\* C:\Users\wil9fd\csv2rux_python_v1.0.0\CSV2RUX.zip
rmdir /s /q build
rmdir /s /q dist
git add -A 
git commit -m "Changed Lat and Lon to 8 dp" --all 
git push ghub 
git push bitbucket
cmd /k
