# Requires -Version 7.0
param(
    [Parameter()]
    [string]$CommitMessage = "Auto-commit: Committing all changes",
    [Parameter()]
    [string]$Branch = "develop"
)

# Function to check if gh CLI is installed
function Test-GHInstalled {
    try {
        $null = Get-Command gh -ErrorAction Stop
        return $true
    }
    catch {
        Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
        return $false
    }
}

# Function to check if git is installed
function Test-GitInstalled {
    try {
        $null = Get-Command git -ErrorAction Stop
        return $true
    }
    catch {
        Write-Error "Git is not installed. Please install it from https://git-scm.com/"
        return $false
    }
}

# Function to check if user is authenticated with gh CLI
function Test-GHAuthenticated {
    try {
        $status = gh auth status 2>&1
        return $true
    }
    catch {
        Write-Error "Not authenticated with GitHub CLI. Please run 'gh auth login'"
        return $false
    }
}

# Function to get the current branch name
function Get-CurrentBranch {
    return git branch --show-current
}

# Function to stage and commit all changes
function Invoke-GitCommit {
    param(
        [string]$Message
    )
    
    Write-Host "Staging all changes..." -ForegroundColor Yellow
    git add -A
    
    # Check if there are any changes to commit
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "No changes to commit." -ForegroundColor Green
        return $false
    }
    
    Write-Host "Committing changes..." -ForegroundColor Yellow
    git commit -m $Message
    return $true
}

# Function to push changes to remote
function Invoke-GitPush {
    param(
        [string]$Branch
    )
    
    Write-Host "Pushing to $Branch..." -ForegroundColor Yellow
    git push origin $Branch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push to $Branch"
        return $false
    }
    return $true
}

# Function to watch GitHub Actions runs
function Watch-GHRuns {
    Write-Host "Fetching recent workflow runs..." -ForegroundColor Yellow
    
    # Get the repo name from git remote
    $remoteUrl = git config --get remote.origin.url
    $repoName = $remoteUrl -replace '.*github.com[:/](.*)\.git$', '$1'
    
    # Watch workflow runs
    Write-Host "Watching workflow runs for $repoName..." -ForegroundColor Cyan
    gh run watch
    
    # List all active runs
    gh run list --limit 5
}

# Main script execution
Write-Host "Starting commit and watch script..." -ForegroundColor Cyan

# Check prerequisites
if (-not (Test-GitInstalled)) { exit 1 }
if (-not (Test-GHInstalled)) { exit 1 }
if (-not (Test-GHAuthenticated)) { exit 1 }

# Get current branch
$currentBranch = Get-CurrentBranch
if ($currentBranch -ne $Branch) {
    Write-Host "Currently on branch '$currentBranch'. Switching to '$Branch'..." -ForegroundColor Yellow
    git checkout $Branch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to switch to branch $Branch"
        exit 1
    }
}

# Commit changes
$committed = Invoke-GitCommit -Message $CommitMessage
if (-not $committed) {
    Write-Host "No changes to push. Proceeding to watch existing runs..." -ForegroundColor Yellow
}
else {
    # Push changes
    $pushed = Invoke-GitPush -Branch $Branch
    if (-not $pushed) { exit 1 }
}

# Watch GitHub Actions runs
Watch-GHRuns

Write-Host "Script completed successfully!" -ForegroundColor Green 