# Apc portal

|     App name    |                                                 Status                                                                       |
| ----------------| ---------------------------------------------------------------------------------------------------------------------------- |
| Prod frontend   | ![Production - publish frontend](https://github.com/cppseminar/APC/workflows/Production%20-%20publish%20frontend/badge.svg)  |
| Prod functions  | ![Production - publish api](https://github.com/cppseminar/APC/workflows/Production%20-%20publish%20api/badge.svg)            |
| Dev frontend    | ![Development - publish frontend](https://github.com/cppseminar/APC/workflows/Development%20-%20publish%20frontend/badge.svg)|
| Dev functions   | ![Development - publish api](https://github.com/cppseminar/APC/workflows/Development%20-%20publish%20api/badge.svg)          |

This repository contains source code for APC portal 1&2.  This portal is used by
students and teachers to assign, submit and test programming homeworks.

Reason for implementing our own solution was having ability to run different
tests on submission by students and running even more tests by teacher later.

## Architecture
One of our primary targets was to create system with low maintenance costs. For
this reason we used Azure serverless solutions as much as possible.

This project consists of these logical parts:
 - Frontend - Javascript (React) application (hosted on Azure BLOB Storage)
 - Backend - Azure functions (on consumption plan)
 - Database - We choose Azure Cosmos DB with Mongo API (can switch to real Mongo)
 - Tester - Python commmand line script able to compile (gcc + msvc) and test
            source codes
 - API Mangement - Azure gateway for our backend, used to handle Google Auth and
                   limit request rate
 - Virtual machine - Azure VM able to run docker orchestrator.
 - Go services - Services to run Tester scripts and communicate with our Backend

Because test and submissions are usually happening more often when submission
deadline approaches, vms are automatically turned off and deallocated by azure
orchestration functions (via automation account).  These are then turned on
automatically, when test request is queued.

Communication between our backend and Go services running in VM is signed via
JWT, due to not having dns names for testers (it could be done, but who would
do it 😀)


### Directory structure
Here is basic directory structure for this project, some of these might have
their own READMEs.
```
testscripts/
│ .vscode/          Basic settings fo vs code
│ assets/           Scripts, configs etc. basically things that don't belong anywhere
│ frontend/         React web app - frontend for our portal
│ functions/        Azure functions - REST api backend
│ functions_test/   Tests for azure functions
│ services/         Golang daemons for VMs, where we run tests
│ tester/           Python scripts used for black box testing C++ programs

```
