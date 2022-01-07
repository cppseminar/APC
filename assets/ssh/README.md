# Limited ssh server
This folder contains setup for ssh with limited functionality.

This is achieved through use of linux kernel namespaces.

Required software:
- s6



```
/usr/sbin/sshd -D -f sshd_config

```
