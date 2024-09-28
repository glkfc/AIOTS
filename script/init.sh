#!/usr/bin/expect -f


set qemu_command [lindex $argv 0]
set args [lrange $argv 1 end-3]
set flag [lindex $argv end-2]
set data_name [lindex $argv end-1]
set script_name [lindex $argv end]

eval spawn $qemu_command $args

set timeout 240

expect "login: "
send "root\r"

expect "Password: "
send "root\r"

sleep 2

expect "~# "
send "ifconfig eth0 10.10.10.2/24\r"

sleep 2

expect "~# "
switch  $flag {
    "0" {
    	send "wget 10.10.10.1:8081/$data_name/rootfs.tar; tar -xvf rootfs.tar ;wget 10.10.10.1:8081/script/a.sh; chmod 777 a.sh; ./a.sh\r"
    }
    "1" {
    	send "mount -o bind /dev ./rootfs/dev;mount -t proc /proc ./rootfs/proc;chroot ./rootfs sh\r"
    }
        
    "2" {
        send "wget 10.10.10.1:8081/$data_name/rootfs.tar; wget 10.10.10.1:8081/script/a.sh; wget 10.10.10.1:8081/$script_name; tar -xvf rootfs.tar ;mv $script_name ./rootfs; chmod 777 a.sh; ./a.sh\r "
        sleep 5
        expect "# "
        send "chmod 777 $script_name; ./$script_name\r"
    }

    "3" {
        send "wget 10.10.10.1:8081/$script_name; mv $script_name ./rootfs; mount -o bind /dev ./rootfs/dev;mount -t proc /proc ./rootfs/proc;chroot ./rootfs sh\r"
        sleep 2
        expect "# "
        send " chmod 777 $script_name; ./$script_name\r"
    
    }

    default {
        send_user "Invalid flag value: $flag\r"
        exit 1
    }
}
interact
