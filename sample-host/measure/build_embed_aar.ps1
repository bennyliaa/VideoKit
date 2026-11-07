# Builds the VideoKit add-to-app Flutter module AAR (14 §9.2, 13 §2.1) into flutter/videokit_embed/build/host/outputs/repo.
# 1. Publishes the Kit to build/kit-maven (the generated module host has no includeBuild; the plugin reads that repo).
# 2. flutter build aar.
# Usage: powershell -File sample-host/measure/build_embed_aar.ps1
$ErrorActionPreference = 'Stop'
$repo = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location $repo
try {
    & .\gradlew.bat publishKitMaven --console=plain
    if ($LASTEXITCODE -ne 0) { throw 'gradlew publishKitMaven failed' }
    & .\gradlew.bat --stop | Out-Null
    Set-Location (Join-Path $repo 'flutter')
    flutter pub get
    if ($LASTEXITCODE -ne 0) { throw 'flutter pub get failed' }
    Set-Location 'videokit_embed'
    # Same version as the Kit artifacts, so sample-host resolves com.videokit.embed:flutter_<mode>:1.0.0-dev.1.
    flutter build aar --build-number 1.0.0-dev.1 --no-profile
    if ($LASTEXITCODE -ne 0) { throw 'flutter build aar failed' }
} finally {
    Pop-Location
}
Write-Output "AAR repo: $(Join-Path $repo 'flutter\videokit_embed\build\host\outputs\repo')"
