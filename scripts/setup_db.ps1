# .\setup_db.ps1 -DbHost "your-rds-endpoint.amazonaws.com" -DbUser "postgres" -DbName "your_db_name"


param(
    [string]$DbName   = "your_db_name",
    [string]$DbUser   = "postgres",
    [string]$DbHost   = "localhost",
    [string]$DbPort   = "5432",
    [string]$SqlFile  = "database_table.sql"
)

$env:PGPASSWORD = Read-Host "Enter PostgreSQL password" -AsSecureString | `
    ConvertFrom-SecureString -AsPlainText

$ErrorActionPreference = "Stop"

# Check if DB exists, create if not
$exists = psql -U $DbUser -h $DbHost -p $DbPort -tAc `
    "SELECT 1 FROM pg_database WHERE datname='$DbName'" postgres

if ($exists -ne "1") {
    Write-Host "Creating database '$DbName'..."
    psql -U $DbUser -h $DbHost -p $DbPort -c "CREATE DATABASE $DbName" postgres
} else {
    Write-Host "Database '$DbName' already exists, skipping creation."
}

# Run schema file
Write-Host "Running $SqlFile..."
psql -U $DbUser -h $DbHost -p $DbPort -d $DbName -f $SqlFile

Write-Host "Done! '$DbName' is ready."