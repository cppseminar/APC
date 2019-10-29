# Script for testing quality, managing python environment
# and builds on CI

param (
    [Parameter(Mandatory = $false)][string] $build,
    [switch] $all = $false,
    [switch] $install = $false,
    [switch] $update = $false,
    [switch] $force = $false,
    [switch] $test = $false,
    [string] $python_path = ""
)


if (!$python_path) {
    if (!$env:VIRTUAL_ENV -and !$force) {
        Write-Error "Please activate virtualenv for python, or set python_path inside this script"
        Exit 1
    }
    else {
        $python_path = get-command python.exe -ErrorAction stop |  ForEach-Object {$_.Path}
    }
}

if ($install) {
    & $python_path "-m" "pip" "install" "-r" "requirements.txt"
    if ($?) {
        Write-Error "Installation failed"
        Exit 1
    }
}

if ($update) {
    $files = Get-Content .\requirements.txt 
    & $python_path "-m" "pip" "install" "--upgrade" pip $files
}

if ($test) {
    & $python_path "-m" "pytest"
}

exit $?
