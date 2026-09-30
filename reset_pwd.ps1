Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Resetting MySQL Root Password to: root123     " -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "[1/4] Stopping MySQL80 service..." -ForegroundColor Gray
Stop-Service -Name MySQL80 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

$mysqld = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
$myini = "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"
$sqlFile = "$PSScriptRoot\mysql_init_password.sql"

Write-Host "[2/4] Applying password reset with mysqld..." -ForegroundColor Gray
$process = Start-Process -FilePath $mysqld -ArgumentList "--defaults-file=`"$myini`" --init-file=`"$sqlFile`" --console" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5

Write-Host "[3/4] Stopping background reset worker..." -ForegroundColor Gray
Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[4/4] Restarting MySQL80 service..." -ForegroundColor Gray
Start-Service -Name MySQL80

Write-Host "`nSUCCESS! MySQL root password is now: root123" -ForegroundColor Green
Write-Host "Press any key to close this window..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
