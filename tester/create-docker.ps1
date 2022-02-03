param ($testPath, $iniPath, $containerName="tmp")

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
  Copy-Item -Path $testPath\* -Destination $tempFolder\tests\src -Include ('*.cpp', '*.cc', '*.c', '*.h', '*.hpp')

  New-Item -Path $tempFolder\tests -Name 'dat' -ItemType 'directory'
  Copy-Item -Path $testPath\* -Destination $tempFolder\tests\dat -Exclude ('*.cpp', '*.cc', '*.c', '*.h', '*.hpp')

  Copy-Item -Path $iniPath -Destination $tempFolder\tests\config.ini

  $location = Get-Location
  try {
    Set-Location -Path $tempFolder

    docker build -t $containerName .
  }
  finally {
    Set-Location $location
  }
}
finally {
  Remove-Item -Path $tempFolder -Recurse
}
