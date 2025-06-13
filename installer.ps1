# installer.ps1  (run as Administrator on Windows)
$svc = "PyServerReport"
$exe = Join-Path $PSScriptRoot "service.py"
& $env:PYTHON "service.py" install
sc.exe failure $svc reset= 0 actions= restart/5000
Start-Service $svc
