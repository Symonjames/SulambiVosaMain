# Add PostgreSQL bin folder to your user PATH (Windows)
# Run in PowerShell: .\add-pg-to-path.ps1
# If your PostgreSQL is in a different path, run: .\add-pg-to-path.ps1 -BinPath "C:\Your\Path\To\PostgreSQL\16\bin"

param(
    [string]$BinPath
)

if (-not $BinPath) {
    $possible = @(
        "C:\Program Files\PostgreSQL\18\bin",
        "C:\Program Files\PostgreSQL\17\bin",
        "C:\Program Files\PostgreSQL\16\bin",
        "C:\Program Files\PostgreSQL\15\bin",
        "C:\Program Files\PostgreSQL\14\bin"
    )
    foreach ($p in $possible) {
        if (Test-Path (Join-Path $p "pg_dump.exe")) {
            $BinPath = $p
            break
        }
    }
}

if (-not $BinPath -or -not (Test-Path (Join-Path $BinPath "pg_dump.exe"))) {
    Write-Host "PostgreSQL bin folder not found. Specify it explicitly:" -ForegroundColor Red
    Write-Host '  .\add-pg-to-path.ps1 -BinPath "C:\Program Files\PostgreSQL\16\bin"' -ForegroundColor Yellow
    exit 1
}

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -split ";" -contains $BinPath) {
    Write-Host "Already in PATH: $BinPath" -ForegroundColor Green
    exit 0
}

$newPath = $BinPath + ";" + $currentPath
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")
Write-Host "Added to user PATH: $BinPath" -ForegroundColor Green
Write-Host "Open a NEW PowerShell or terminal window for it to take effect. Then run: pg_dump --version" -ForegroundColor Yellow
