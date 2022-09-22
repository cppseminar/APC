# Building tester docker

Building tester docker images is quite easy. You just need to run script `create-docker.ps1` from this directory with required parameters

   * `-iniPath` path to `config.ini` file
   * `-testPath` bath to folder with tests

For example you can run `.\create-docker.ps1 -iniPath .\example\configs\hello-world\config.ini -testPath .\example\tests\hello-world\`. This will create docker image with required tests. This will create image called `tmp`. You can use another name with parameter `-containerName`.

## Running it locally

You need to add two volume mapping. Like this

`docker run -v 'C:\path\to\submission\:/app/submission' -v 'C:\path\to\output\:/app/output' -it tmp`
