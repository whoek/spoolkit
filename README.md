# SPOOLKIT #


How to manage files on PC.

:: With python 2.7.11 installed
set newdir=venv

### create new virtual environment ###
cd C:\data\bitbucket
RMDIR %newdir%  /S /Q      
mkdir %newdir%
virtualenv  venv

::activate it
venv\Scripts\activate

:: get packages
pip install Flask
pip install flask-admin
pip install flask_sqlalchemy
pip install https://github.com/pyinstaller/pyinstaller/tarball/develop



### get SPOOLKIT from BITBUCKET  ###
cd c:\data\bitbucket
RMDIR spoolkit /S /Q      
git clone https://matimba@bitbucket.org/matimba/spoolkit.git
cd spoolkit


:: copy templates from flask-admin to spoolkit -- ONCE OFF!!!!
::  copy 
:: C:\data\pyvirt\flask_admin\venv\Lib\site-packages\flask_admin\templates\bootstrap3\admin
:: to
:: .....\templates\admin

### Build an EXE ###

cd C:\data\bitbucket
venv\Scripts\pyinstaller spoolkit\__spoolkit.spec

### GIT -- adding files and push to Bitbucket ###

cd C:\data\bitbucket\spoolkit

git add *.py 
git add *.html 
git add *.png 
git add *.md 
git add *.sql
git add *.css
git add *.js
git add spoolkit.spec 
git add __spoolkit.spec 
git add _spoolkit.spec 

git commit
git push


