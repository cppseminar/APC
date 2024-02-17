param ($TestPath, [ValidateSet('build','copy')]$Mode='build', [switch]$ShowTestsToStudents, [String]$ContainerName)

if (-Not (Test-Path $TestPath)) {
    throw "TestPath does not exists!"
}

if (-Not ((Get-Item $TestPath) -is [System.IO.DirectoryInfo])) {
  throw "TestPath must be a directory!"
}

if ($ContainerName.Length -eq 0) {
  Write-Output "Container name not given using TestPath as container name."
  $ContainerName = Split-Path $TestPath -Leaf
}

Write-Output "TestPath: $TestPath"
Write-Output "Mode: $Mode"
Write-Output "ShowTestsToStudents: $ShowTestsToStudents"
Write-Output "Container name: $ContainerName"

function New-TemporaryDirectory {
  $parent = [System.IO.Path]::GetTempPath()
  [string] $name = [System.Guid]::NewGuid()
  New-Item -ItemType Directory -Path (Join-Path $parent $name)
}

$tempFolder = New-TemporaryDirectory

try {
  Copy-Item -Path '.\*' -Destination $tempFolder -Recurse -Exclude 'example'
  New-Item -Path $tempFolder -Name 'tests' -ItemType 'directory'

  <# We include, exclude files because we may want to build it from single
  folder, in that case it make sense to split, hopefully noone will try
  to use .cpp file as data...
  #>
  New-Item -Path $tempFolder\tests -Name 'src' -ItemType 'directory'
  Copy-Item -Path $TestPath\* -Destination $tempFolder\tests\src -Include ('*.cpp', '*.cc', '*.c', '*.h', '*.hpp')

  New-Item -Path $tempFolder\tests -Name 'dat' -ItemType 'directory'
  Copy-Item -Path $TestPath\* -Destination $tempFolder\tests\dat -Exclude ('*.cpp', '*.cc', '*.c', '*.h', '*.hpp')

  $location = Get-Location
  try {
    Set-Location -Path $tempFolder

    $ShowTestsToStudentsInt = (&{If($ShowTestsToStudents) {1} Else {0}})

    $dockerParams = @(
      '--build-arg', "TEST_MODE_ARG=$Mode",
      '--build-arg', "SHOW_RESULTS_TO_STUDENTS_ARG=$ShowTestsToStudentsInt",
      '--tag', $ContainerName
    )
    & docker build @dockerParams .
  }
  finally {
    Set-Location $location
  }
}
finally {
  <#Remove-Item -Path $tempFolder -Recurse#>
}
