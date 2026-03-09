$ErrorActionPreference = "Stop"

# 默认推测的 Cloudflare Pages 域名，如果你的项目名不同，请稍后自行修改
$ProjectUrl = "https://tool.vanzor.com/mirror-switch.zip" 

$TempDir = Join-Path $env:TEMP "mirror-switch-install"
$ZipFile = Join-Path $env:TEMP "mirror-switch.zip"
$ExtractDir = Join-Path $env:TEMP "mirror-switch-extracted"

Write-Host ">>> 开始下载 Mirror Switch..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $ProjectUrl -OutFile $ZipFile

if (Test-Path $ExtractDir) {
    Remove-Item -Recurse -Force $ExtractDir
}

Write-Host ">>> 解压中..." -ForegroundColor Cyan
Expand-Archive -Path $ZipFile -DestinationPath $ExtractDir -Force

#因为我们打包的 ZIP 没有外层目录，文件直接在根目录
$ActualDir = $ExtractDir

Write-Host ">>> 准备运行环境（使用 阿里源 加速）..." -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host ">>> 检测到 uv，正在通过当前环境 uv 运行..." -ForegroundColor Green
    $UvExe = "uv"
} else {
    Write-Host ">>> 未检测到 uv，正在极速拉取免安装运行环境..." -ForegroundColor Yellow
    
    $UvFile = "uv-x86_64-pc-windows-msvc.zip"
    $UvUrl = "https://tool.vanzor.com/bin/$UvFile"
    $UvTempZip = Join-Path $env:TEMP $UvFile
    
    Write-Host ">>> 正在同步独立运行环境..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $UvUrl -OutFile $UvTempZip
    
    $UvExtractDir = Join-Path $env:TEMP "uv-bin-extracted"
    if (Test-Path $UvExtractDir) { Remove-Item -Recurse -Force $UvExtractDir }
    Expand-Archive -Path $UvTempZip -DestinationPath $UvExtractDir -Force
    
    $UvExe = Join-Path $UvExtractDir "uv-x86_64-pc-windows-msvc\uv.exe"
}

Set-Location $ActualDir
& $UvExe run --python 3.12 --index-url https://mirrors.aliyun.com/pypi/simple/ python -m mirror_switch.main

Write-Host ">>> 运行结束，清理临时文件..." -ForegroundColor Cyan
Set-Location $env:TEMP
Remove-Item -Recurse -Force $ExtractDir
Remove-Item -Force $ZipFile
Write-Host ">>> 完成" -ForegroundColor Green
