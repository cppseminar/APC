# What is this?

This folder contains tools to deploy information about setting up APC portal from infrastructure perspective.

It contains infrastructure deployment scripts written in **bicep** and **kubernetes** helm charts.

Our architecture currently only runs in Azure, but we are slowly making transition to make it cloud provider independent.

## How to set this up

1. This folder contains automatic infrastructure deployment (bicep), but not everything. Missing parts are:
   - Azure container registry
   - Azure storage account
   Those are expected to be created outside of this deployment.
2. Build containers (source code is outside this folder) for kubernetes
3. Setup some necessary environment variables, that are outside of this overview, but are in `deploy-portal.ps1` script.

## How to run it

Switch to desired azure subscription and run script `./deploy-portal.ps1`. All parameters and usage notes are in the beginning of that file. Most of it will be automated, if your storage account and container registry are already set up in resource group `apc-data`.

## Networks

Due to our use of VPN tunnels and internal static ips in subnets, it is necesssary to keep these in mind:

```
| Subnet name               | Subnet ip    |
|---------------------------+--------------|
| Development               | 10.12.0.0/14 |
| Production                | 10.8.0.0/14  |
| Management (logging)      | 10.4.0.0/14  |
| Reserved                  | 10.3.0.0/16  |
| Reserved                  | 10.2.0.0/16  |
| Reserved for user devices | 10.1.0.0/16  |
| Reserved                  | 10.3.0.0/16  |
```

Basic layout looks like this, note that there is only one management stack connected to both dev and prod. That is the reason why we use VPN tunnels and not peering for communication.

```
       +----------------------------------------------------+
       |              Production / dev Subnet               |
       |                                                    |
    +--+---+        +----------+       +---------------+    |
    |Public|        |Kubernetes|       |Virtual machine|    |
    |  ip  |<------>| cluster  |------>|   scale set   |    |
    +--+---+        +----------+       +---------------+    |
       |                                                    |
       |                                                    |
       |                       +-------+                    |
       |                       |Access-|                    |
       |                       | point |                    |
       |                       |  VM   |                    |
       |                       +-------+                    |
       |                           |                        |
       |                           |                        |
       +---------------------------+------------------------+
                                   |
                                   | VPN
                                  / tunnel
                                  |
                                  |
                                  v
                              +------+
                              |Public|
                              |  ip  |
                +-------------+------+---------------+
                |        Management (logging)        |
                |              subnet                |
                |                                    |
                |                                    |
                +------------------------------------+
```
