# Run lint-staged first since it modifies files
Set-Location frontend
Write-Host "Running lint-staged..."
npx lint-staged
if ($LASTEXITCODE -ne 0) { exit 1 }

# Start frontend and backend tests in parallel
Write-Host "Starting tests in parallel..."

$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Write-Host "Running frontend tests..."
    npm run test:ci
}

$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD/..
    Set-Location azfunctions
    Write-Host "Running Azure Functions tests..."
    .venv/Scripts/python -m pytest tests/ -v -n auto
}

# Wait for both jobs to complete and get their results
$frontendResult = Wait-Job $frontendJob | Receive-Job
$backendResult = Wait-Job $backendJob | Receive-Job

# Display results
Write-Host "Frontend test results:"
Write-Host $frontendResult
Write-Host "Backend test results:"
Write-Host $backendResult

# Check if either job failed
if ($frontendJob.State -eq "Failed" -or $backendJob.State -eq "Failed") {
    Write-Host "Tests failed!"
    exit 1
}

# Check exit codes
if ($frontendJob.ChildJobs[0].JobStateInfo.State -eq "Failed" -or $backendJob.ChildJobs[0].JobStateInfo.State -eq "Failed") {
    Write-Host "Tests failed!"
    exit 1
}

Write-Host "All tests passed!" 