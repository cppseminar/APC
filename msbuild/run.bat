:: USAGE:
::  run.bat OUT_DIR_PATH SOURCE_FILES
::   SOURCE_FILES - files separated by ';', if multiple, need to be quoted
:: EXAMPLES:
::  run.bat c:\usr\123\out c:\usr\123\src\1.cpp
::  run.bat c:\usr\123\out "c:\usr\123\src\1.cpp;c:\usr\123\src\2.cpp"

setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat"

msbuild "%~dp0run.targets" /bl /m /p:BinaryTargetDir=%1 /p:SourceFiles=%2

copy "%~dp0msbuild.binlog" %1

endlocal