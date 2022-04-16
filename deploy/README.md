# What is this?
This folder contains tools to deploy  information about setting up APC portal fromninfrastructure perspective.

It contains infrastructure deployment scripts written in **bicep** and vm setup written in **ansible**.

Our architecture currently only runs in Azure, but we are slowly making transition to make it cloud provider indempendent.

# How to set this up
1. This folder contains automatic infrastructure deployment (bicep), but not everything. Missing parts are:
   - Azure cosmos db
   - Azure container registry
   - Azure storage account
2. Use ansible to set up logging and ~~management~~ servers
3. Build and deploy containers (source code is outside this folder) to kubernetes
4. Create custom os image for scale set (testers)
   - Run init script for testers (found outside in services dir)
   - Use ansible to setup logging client for this image
   - Set this image to virtual machine scale set
5. Setup some necessary environment variables, that are outside of this overview

# Networks
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
