SET PYTHON_EXE=C:\ProgramData\BHoM\Extensions\PythonEnvironments\Python_Toolkit\v3_10\python.exe
SET TEST_DIR=C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\tests

@REM C:\ProgramData\BHoM\Extensions\PythonEnvironments\Python_Toolkit\v3_10\python.exe -m pytest --cov-report term --cov-report html:cov_html --cov python_toolkit -v C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\tests

"%PYTHON_EXE%" -m pytest --cov-report term --cov-report html:cov_html --cov python_toolkit -v "%TEST_DIR%"
cmd /k