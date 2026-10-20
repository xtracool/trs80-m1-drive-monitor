# Windows verification for sa400_led_monitor: KiCad 10 DRC + ERC + fab outputs.
# Run from the project root in PowerShell:  .\gen\check.ps1
$K = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
$P = "C:\Program Files\KiCad\10.0\bin\python.exe"
if (-not (Test-Path $K)) { Write-Error "kicad-cli not found at $K - edit the path at the top of this script"; exit 1 }
& $P gen\postprocess.py kicad\sa400_led_monitor.kicad_pcb
& $K pcb drc --schematic-parity --severity-all --format json --output output\drc.json kicad\sa400_led_monitor.kicad_pcb
& $K sch erc --severity-all --format json --output output\erc.json kicad\sa400_led_monitor.kicad_sch
New-Item -ItemType Directory -Force output\gerbers | Out-Null
& $K pcb export gerbers --output output\gerbers\ --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts" --subtract-soldermask kicad\sa400_led_monitor.kicad_pcb
& $K pcb export drill --output output\gerbers\ --format excellon --excellon-separate-th --generate-map --map-format gerberx2 kicad\sa400_led_monitor.kicad_pcb
Write-Host "DRC violations:" (Get-Content output\drc.json | ConvertFrom-Json).violations.Count
Write-Host "ERC violations:" ((Get-Content output\erc.json | ConvertFrom-Json).sheets | ForEach-Object { $_.violations.Count } | Measure-Object -Sum).Sum
