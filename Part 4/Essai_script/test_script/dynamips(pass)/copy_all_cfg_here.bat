@echo off

for /r . %%a in (*.cfg) do if exist "%%a" copy /y "%%a" .