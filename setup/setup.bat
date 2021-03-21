@echo off

:: request admin access - https://stackoverflow.com/a/40388766
if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit /b)
:: keep the working directory
cd /D %~dp0

pip install -r requirements.txt
echo If pyaudio installation failed, check this link https://stackoverflow.com/a/55630212
reg import ..\registry\reg_constants.reg

echo Setup is done!
pause