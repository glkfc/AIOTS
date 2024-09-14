#!/usr/bin/expect -f


set qemu_command [lindex $argv 0]
set args [lrange $argv 1 end-1]
set data_name [lindex $argv end]

eval spawn $qemu_command $args

set timeout 120

expect "login: "
send "root\r"

expect "Password: "
send "root\r"

sleep 2

expect "~# "
send "ifconfig eth0 10.10.10.2/24\r"

sleep 2

expect "~# "
send "wget 10.10.10.1:8081/$data_name/rootfs.tar; wget 10.10.10.1:8081/script/a.sh; chmod 777 a.sh; ./a.sh\r"

interact
