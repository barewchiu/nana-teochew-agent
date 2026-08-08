# Pack holdout audio + manifest for AutoDL upload (forward-slash zip via Python).
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $ScriptDir "pack_holdout_for_autodl.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
