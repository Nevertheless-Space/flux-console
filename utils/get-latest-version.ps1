$Uri = "https://github.com/Nevertheless-Space/flux-console/releases/latest"
$WebResponse = Invoke-WebRequest -Method HEAD -Uri $Uri
$version = $WebResponse.BaseResponse.ResponseUri.AbsoluteUri.Split("/")[-1]

Get-ChildItem -Path  '.\' -Recurse -exclude "get-latest-version.ps1" | Remove-Item -Force -Recurse

$source = "https://github.com/Nevertheless-Space/flux-console/releases/download/${version}/ntl-flux-console-windows-${version}.zip"
$destination = ".\ntl-flux-console-windows-${version}.zip"
Invoke-RestMethod -Uri $source -OutFile $destination

Expand-Archive ".\ntl-flux-console-windows-${version}.zip" -DestinationPath ".\"
Remove-Item ".\ntl-flux-console-windows-${version}.zip" -Force