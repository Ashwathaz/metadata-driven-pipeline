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
    if not os.path.exists("docker/Dockerfile"):
        print_err("FAIL: Required file docker/Dockerfile is missing.")
        sys.exit(1)
        
    if not os.path.exists("app/") or not os.path.isdir("app/"):
        print_err("FAIL: app/ directory is missing.")
        sys.exit(1)
        
    if len(os.listdir("app/")) == 0:
        print_err("FAIL: app/ directory is empty.")
        sys.exit(1)
        
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
    run_cmd = ["docker", "run", "-d", "--rm", "-p", "8080:80", "--name", "app-validator-container", "app-test-validator"]
    print(f"Executing: {' '.join(run_cmd)}")
    result = subprocess.run(run_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_err(f"FAIL: Docker run failed. Exit code: {result.returncode}")
        print_err(f"Logs: {result.stderr}")
        sys.exit(1)
        
    container_id = result.stdout.strip()
    print(f"Container ID: {container_id}")
    
    print("Validating files inside container...")
    exec_cmd = ["docker", "exec", "app-validator-container", "ls", "-l", "/usr/share/nginx/html/"]
    exec_result = subprocess.run(exec_cmd, capture_output=True, text=True)
    if exec_result.returncode != 0:
        print_err(f"FAIL: Could not list files in container. Error: {exec_result.stderr}")
        subprocess.run(["docker", "stop", "app-validator-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)
    print("Files in /usr/share/nginx/html/:")
    print(exec_result.stdout)
    if "index.html" not in exec_result.stdout:
        print_err("FAIL: index.html not found in container's /usr/share/nginx/html/")
        subprocess.run(["docker", "stop", "app-validator-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)
        
    time.sleep(3)
    
    success = False
    for attempt in range(5):
        try:
            req = urllib.request.Request("http://localhost:8080")
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    success = True
                    print("PASS: Received status code 200")
                    break
                else:
                    print_err(f"Warning: Received status code {response.getcode()}")
        except urllib.error.URLError as e:
            print_err(f"Warning: Unreachable. {e}")
        time.sleep(2)
        
    if not success:
        print_err("FAIL: Runtime check failed.")
        print_err("Fetching container logs...")
        logs_result = subprocess.run(["docker", "logs", "app-validator-container"], capture_output=True, text=True)
        print_err(f"Container Logs: {logs_result.stdout}\n{logs_result.stderr}")
        subprocess.run(["docker", "stop", "app-validator-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "rmi", "app-test-validator"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    print("Cleaning up temporary container and image...")
    subprocess.run(["docker", "stop", "app-validator-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "rmi", "app-test-validator"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    print("PASS: Runtime check successful.")
    print("All validations passed!")

if __name__ == '__main__':
    main()
