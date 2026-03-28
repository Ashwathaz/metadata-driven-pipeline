import os
import sys
import json
import subprocess
import time
import urllib.request
from urllib.error import URLError, HTTPError
import uuid

def print_log(msg):
    print(f"[VALIDATOR] {msg}")

def check_files(metadata):
    print_log("Starting L1 Validation: File Check")
    must_have_files = metadata.get('must_have_files', [])
    for file_path in must_have_files:
        if not os.path.exists(file_path):
            print_log(f"FAILED: Missing required file: {file_path}")
            sys.exit(1)
        print_log(f"Found required file: {file_path}")
    print_log("L1 Validation passed successfully.\\n")

def check_content(metadata):
    print_log("Starting L2 Validation: Content Check")
    expected_title = metadata.get('expected_title', '')
    index_path = 'app/index.html'
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if f"<title>{expected_title}</title>" not in content and f"<title>{expected_title}</title>".lower() not in content.lower():
        # Fallback check title tag using simple string extraction to ignore formatting
        import re
        match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if match and match.group(1).strip() == expected_title:
             pass
        else:
             print_log(f"FAILED: 'app/index.html' must contain expected_title '{expected_title}'")
             sys.exit(1)
        
    print_log("L2 Validation passed successfully.\\n")

def check_runtime():
    print_log("Starting L3 Validation: Runtime Check")
    temp_image_name = f"temp_app_image_{uuid.uuid4().hex[:8]}"
    temp_container_name = f"temp_app_container_{uuid.uuid4().hex[:8]}"
    port = "8099" 

    try:
        print_log("Building temporary Docker image...")
        build_cmd = ["docker", "build", "-t", temp_image_name, "-f", "docker/Dockerfile", "."]
        subprocess.run(build_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print_log("Running temporary container...")
        run_cmd = ["docker", "run", "-d", "-p", f"{port}:80", "--name", temp_container_name, temp_image_name]
        subprocess.run(run_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Give container time to start serving
        time.sleep(3)
        
        url = f"http://localhost:{port}"
        print_log(f"Verifying app is reachable at {url}...")
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print_log("App is reachable. Output verified.")
            else:
                print_log(f"FAILED: Received HTTP status code {response.status}")
                sys.exit(1)
                
    except subprocess.CalledProcessError as e:
        print_log(f"FAILED: Docker command failed - {e}")
        sys.exit(1)
    except (URLError, HTTPError) as e:
        print_log(f"FAILED: Application not reachable - {e}")
        sys.exit(1)
    finally:
        print_log("Cleaning up temporary Docker resources...")
        subprocess.run(["docker", "rm", "-f", temp_container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "rmi", temp_image_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print_log("L3 Validation passed successfully.\\n")

if __name__ == "__main__":
    if not os.path.exists('config/metadata.json'):
        print_log("FAILED: config/metadata.json not found")
        sys.exit(1)
        
    with open('config/metadata.json', 'r') as f:
        try:
            metadata = json.load(f)
        except json.JSONDecodeError:
            print_log("FAILED: Invalid JSON in config/metadata.json")
            sys.exit(1)
            
    check_files(metadata)
    check_content(metadata)
    check_runtime()
    
    print_log("ALL VALIDATIONS PASSED. APP IS READY FOR DEPLOYMENT.")
