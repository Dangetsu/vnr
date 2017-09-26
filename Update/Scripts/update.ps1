# update.ps1
# 11/7/2013 jichi
#
# Run:
# powershell -NoProfile -ExecutionPolicy unrestricted -Command "& {./update.ps1}"

$PWD = $(Get-Location)

$batchFile = Join-Path $PWD "update.cmd"
if (Test-Path $batchFile) {
  #Start-Process "cmd.exe" -ArgumentList "/c `"$batchFile`"" -Wait -WindowStyle Hidden
  Start-Process "cmd.exe" -ArgumentList "/c `"$batchFile`"" -Wait
}

# EOF
