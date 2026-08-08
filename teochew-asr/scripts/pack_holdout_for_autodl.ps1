# Pack holdout audio + manifest for AutoDL upload
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Hold = Join-Path $Root "data\asr\eval_holdout"
$OutDir = Join-Path $Root "data\asr\eval_holdout"
$Zip = Join-Path $OutDir "holdout_audio.zip"
$Stage = Join-Path $env:TEMP "nana_holdout_pack"

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $Stage "audio") | Out-Null
Copy-Item (Join-Path $Hold "manifest.csv") (Join-Path $Stage "manifest.csv")
Copy-Item (Join-Path $Hold "audio\*") (Join-Path $Stage "audio") -Include *.m4a,*.mp3,*.wav

if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $Zip -Force
$mb = [math]::Round((Get-Item $Zip).Length / 1MB, 2)
Write-Host "Wrote $Zip ($mb MB)"
