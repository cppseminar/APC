# Building tester docker

Building tester docker images is quite easy. You just need to run script `create-docker.ps1` from this directory with required parameters

   * `-TestPath` path to folder with tests
   * `-Mode` test mode, `build` will build the submission, `copy` will just copy it to tests and build that together (default is `build`)
   * `-ShowTestsToStudents` if specified test output will be visible to students, default is no visibility
   * `-ContainerName` name of container (default is last folder name from `-TestPath`)

For example you can run `.\create-docker.ps1 -testPath .\example\tests\hello-world\`. This will create docker image with required tests. This will create image called `hello-world`. You can use another name with parameter `-ContainerName`.

## Running it locally

You need to add two volume mapping. Like this

`docker run -v 'C:\path\to\submission\:/app/submission' -v 'C:\path\to\output\:/app/output' -it hello-world`
