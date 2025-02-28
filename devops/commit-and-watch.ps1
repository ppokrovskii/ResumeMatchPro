# Requires -Version 7.0
param(
    [Parameter()]
    [string]$CommitMessage = "Auto-commit: Committing all changes",
    [Parameter()]
    [string]$Branch = "develop"
)

# Set error action preference to stop on any error
$ErrorActionPreference = "Stop"

# Function to check if gh CLI is installed
function Test-GHInstalled {
    try {
        $null = Get-Command gh -ErrorAction Stop
        return $true
    }
    catch {
        Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/" -ErrorAction Stop
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
        Write-Error "Git is not installed. Please install it from https://git-scm.com/" -ErrorAction Stop
        return $false
    }
}

# Function to check if user is authenticated with gh CLI
function Test-GHAuthenticated {
    try {
        $status = gh auth status 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "GitHub CLI authentication failed"
        }
        return $true
    }
    catch {
        Write-Error "Not authenticated with GitHub CLI. Please run 'gh auth login'" -ErrorAction Stop
        return $false
    }
}

# Function to get the current branch name
function Get-CurrentBranch {
    $branch = git branch --show-current
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to get current branch" -ErrorAction Stop
    }
    return $branch
}

# Function to stage and commit all changes
function Invoke-GitCommit {
    param(
        [string]$Message
    )
    
    Write-Host "Staging all changes..." -ForegroundColor Yellow
    git add -A
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to stage changes" -ErrorAction Stop
        return $false
    }
    
    # Check if there are any changes to commit
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "No changes to commit." -ForegroundColor Green
        return $false
    }
    
    Write-Host "Committing changes..." -ForegroundColor Yellow
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to commit changes" -ErrorAction Stop
        return $false
    }
    
    # Verify the commit was successful
    $lastCommit = git log -1 --pretty=format:"%s"
    if ($LASTEXITCODE -ne 0 -or -not $lastCommit) {
        Write-Error "Failed to verify commit" -ErrorAction Stop
        return $false
    }
    
    Write-Host "Successfully committed changes: $lastCommit" -ForegroundColor Green
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
        Write-Error "Failed to push to $Branch" -ErrorAction Stop
        return $false
    }
    return $true
}

# Function to watch GitHub Actions runs
function Watch-GHRuns {
    Write-Host "Fetching recent workflow runs..." -ForegroundColor Yellow
    
    # Get the repo name from git remote
    $remoteUrl = git config --get remote.origin.url
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to get remote URL" -ErrorAction Stop
        return
    }
    
    $repoName = $remoteUrl -replace '.*github.com[:/](.*)\.git$', '$1'
    
    # Watch workflow runs
    Write-Host "Watching workflow runs for $repoName..." -ForegroundColor Cyan
    gh run watch
    
    # List all active runs
    gh run list --limit 5
}

# Main script execution
try {
    Write-Host "Starting commit and watch script..." -ForegroundColor Cyan

    # Check prerequisites
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    if (-not (Test-GitInstalled)) { 
        Write-Error "Git is not installed. Exiting script." -ErrorAction Stop
        exit 1 
    }
    if (-not (Test-GHInstalled)) { 
        Write-Error "GitHub CLI is not installed. Exiting script." -ErrorAction Stop
        exit 1 
    }
    if (-not (Test-GHAuthenticated)) { 
        Write-Error "Not authenticated with GitHub CLI. Exiting script." -ErrorAction Stop
        exit 1 
    }

    # Get current branch
    $currentBranch = Get-CurrentBranch
    if ($currentBranch -ne $Branch) {
        Write-Host "Currently on branch '$currentBranch'. Switching to '$Branch'..." -ForegroundColor Yellow
        git checkout $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to switch to branch $Branch. Exiting script." -ErrorAction Stop
            exit 1
        }
    }

    # Commit changes
    $committed = Invoke-GitCommit -Message $CommitMessage
    if (-not $committed) {
        Write-Host "No changes were committed. Proceeding to watch existing runs..." -ForegroundColor Yellow
    }
    else {
        # Push changes
        Write-Host "Attempting to push changes..." -ForegroundColor Yellow
        $pushed = Invoke-GitPush -Branch $Branch
        if (-not $pushed) { 
            Write-Error "Failed to push changes. Exiting script." -ErrorAction Stop
            exit 1 
        }
        Write-Host "Successfully pushed changes to $Branch." -ForegroundColor Green
    }

    # Watch GitHub Actions runs
    Watch-GHRuns

    Write-Host "Script completed successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Script failed: $_" -ErrorAction Continue
    exit 1
} 