#!/bin/bash

set -e

while read -r line;
do

	echo "Applying file $line to iptables"
	iptables-restore --ipv4 --noflush /etc/iptables-nft4/"$line"


done < <(  ls -B1  /etc/iptables-nft4/ )

exit 0
