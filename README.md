# Metadata-Driven CI/CD Pipeline

## Project Overview
This project establishes a metadata-driven CI/CD system using Jenkins and Docker. The pipeline acts as a gated barrier ensuring the deployment only proceeds if valid requirement metadata and complete implementation code coincide. 

## Architecture
- **Web App**: Minimalist HTML and CSS application.
- **Docker**: Containerizes the front end with NGINX.
- **Python Validator**: Pre-flight test validator triggering localized environment validations validating static configs.
- **Jenkins**: Handles deployment orchestration triggering off standard Git push hooks.

## Pipeline Flow
1. **Trigger**: Pulls on repository changes (e.g. Any branch push).
2. **Pre-check**: Establishes existence of required code/metadata parameters.
   - If ONLY config present: `Waiting for Development Team`
   - If ONLY code present: `Waiting for Implementation Team`
3. **Read Metadata**: Evaluates `port` mappings.
4. **Validation (Validator)**:
   - **L1 (File Check)**: Ascertains structural project mapping (`index.html`, `style.css`).
   - **L2 (Content Check)**: Confirms metadata mapped details specifically expected title elements internally.
   - **L3 (Runtime Check)**: Boots a temp Docker daemon assessing NGINX network functionality.
5. **Build Docker Image**: Tags app dynamically tracking Jenkins `BUILD_NUMBER`.
6. **Deploy Container**: Spins up NGINX discarding previous legacy active versions internally overlapping.
7. **Print Public URL**: Queries internet gateway tracking external URL mappings successfully exposing app.

## Tools Used
- NGINX inside Docker (`nginx:alpine`)
- Jenkins Server (`readJSON`)
- Python Environment (`subprocess/requests validator`)

## Setup Steps (Jenkins + Docker)
1. Provide Jenkins worker `Docker` availability ensuring groups overlap appropriately.
2. Initialize repository inside Jenkins pointing Pipeline towards `jenkins/Jenkinsfile`.
3. Provide required plugin inside Jenkins: `Pipeline Utility Steps` (for `readJSON`).

## How to run locally
Ensure active Docker container and test validator behavior standalone bypassing Jenkins:
```bash
python validator/validator.py
```
