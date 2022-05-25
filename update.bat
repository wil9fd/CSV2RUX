call C:\Users\wil9fd\csv2rux_dev\venv_csv2rux\Scripts\activate.bat
pyinstaller --clean -y CSV2RUX.spec
rmdir /s /q CSV2RUX.zip
powershell Compress-Archive dist\CSV2RUX\* CSV2RUX.zip ^
rmdir /s /q build
rmdir /s /q dist
git add -A 
git commit -m "Yet another update" --all 
git push ghub 
git push bitbucket
call deactivate