chmod -R 777 rootfs
mount -o bind /dev ./rootfs/dev
mount -t proc /proc ./rootfs/proc
chroot ./rootfs sh
