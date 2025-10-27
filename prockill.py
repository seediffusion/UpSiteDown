import subprocess, sys
subprocess.run(["taskkill", "/f", "/im", "UpSiteDown.exe"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
subprocess.Popen("UpSiteDown.exe")
sys.exit()