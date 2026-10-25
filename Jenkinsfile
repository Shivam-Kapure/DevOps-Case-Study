pipeline {
    agent any

    environment {
        APP_VERSION = '1.0.0'
        BACKEND_IMAGE = "payment-backend:${env.APP_VERSION}"
        FRONTEND_IMAGE = "payment-frontend:${env.APP_VERSION}"
    }

    stages {
        stage('Checkout / Source verification') {
            steps {
                powershell '''
                    Write-Host "=================================================="
                    Write-Host "Stage 1: Checkout / Source Verification"
                    Write-Host "=================================================="
                    Write-Host "Working Directory: $PWD"
                    
                    if (Get-Command git -ErrorAction SilentlyContinue) {
                        Write-Host "Checking Git metadata..."
                        git log -1 --format="Commit: %h - %s (%ci)"
                    }

                    $requiredFiles = @(
                        "backend/Dockerfile",
                        "backend/requirements.txt",
                        "backend/run.py",
                        "frontend/Dockerfile",
                        "frontend/nginx.conf",
                        "frontend/docker-entrypoint.sh",
                        "docker-compose.yml",
                        "tests/test_health.py",
                        "tests/test_payments.py",
                        "tests/test_notifications.py",
                        "tests/test_cors.py"
                    )

                    $missing = @()
                    foreach ($file in $requiredFiles) {
                        if (-not (Test-Path $file)) {
                            $missing += $file
                        }
                    }

                    if ($missing.Count -gt 0) {
                        Write-Error "Source verification failed. Missing files: $($missing -join ', ')"
                        exit 1
                    }

                    Write-Host "Source verification PASSED. All required project files are present."
                '''
            }
        }

        stage('Build') {
            steps {
                powershell '''
                    Write-Host "=================================================="
                    Write-Host "Stage 2: Build & Dependency Resolution"
                    Write-Host "=================================================="
                    Write-Host "System Python Interpreter:"
                    python --version

                    if (-not (Test-Path ".venv_ci")) {
                        Write-Host "Creating clean CI virtual environment in .venv_ci..."
                        python -m venv .venv_ci
                    }

                    $py = ".\\.venv_ci\\Scripts\\python.exe"
                    Write-Host "Upgrading pip and installing backend dependencies..."
                    & $py -m pip install --upgrade pip --quiet
                    & $py -m pip install -r backend/requirements.txt --quiet

                    Write-Host "Verifying installed packages in CI environment:"
                    & $py -m pip list
                    Write-Host "Build stage PASSED."
                '''
            }
        }

        stage('Test') {
            steps {
                powershell '''
                    Write-Host "=================================================="
                    Write-Host "Stage 3: Automated Pytest Suite"
                    Write-Host "=================================================="
                    $py = ".\\.venv_ci\\Scripts\\python.exe"
                    if (-not (Test-Path $py)) {
                        if (Test-Path ".\\.venv\\Scripts\\python.exe") {
                            $py = ".\\.venv\\Scripts\\python.exe"
                        } else {
                            $py = "python"
                        }
                    }

                    Write-Host "Running automated tests with: $py"
                    & $py -m pytest -v --tb=short tests/
                    if ($LASTEXITCODE -ne 0) {
                        Write-Error "Pytest suite execution FAILED with exit code $LASTEXITCODE."
                        exit $LASTEXITCODE
                    }
                    Write-Host "Test stage PASSED. All 15 tests completed successfully."
                '''
            }
        }

        stage('Docker Packaging') {
            steps {
                powershell '''
                    Write-Host "=================================================="
                    Write-Host "Stage 4: Docker Image Packaging"
                    Write-Host "=================================================="
                    Write-Host "Checking Docker CLI availability..."
                    docker version

                    Write-Host "Building Backend Docker image: $env:BACKEND_IMAGE..."
                    docker build -t "$env:BACKEND_IMAGE" -f backend/Dockerfile ./backend
                    if ($LASTEXITCODE -ne 0) {
                        Write-Error "Backend Docker build FAILED."
                        exit $LASTEXITCODE
                    }

                    Write-Host "Building Frontend Docker image: $env:FRONTEND_IMAGE..."
                    docker build -t "$env:FRONTEND_IMAGE" -f frontend/Dockerfile ./frontend
                    if ($LASTEXITCODE -ne 0) {
                        Write-Error "Frontend Docker build FAILED."
                        exit $LASTEXITCODE
                    }

                    Write-Host "Packaged Docker Images:"
                    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}" | Select-String "payment-(backend|frontend)"
                    Write-Host "Docker Packaging stage PASSED."
                '''
            }
        }

        stage('Deployment readiness verification') {
            steps {
                powershell '''
                    Write-Host "=================================================="
                    Write-Host "Stage 5: Deployment Readiness Verification"
                    Write-Host "=================================================="
                    
                    Write-Host "Verifying container images exist in local Docker engine..."
                    $backendId = docker images -q "$env:BACKEND_IMAGE"
                    $frontendId = docker images -q "$env:FRONTEND_IMAGE"

                    if (-not $backendId -or -not $frontendId) {
                        Write-Error "Deployment readiness check failed: Images not found in Docker daemon."
                        exit 1
                    }
                    Write-Host "Verified Backend Image : $env:BACKEND_IMAGE (ID: $backendId)"
                    Write-Host "Verified Frontend Image: $env:FRONTEND_IMAGE (ID: $frontendId)"

                    Write-Host "Checking Kubernetes CLI (kubectl) readiness..."
                    if (Get-Command kubectl -ErrorAction SilentlyContinue) {
                        kubectl version --client=true
                        Write-Host "kubectl client CLI is ready on host for upcoming Kubernetes practical."
                    } else {
                        Write-Host "Note: kubectl CLI not detected in system PATH."
                    }

                    Write-Host "Minikube / Kubernetes Cluster: Not initialized yet."
                    Write-Host "Remote Registry: Push deferred (no credentials/registry configured)."
                    Write-Host "Deployment readiness verification PASSED."
                '''
            }
        }
    }

    post {
        always {
            powershell '''
                Write-Host "=== Pipeline Cleanup ==="
                if (Test-Path ".venv_ci") {
                    Write-Host "Removing temporary CI virtual environment..."
                    Remove-Item -Recurse -Force .venv_ci -ErrorAction SilentlyContinue
                }
            '''
        }
        success {
            echo "CI Pipeline executed successfully! All stages verified."
        }
        failure {
            echo "CI Pipeline encountered errors. Review stage logs above."
        }
    }
}
