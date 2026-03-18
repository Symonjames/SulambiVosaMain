# Migrate data from old Render PostgreSQL DB to new Render PostgreSQL DB
# 1. Install PostgreSQL client tools (see README below) if needed
# 2. Set OLD_DATABASE_URL and NEW_DATABASE_URL below, then run this script

param(
    [Parameter(Mandatory = $true)]
    [string]$OldDatabaseUrl,
    [Parameter(Mandatory = $true)]
    [string]$NewDatabaseUrl,
    [string]$BackupFile = "old_backup.dump"
)

$ErrorActionPreference = "Stop"
$BackupPath = Join-Path $PSScriptRoot $BackupFile

Write-Host "Step 1: Dumping from OLD database..." -ForegroundColor Cyan
& pg_dump $OldDatabaseUrl --no-owner --no-acl -F c -f $BackupPath
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }
Write-Host "Backup saved to: $BackupPath" -ForegroundColor Green

Write-Host "`nStep 2: Restoring into NEW database..." -ForegroundColor Cyan
& pg_restore -d $NewDatabaseUrl --no-owner --no-acl --clean --if-exists $BackupPath
# pg_restore often exits 1 for non-fatal warnings; 0 = success
if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 1) { throw "pg_restore failed with exit code $LASTEXITCODE" }
Write-Host "Restore completed." -ForegroundColor Green

Write-Host "`nDone. Update your backend DATABASE_URL in Render to the NEW database URL and redeploy." -ForegroundColor Yellow
