# Decrypts the Vita dump (game + DLC) with psvpfsparser.
# The key for each folder is read from its NoNpDRM work.bin at offset 0x50.
#
# Usage (from the project root):
#   powershell -ExecutionPolicy Bypass -File scripts\decrypt_vita.ps1 -Parser "C:\path\to\psvpfsparser.exe"
#
# psvpfsparser: https://github.com/motoharu-gosuto/psvpfstools/releases (release_win64_7.zip)
# The tool contacts the F00D key service (cma.henkaku.xyz), so this needs internet access.

param(
    [Parameter(Mandatory = $true)][string]$Parser,
    [string]$Source = "Shin Gundam Musou (JPN)",
    [string]$Dest   = "decrypted\vita",
    [string]$F00d   = "cma.henkaku.xyz",
    [switch]$SkipDlc
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Get-Klicensee([string]$workBin) {
    $b = [IO.File]::ReadAllBytes($workBin)
    $magic = -join ($b[8..15] | ForEach-Object { $_.ToString("x2") })
    if ($magic -ne "efcdab8967452301") { throw "$workBin is not a NoNpDRM fake license" }
    return -join ($b[0x50..0x5F] | ForEach-Object { $_.ToString("x2") })
}

$targets = @(Get-ChildItem (Join-Path $root "$Source\app") -Directory | ForEach-Object { @{ In = $_.FullName; Rel = "app\$($_.Name)" } })
if (-not $SkipDlc) {
    Get-ChildItem (Join-Path $root "$Source\addcont") -Directory | ForEach-Object {
        $tid = $_.Name
        Get-ChildItem $_.FullName -Directory | ForEach-Object {
            $targets += @{ In = $_.FullName; Rel = "addcont\$tid\$($_.Name)" }
        }
    }
}

$failed = @()
foreach ($t in $targets) {
    $key = Get-Klicensee (Join-Path $t.In "sce_sys\package\work.bin")
    $out = Join-Path $root "$Dest\$($t.Rel)"
    New-Item -ItemType Directory -Force $out | Out-Null
    Write-Host "== $($t.Rel)  (key $key)"
    & $Parser -i $t.In -o $out -k $key -f $F00d
    if ($LASTEXITCODE -ne 0) { $failed += $t.Rel; Write-Warning "FAILED: $($t.Rel)" }
}

Write-Host ""
if ($failed.Count) { Write-Warning "Failed: $($failed -join ', ')" } else { Write-Host "All done -> $Dest" }
