$ErrorActionPreference='Stop'
if((Get-FileHash -LiteralPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/read-only-release.json' -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03'){throw 'K_EXACT_BINDING_CHANGED'}
if((Get-FileHash -LiteralPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/execution-scope.json' -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'ea8a82cb947420197e42f62539ec327147117580e83ada5598981a7dfa8a6a5e'){throw 'K_EXACT_BINDING_CHANGED'}
if((Get-FileHash -LiteralPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/observer-request.json' -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a2040964fbcbae5e070d84472a7e4d73454e6f1488441466cc96ec8723e5bf5d'){throw 'K_EXACT_BINDING_CHANGED'}
if((Get-FileHash -LiteralPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/artifacts/e13k-host-tools.jar' -Algorithm SHA256).Hash.ToLowerInvariant() -ne '09aec958873b2f4cf6fcb562e608d0143f7f865c742170bd30fd49432b5f9797'){throw 'K_EXACT_BINDING_CHANGED'}
if((Get-FileHash -LiteralPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/policy/observe_e13k.ps1' -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'b6ab0aec0df4ec62a2b317d7abcf21a8c7d0c63e5b2b9605c0a12e9bb506078d'){throw 'K_EXACT_BINDING_CHANGED'}
$captured = & 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/policy/observe_e13k.ps1' -RequestPath 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/observer-request.json' | Out-String
$facts = $captured | ConvertFrom-Json -ErrorAction Stop
$consoleSha=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($captured))).ToLowerInvariant()
$summary=@{r=[bool]$facts.allOriginalResourcesReturned;m=[bool]$facts.metadataRecordFilesReturnedAtConsole;h=$consoleSha}|ConvertTo-Json -Compress
if([Text.Encoding]::UTF8.GetByteCount($summary) -gt 128){throw 'K_FIXED_SUMMARY_BOUND'}
[Console]::WriteLine($summary)
