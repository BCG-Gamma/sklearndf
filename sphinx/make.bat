@ECHO OFF

del /q /s bar\*
set DIRFOO=foo
set DIRBAR=bar
rem for %%i in (%DIRFOO%\*) do move "%%i" bar\
rem for /d %%i in (foo\*) do move "%%i" bar\


pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help
if "%1" == "html" goto html

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:html
REM generate apidoc using docstrings
sphinx-apidoc -o %SOURCEDIR% -f ./../src/yieldengine
REM run the sphinx build for html
%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
REM clean up potentially pre-existing files in /docs
del /q /s ..\docs\*
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
