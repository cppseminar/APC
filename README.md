# Apc portal

|     App name    |                                                 Status                                                                       |
| ----------------| ---------------------------------------------------------------------------------------------------------------------------- |
| Prod frontend   | ![Production - publish frontend](https://github.com/cppseminar/APC/workflows/Production%20-%20publish%20frontend/badge.svg)  |
| Prod functions  | ![Production - publish api](https://github.com/cppseminar/APC/workflows/Production%20-%20publish%20api/badge.svg)            |
| Dev frontend    | ![Development - publish frontend](https://github.com/cppseminar/APC/workflows/Development%20-%20publish%20frontend/badge.svg)|
| Dev functions   | ![Development - publish api](https://github.com/cppseminar/APC/workflows/Development%20-%20publish%20api/badge.svg)          |

## Directory structure

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
