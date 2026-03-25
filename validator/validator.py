import json
import os
import sys
import subprocess
import time
import urllib.request
import urllib.error

def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    print("Starting Validation...")
    
    metadata_path = 'config/metadata.json'
    if not os.path.exists(metadata_path):
        print_err(f"FAIL: Metadata file {metadata_path} not found.")
        sys.exit(1)
        
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print_err(f"FAIL: Could not parse metadata.json. {e}")
        sys.exit(1)
        
    print("--- L1: File Check ---")
    must_have_files = metadata.get('must_have_files', [])
    for file_path in must_have_files:
        if not os.path.exists(file_path):
            print_err(f"FAIL: Required file {file_path} is missing.")
            sys.exit(1)
    print("PASS: All required files exist.")
    
    print("--- L2: Content Check ---")
    expected_title = metadata.get('expected_title', '')
    index_path = 'app/index.html'
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_title not in content:
                print_err(f"FAIL: index.html does not contain expected title '{expected_title}'")
                sys.exit(1)
    except Exception as e:
        print_err(f"FAIL: Could not read {index_path}. {e}")
        sys.exit(1)
    print("PASS: Content check successful.")
    
    print("--- L3: Runtime Check ---")
    print("Building temporary Docker image for runtime check...")
    build_cmd = ["docker", "build", "-t", "app-test-validator", "-f", "docker/Dockerfile", "."]
    if subprocess.run(build_cmd).returncode != 0:
        print_err("FAIL: Docker build failed.")
        sys.exit(1)
        
    print("Running temporary container...")
    run_cmd = ["docker", "run", "-d", "-p", "8080:80", "--name", "app-validator-container", "app-test-validator"]
    result = subprocess.run(run_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_err("FAIL: Docker run failed.")
        sys.exit(1)
        
    time.sleep(3)
    
    success = False
    try:
        req = urllib.request.Request("http://localhost:8080")
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                success = True
            else:
                print_err(f"FAIL: Received status code {response.getcode()}")
    except urllib.error.URLError as e:
        print_err(f"FAIL: Unreachable. {e}")
    
    print("Cleaning up temporary container and image...")
    subprocess.run(["docker", "rm", "-f", "app-validator-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "rmi", "app-test-validator"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not success:
        print_err("FAIL: Runtime check failed.")
        sys.exit(1)
        
    print("PASS: Runtime check successful.")
    print("All validations passed!")

if __name__ == '__main__':
    main()
