# Script for testing quality, managing python environment
# and builds on CI

param (
    [Parameter(Mandatory = $false)][string] $build,
    [switch] $all = $false,
    [switch] $install = $true,
    [switch] $update = $false,
    [switch] $force = $false,
    [switch] $test = $false,
    [string] $python_path = ""
)

$python_run = ''

if ((Get-Command "pipenv" -ErrorAction SilentlyContinue) -eq $null) {
    if (!$python_path) {
        if (!$env:VIRTUAL_ENV -and !$force) {
            Write-Error "Please activate virtualenv for python, or set python_path inside this script"
            Exit 1
        }
        else {
            $python_path = get-command python.exe -ErrorAction stop |  ForEach-Object {$_.Path}
        }

    }
    $python_run = '"' + $python_path + '" -m '
}

$command = $python_run

if ($install) {
    $command += "pipenv install"
}

if ($update) {
    & $python_run "pipenv" "update"
}

if ($test) {
    & $python_run "pytest"
}

Invoke-Expression "& $command"

if ($?) {
    Exit 0
}
Exit 1
