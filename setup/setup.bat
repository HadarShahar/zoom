@echo off
pip install -r requirements.txt
echo If pyaudio installation failed, check this link https://stackoverflow.com/a/55630212

rem TODO: get admin rights and imports constants to registry
rem reg import ..\registry\reg_constants.reg

echo Setup is done!
pause