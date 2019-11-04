# Script for testing quality, managing python environment
# and builds on CI

param (
    [Parameter(Mandatory = $false)][string] $build,
    [switch] $all = $false,
    [switch] $install = $false,
    [switch] $update = $false,
    [switch] $force = $false,
    [switch] $test = $false,
    [switch] $lint = $false,
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
}

if ($update) {
    $files = Get-Content .\requirements.txt 
    & $python_path "-m" "pip" "install" "--upgrade" pip $files
}

if ($test) {
    & $python_path "-m" "pytest"
}

Function Lint-File
{
     Param (
        [Parameter(mandatory=$true)]
        [string]$file
        )

    Write-Output "Linting file " + $file
    Write-Output "Running pylint"
    & $python_path "-m" "pylint" $file

    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
    # mypy
    Write-Output "Running mypy"
    & $python_path "-m" "mypy" $file

    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
    Write-Output "Running pyflakes"
    & $python_path "-m" "pyflakes" $file
    if ($LASTEXITCODE -ne 0) {
        exit 1
    }

    Write-Output "No errors found in file   $file"
}

if ($lint) {
    Lint-File(".\src\infrastructure.py")
}

if ($?) {
    Exit 0
}
Exit 1
