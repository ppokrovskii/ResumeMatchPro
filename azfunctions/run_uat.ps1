# PowerShell script to run UAT tests
# Navigate to the azfunctions directory
$currentDir = $PSScriptRoot
Write-Host "Current directory: $currentDir"

# Activate virtual environment if it exists
if (Test-Path "$currentDir\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & "$currentDir\.venv\Scripts\Activate.ps1"
}
else {
    Write-Host "Virtual environment not found at $currentDir\.venv"
    Write-Host "Please create and activate a virtual environment before running this script."
    exit 1
}

# Load environment variables from .env.test file
Write-Host "Loading environment variables from .env.test..."
$envFile = "$currentDir\tests\.env.test"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove quotes if present
            if ($value -match '^"(.*)"$') {
                $value = $matches[1]
            }
            Write-Host "Setting environment variable: $key"
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}
else {
    Write-Host "Environment file not found at $envFile"
    exit 1
}

# Check for emulators
Write-Host "Checking if emulators are running..."
python -c "import socket; print('Cosmos DB Emulator running:',socket.socket().connect_ex(('localhost', 8081)) == 0)"
python -c "import socket; print('Azurite Blob running:',socket.socket().connect_ex(('127.0.0.1', 10000)) == 0)"
python -c "import socket; print('Azurite Queue running:',socket.socket().connect_ex(('127.0.0.1', 10001)) == 0)"

# Run the UAT tests
Write-Host "Running UAT tests..."
python "$currentDir\uat\run_uat_tests.py" $args

# Deactivate virtual environment
if (Test-Path function:deactivate) {
    deactivate
} 