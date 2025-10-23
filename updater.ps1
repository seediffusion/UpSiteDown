Start-Sleep -Seconds 3
if (Get-Process -Name "UpSiteDown" -ErrorAction SilentlyContinue) {
    Stop-Process -Name "UpSiteDown" -Force
} if (Get-Process -name "python" -ErrorAction SilentlyContinue) {
    Stop-Process -Name "python" -force
}
Copy-Item -Path "UpSiteDown\*" -Destination "." -Recurse -Force -Exclude "updater.exe" -ErrorAction SilentlyContinue
if (Test-Path -Path "UpSiteDown.zip") {
    Remove-Item -Path "UpSiteDown.zip"
}
if (Test-Path -Path "UpSiteDown") {
    Remove-Item -Path "UpSiteDown" -Recurse -Force
}
.\UpSiteDown.exe
exit