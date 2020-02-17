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
    [switch] $tags = $false,
    [string] $python_path = ""
)

$python_path="C:\Users\mandu\source\virtualenvs\testscript\Scripts\python.exe"


if ($tags) {
    & "ctags" "--kinds-python=+cfm-vxiIzl" "--maxdepth=1" "-R" "src"
}



if ($tags) {
    & "ctags" "--kinds-python=+cfm-vxiIzl" "--maxdepth=1" "-R" "src"
}

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
    & $python_path "-m" "pytest" "-s" "-vv" "--tb=long" "--color=yes" "src"
    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
    
}

Function LintFile
{
     Param (
        [Parameter(mandatory=$true)]
        [string]$file
        )

    Write-Host  "-----------------------------------------------" -ForegroundColor white -BackgroundColor black
    Write-Host "Linting file  $file" -BackgroundColor Blue -ForegroundColor Yellow
    # mypy
    Write-Output "Running mypy"
    & $python_path "-m" "mypy" "--ignore-missing-imports" $file

    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
    # pyflakes
    Write-Output "Running pyflakes"
    & $python_path "-m" "pyflakes" $file
    if ($LASTEXITCODE -ne 0) {
        exit 1
    }

    Write-Output "No errors found in file   $file"


    # pylint
    Write-Output "Running pylint"
    & $python_path "-m" "pylint" "--output-format=colorized" $file

    # pydocstyle
    Write-Output "Running pycodestyle"
    & $python_path "-m" "pycodestyle" $file

    # pycodestyle
    Write-Output "Running pydocstyle"
    & $python_path "-m" "pydocstyle"  $file

    # flake8
    Write-Output "Running flake8"
    & $python_path "-m" "flake8"  $file

    # flake8
    Write-Output "Running flake8"
    & $python_path "-m" "bandit"  $file
    
    Write-Output "please fix your pylint, code&doc style and bandit  $file"

    Write-Host  "===============================================" -ForegroundColor white -BackgroundColor black


	
}

$lint_files = New-Object System.Collections.ArrayList
$lint_files.Add(".\src\infrastructure.py")
$lint_files.Add(".\src\infrastructure_test.py")
$lint_files.Add(".\src\library.py")
$lint_files.Add(".\src\library_test.py")
$lint_files.Add(".\src\runner.py")
$lint_files.Add(".\src\runner_test.py")
$lint_files.Add(".\src\evaluators.py")
$lint_files.Add(".\src\evaluators_test.py")


if ($lint) {
    foreach($file in $lint_files) {
        LintFile($file)
    }
    
}

if ($?) {
    Write-Host ""
    Write-Host ""
    Write-Host "SUCCESS Congratulations you da best ;)" -ForegroundColor 'Green'
    Write-Host ""
    Write-Host ""
    Exit 0
}
Exit 1
