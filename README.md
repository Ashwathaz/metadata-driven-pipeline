# 🚀 Metadata-Driven CI/CD Pipeline with Gated Deployments & Runtime Validation

## 📌 Project Overview
A production-grade, metadata-driven CI/CD pipeline built to orchestrate staggered deployments between cross-functional teams (e.g., Development and Implementation teams). The system acts as a rigid gatekeeper, ensuring that infrastructure requirements and application code are fully synchronized and automatically validated before any Docker build or Kubernetes deployment occurs. 

## 🏗️ Architecture & Tech Stack
- **CI/CD Orchestration:** Jenkins (Pipeline-as-Code, Groovy)
- **Containerization:** Docker (Multi-stage builds, Alpine-based)
- **Container Orchestration:** Kubernetes (Deployments, NodePort Services)
- **Validation Engine:** Python 3 (Automated Pre-flight checks)
- **Frontend / Application:** HTML5, CSS3

## 🔄 Pipeline Flow & Gating Logic
The CI/CD workflow strictly implements an "All-or-Nothing" approach.

1. **Trigger:** Pipeline polls SCM and triggers on push to the repository.
2. **Pre-check Barrier (Gating):** 
   - ❌ **Only Metadata exists:** Fails with "Waiting for Development Team"
   - ❌ **Only Code exists:** Fails with "Waiting for Implementation Team"
   - ✅ **Both exist:** Pipeline proceeds.
3. **Automated Validation:** The `validator.py` script executes a 3-tier check (see Validation Engine).
4. **Build & Tag:** Docker image is built and tagged incrementally with `${BUILD_NUMBER}` and `latest`.
5. **K8s Deployment:** Applies standard Kubernetes Deployment and Service configurations with zero downtime.
6. **Dynamic Routing Extraction:** Dynamically fetches the node's public IP (`ifconfig.me`) and binds it with the NodePort to generate and print a public-facing URL in the Jenkins console log.

## 🛡️ Validation Engine (3-Tier Check)
Before containerizing, the system executes stringent validation:
- **L1 (File Integrity):** Parses `metadata.json` to verify that every required file (`index.html`, `style.css`) is physically present in the workspace.
- **L2 (Content Verification):** Deep-scans the source code to guarantee that `<title>` and core tags match the expected metadata requirements.
- **L3 (Runtime/Simulated Test):** Spins up a temporary isolated Docker container, performs an automated HTTP `curl` request to the web server, verifies an HTTP 200 OK response, and cleanly destroys the temporary container.

---

## 💼 Resume-Ready Bullet Points
*Feel free to copy/paste and adapt these bullet points straight into your resume!*

- **DevOps / CI/CD Automation:** Engineered a metadata-driven Jenkins CI/CD pipeline featuring a strict gating mechanism that synchronizes deployment workflows between cross-functional teams, reducing premature build failures by 100%.
- **Automated Pre-Flight Testing:** Designed a Python-based 3-tier validation engine that performs File Integrity (L1), Content Verification (L2), and isolated Runtime Container testing (L3) prior to the build phase.
- **Containerization & Orchestration:** Containerized web applications using Docker (Nginx Alpine) and automated deployment to a Kubernetes cluster utilizing declarative YAML manifests (Deployments, NodePort Services).
- **Pipeline Optimization:** Implemented dynamic public IP extraction and intelligent terminal logging within the Groovy Jenkinsfile, improving visibility and mean-time-to-test (MTTT) for developers.

## 🚀 Setup & Execution 
1. Place `config/metadata.json` and `app/` files in the repository.
2. Ensure Jenkins has the **Pipeline Utility Steps** plugin installed.
3. Give Jenkins node permissions for `docker` and `kubectl`.
4. Trigger a build—watch the validation and get your live URL!
