#!/usr/bin/expect -f

set qemu_command [lindex $argv 0]
set args [lrange $argv 1 end]


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
send "mount -o bind /dev ./rootfs/dev;mount -t proc /proc ./rootfs/proc;chroot ./rootfs sh\r"

interact
