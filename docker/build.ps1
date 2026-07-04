Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building Patient Monitor Unified Docker Image..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if docker daemon is running
& docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker daemon is not running! Please start Docker Desktop and try again."
    exit 1
}

# Navigate to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

# Build Docker Image
Write-Host "Building docker image 'patient-monitor:latest'..." -ForegroundColor Yellow
& docker build -t patient-monitor:latest -f Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed!"
    Pop-Location
    exit 1
}

# Save Docker Image to Tar file
$outputPath = Join-Path $scriptDir "patient-monitor-image.tar"
Write-Host "Saving docker image to $outputPath..." -ForegroundColor Yellow
& docker save -o $outputPath patient-monitor:latest
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to save docker image to tar!"
    Pop-Location
    exit 1
}

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Successfully built and exported Docker image!" -ForegroundColor Green
Write-Host "Image Tar File: $outputPath" -ForegroundColor Green
Write-Host "To load it on your server, run:" -ForegroundColor Green
Write-Host "  docker load -i patient-monitor-image.tar" -ForegroundColor White
Write-Host "To run the container, run:" -ForegroundColor Green
Write-Host "  docker run -d -p 80:80 --name patient-monitor patient-monitor:latest" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green

Pop-Location
