$preCommitContent = @'
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

cd frontend
echo "Running lint-staged..."
npx lint-staged || exit 1

echo "Running frontend tests..."
npm run test:ci || exit 1

cd ../azfunctions
echo "Running Azure Functions tests..."
# Run tests and exit on failure
python -m pytest tests/ -v || exit 1

# Always run schema compatibility tests, regardless of emulator status
echo "Running schema compatibility tests..."
python -m pytest uat/test_schema_compatibility.py -v || exit 1

echo "Running UAT tests if emulators are available..."
python -c "import socket; s1=socket.socket(); s2=socket.socket(); s3=socket.socket(); cosmos_running=s1.connect_ex((\"localhost\", 8081)) == 0; blob_running=s2.connect_ex((\"127.0.0.1\", 10000)) == 0; queue_running=s3.connect_ex((\"127.0.0.1\", 10001)) == 0; s1.close(); s2.close(); s3.close(); exit(0 if cosmos_running and blob_running and queue_running else 1)" && powershell -Command "./run_uat.ps1" || echo "Skipping full UAT tests - emulators not running"
'@

# Ensure the .husky directory exists
if (-not (Test-Path -Path ".husky")) {
    New-Item -Path ".husky" -ItemType Directory -Force
}

# Write the pre-commit hook content to the file
$preCommitContent | Out-File -FilePath ".husky/pre-commit" -Encoding utf8 -NoNewline

# Ensure the file has Unix-style line endings (LF instead of CRLF)
$content = [System.IO.File]::ReadAllText(".husky/pre-commit")
$content = $content -replace "`r`n", "`n"
[System.IO.File]::WriteAllText(".husky/pre-commit", $content)

Write-Host "Pre-commit hook has been fixed successfully."
