# run_etl.ps1 — 매일 자동 실행용
$ErrorActionPreference = 'Stop'

# 1) 작업 폴더
Set-Location $env:USERPROFILE\Desktop\project-etl-sql

# 2) 로그 파일
$ts  = Get-Date -Format "yyyyMMdd_HHmmss"
$log = Join-Path (Join-Path (Get-Location) 'logs') ("etl_$ts.log")
New-Item -ItemType Directory -Force -Path .\logs | Out-Null

'=== START ' + (Get-Date) | Tee-Object -FilePath $log
py etl.py            2>&1 | Tee-Object -FilePath $log -Append
py load_to_sqlite.py 2>&1 | Tee-Object -FilePath $log -Append
'=== END   ' + (Get-Date) | Tee-Object -FilePath $log -Append

# 3) 14일 지난 로그 정리
Get-ChildItem .\logs\*.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } | Remove-Item -Force -ErrorAction SilentlyContinue
