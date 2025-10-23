@echo off
xcopy snd\* dist\UpSiteDown\snd /E /I
xcopy updater.exe dist\UpSiteDown
xcopy prockill.exe dist\UpSiteDown
pause