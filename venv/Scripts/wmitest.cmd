@echo off
for /l %%n in (27,1,38) do if exist c:\python%%n\python.exe (echo. & echo python%%n & c:\python%%n\python.exe -W ignore wmitest.py)
for /l %%n in (27,1,38) do if exist c:\python%%n-64\python.exe (echo. & echo python%%n & c:\python%%n-64\python.exe -W ignore wmitest.py)
pause
