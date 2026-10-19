[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'test_skill.py'
& python $validator
exit $LASTEXITCODE
