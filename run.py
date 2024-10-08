import argparse
import lief
import os
import wget
import subprocess
import requests
import http.server
import socketserver
import threading

url_dict = {
    "mips": ['https://people.debian.org/~aurel32/qemu/mips/vmlinux-3.2.0-4-4kc-malta',
             'https://people.debian.org/~aurel32/qemu/mips/debian_wheezy_mips_standard.qcow2'],
    "mipsel": ['https://people.debian.org/~aurel32/qemu/mipsel/vmlinux-3.2.0-4-4kc-malta',
               'https://people.debian.org/~aurel32/qemu/mipsel/debian_wheezy_mipsel_standard.qcow2'],
    "arm": ['https://people.debian.org/~aurel32/qemu/armhf/vmlinuz-3.2.0-4-vexpress',
              'https://people.debian.org/~aurel32/qemu/armhf/initrd.img-3.2.0-4-vexpress',
              'https://people.debian.org/~aurel32/qemu/armhf/debian_wheezy_armhf_standard.qcow2']
}

def find_file(filename, search_path):
    """find the file """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def create_tap_interface(tap_name, host_ip):
    """ Create and configure the TAP interface """
    try:
        subprocess.run(['sudo', 'tunctl', '-t', tap_name, '-u', os.getlogin()], check=True)
        subprocess.run(['sudo', 'ip', 'addr', 'add', host_ip, 'dev', tap_name], check=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', tap_name, 'up'], check=True)
        print(f"[+]TAP interface {tap_name} was created and configured successfully")
        print(f"[+]Host IP:{host_ip}")
    except subprocess.CalledProcessError as e:
        print(f"[-]Failed to create TAP interface: {e}")


def configure_ip_forwarding():
    """ Enable IP forwarding for the host """
    try:
        subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
        print("[+]IP forwarding is enabled")
    except subprocess.CalledProcessError as e:
        print(f"[-]Failed to enable IP forwarding: {e}")


def print_art():
    art = """
    		 $$$$$$\  $$$$$$\  $$$$$$\ $$$$$$$$\  $$$$$$\  
    		$$  __$$\ \_$$  _|$$  __$$\\__$$  __|$$  __$$\ 
    		$$ /  $$ |  $$ |  $$ /  $$ |  $$ |   $$ /  \__|
    		$$$$$$$$ |  $$ |  $$ |  $$ |  $$ |   \$$$$$$\  
    		$$  __$$ |  $$ |  $$ |  $$ |  $$ |    \____$$\ 
    		$$ |  $$ |  $$ |  $$ |  $$ |  $$ |   $$\   $$ |
    		$$ |  $$ |$$$$$$\  $$$$$$  |  $$ |   \$$$$$$  |
    		\__|  \__|\______| \______/   \__|    \______/ 
    		           Auto IoT Simulate Tool
    """

    print(art)


def download_data(data_path, architecture, endianness):
    """Download kernel and disk files"""
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"[+]Folder {data_path} has been created")
        if architecture == "MIPS":
            if endianness == "MSB":
                wget.download(url_dict["mips"][0], f"./{data_path}/vmlinux")
                print("[+]vmlinux done!")
                wget.download(url_dict["mips"][1], f"./{data_path}/debian.qcow2")
                print("[+]deian.qcow2 done!")
            else:
                wget.download(url_dict["mipsel"][0], f"./{data_path}/vmlinux")
                print("[+]vmlinux done!")
                wget.download(url_dict["mipsel"][1], f"./{data_path}/debian.qcow2")
                print("[+]deian.qcow2 done!")
        else:
            wget.download(url_dict["arm"][0], f"./{data_path}/vmlinux")
            print(" [+]vmlinux done!")
            wget.download(url_dict["arm"][1], f"./{data_path}/initrd.img")
            print(" [+]initrd.img done!")
            wget.download(url_dict["arm"][2], f"./{data_path}/debian.qcow2")
            print(" [+]deian.qcow2 done!")
            os.system(f"qemu-img resize ./{data}/debian.qcow2 32G")
        return 0
    else:
        print(f"[-]Folder {data_path} already exists")
        return 1


parser = argparse.ArgumentParser()
parser.add_argument('--filesystem', '-f', type=str, help="the path of filesystem", required=True)
parser.add_argument('--data', '-d', type=str, help="the path of data to save", required=True)
parser.add_argument('--script', '-s', type=str,
                    help="the path of script, If you want to execute certain commands after startup, you can use the -s parameter and write the commands you want to execute in the script.")
parser.add_argument('--arch', '-a', type=str, help="the arch of filesystem MIPS/ARM")
parser.add_argument('--endianness', '-e', type=str, help="the endianness of filesystem LSB/MSB")
args = parser.parse_args()

data = args.data
filesystem = args.filesystem

qemu_commond = {
    "MIPS": {
        "MSB": f"qemu-system-mips -M malta -kernel ./{data}/vmlinux -hda ./{data}/debian.qcow2 -append \"root=/dev/sda1 console=tty0\" -net nic -net tap,ifname=tap0 -s -nographic",
        "LSB": f"qemu-system-mipsel -M malta -kernel ./{data}/vmlinux -hda ./{data}/debian.qcow2 -append \"root=/dev/sda1 console=tty0\" -net nic -net tap,ifname=tap0 -s -nographic"
    },
    "ARM": {
        "LSB": f"qemu-system-arm -M vexpress-a9 -kernel ./{data}/vmlinux -initrd ./{data}/initrd.img -drive if=sd,file=./{data}/debian.qcow2 -append \"root=/dev/mmcblk0p2 console=tty0\" -net nic -net tap,ifname=tap0 -s -nographic -smp 4",
        "MSB": f"qemu-system-arm -M vexpress-a9 -kernel ./{data}/vmlinux -initrd ./{data}/initrd.img -drive if=sd,file=./{data}/debian.qcow2 -append \"root=/dev/mmcblk0p2 console=tty0\" -net nic -net tap,ifname=tap0 -s -nographic -smp 4"

    }
}


os.system("sudo chmod +x ./script/*")
print_art()
print(f"[+]File path: {args.filesystem}")




if args.arch and args.endianness:
    architecture = args.arch
    endianness = args.endianness
else:
    busybox_path = find_file('busybox', filesystem)
    if busybox_path:
        print(f"[+]Busybox path：{busybox_path}")
    else:
        print(f"[-]File not found, please enter the schema manually, parameter -a and -e")
    binary = lief.parse(busybox_path)
    architecture = str(binary.header.machine_type).split(".")[-1]  # arch  lief._lief.ELF.ARCH.ARM
    endianness = str(binary.header.identity_data).split(".")[-1]  # endianness  lief._lief.ELF.ELF_DATA.LSB

print(f"[+]arch: {architecture}")
print(f"[+]endianness: {endianness}")

flag = download_data(args.data, architecture, endianness)

create_tap_interface("tap0", "10.10.10.1/24")
configure_ip_forwarding()

if args.script and flag == 0:
    flag = 2  # 表示第一次且有脚本
elif args.script and flag == 1:
    flag = 3  # 表示不是第一次且有脚本

"""If the folder does not exist, you need to configure all procedures, including the file system"""
os.system(f"cp -r {filesystem} ./rootfs")
os.system(f"tar -cf ./{args.data}/rootfs.tar rootfs")
os.system(f"sudo rm -rf rootfs")


PORT = 8081
Handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()

print(f"[+]Serving HTTP on port {PORT} in the background...")
print(f"[+]Start qemu")
commond = qemu_commond[architecture][endianness]
print(flag, args.data, args.script)
os.system(f"./script/init.sh {commond} {flag} {args.data} {args.script}") # 改

httpd.shutdown()
httpd.server_close()
