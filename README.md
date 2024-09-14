<div align="center">
<img src="pic/image-20240913225517878.png" alt="image-20240913225517878" style="width:50%;" />
</div>

## Preface

Fully automated qemu simulation script Auto IoT Simulate Tool.

✨ **Broad Support**: Emulates both `ARM` and `MIPS` architectures, covering mainstream IoT devices.

👋 **Easy Setup**: AIOTS designed for beginners, with no need to worry about complex environment.

🎉 **Research-Friendly**: A helpful tool for newcomers to learn and explore IoT vulnerability research.

## Introduction

When I first came into contact with IOT vulnerability mining, the first step was to use `qemu` to simulate the firmware. The simulation process is not difficult, but it is very troublesome. Although there are excellent tools such as `FirmAE`, these tools are often very large and rely on complex environments. , difficult to install, so this script implements the following steps of automated configuration based on previous `IOT` device simulation experience。

1. Identify the file system architecture and identify the big and small ends.
2. Download relevant kernels and images.
3. Create bridges and interfaces on this machine.
4. Package the file system for easy file transfer.
5. Start the virtual machine and use scripts to automate login.
6. Set the `IP` address in the virtual machine.
7. Start transferring file system.
8. Unzip the file system in qemu.
9. Mount `dev` and `proc` in `qemu` and `chroot` the file system.

## Todo List

- [ ] Add testing for `mips` architecture
- [ ] Add script function
- [ ] Add`gdb` debugging testing

## Install dependencies

The steps to install `QEMU` will not be repeated.

- Install `python` library

```bash
pip install lief
pip install wget
```

- Install `bridge-utils` and `uml-utilities` packages

```
sudo apt-get install bridge-utils uml-utilities
```

## Usage

📖The relevant parameters are explained as follows:

- `-f` represents the path of the firmware file system
- `-d` indicates the path where the downloaded data should exist, such as the Linux kernel, etc. If the folder is not changed in the path, it will be created and the downloaded file will be placed in the folder. If the folder already exists, the download operation will not be performed. This is to facilitate the second simulation.
- `-a` indicates the file system `architecture`
- `-e` indicates the `endianness` of the file system

👋The relevant instructions are as follows:

- Local `IP`:`10.10.10.1`
- Virtual machine `IP`:`10.10.10.2`
- `gdb` debugging default port `1234`，`gdb-multiarch` 👉`target remote :1234`

⚙️The relevant usage steps are as follows：

- Clone the repository

```
git clone https://github.com/glkfc/AIOTS.git
cd AIOTS
```

- Use the following command to simulate

```bash
python3 run.py -f ../rootfs -d data
```

- Or specify the relevant `architecture` and `endianness`


```sh
python3 run.py -f ../rootfs -d data -a ARM -e LSB
```

