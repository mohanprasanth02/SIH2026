#!/usr/bin/env pwsh
# SatQuery AI - Windows Quick Start Script
# Run: .\scripts\dev-start.ps1

$ErrorActionPreference = "Stop"
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " SatQuery AI - Development Startup" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check .env
if (-not (Test-Path ".\.env")) {
    Write-Host "[!] .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".\.env.example" ".\.env" -ErrorAction SilentlyContinue
    Write-Host "[!] Please edit .env and add your GEMINI_API_KEY" -ForegroundColor Yellow
}

# Detect Python 3.13
$pythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
if (-not (Test-Path $pythonCmd)) {
    $pythonCmd = "python"
}

# Backend
Write-Host "`n[1/2] Starting Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\backend'; & '$pythonCmd' -m uvicorn app.main:app --reload --port 8000"
) -WindowStyle Normal

# Frontend
Write-Host "[2/2] Starting Frontend (Vite)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\frontend'; npm run dev"
) -WindowStyle Normal

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host " Services starting..." -ForegroundColor Cyan
Write-Host " Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " Frontend: http://localhost:5173" -ForegroundColor White
Write-Host " API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Cyan
