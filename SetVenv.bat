echo.

IF "%~1"=="" GOTO LabelMissingParameter
IF NOT "%~2"=="" GOTO LabelTooManyParameters

echo %1
R:
cd \PythonPlayground
"C:\Program Files (x86)\Python36-32\python" -m venv %1
call %1\scripts\activate
python --version

rem ** The following commands will fail in Windows since can not update a currently running exe.
rem ** See https://github.com/pypa/pip/issues/2863

python -m pip install --upgrade pip

call pip3_list.bat

goto LabelEnd

:LabelMissingParameter
echo Missing Parameter
goto LabelEnd

:LabelTooManyParameters
echo Too Many Parameters
goto LabelEnd

:LabelEnd
echo.
