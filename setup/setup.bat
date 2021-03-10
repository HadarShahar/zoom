@echo off
pip install -r requirements.txt
regedit.exe /S registry\\reg_constants.reg
echo
echo
echo
echo If pyaudio installation failed, check this link https://stackoverflow.com/a/55630212
echo Setup is done!
pause