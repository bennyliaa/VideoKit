# Builds the VideoKit add-to-app Flutter module AAR (14 §9.2, 13 §2.1) into flutter/videokit_embed/build/host/outputs/repo.
# Usage: powershell -File sample-host/measure/build_embed_aar.ps1
$ErrorActionPreference = 'Stop'
$repo = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location (Join-Path $repo 'flutter')
try {
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
