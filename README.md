echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", ATTRS{serial}=="FT4TFVCO", MODE="0666", ATTR{latency_timer}="1", SYMLINK+="USBfollower", RUN+="/bin/sh -c '\''echo 1 > /sys/bus/usb-serial/devices/%k/latency_timer'\''"' | sudo tee /etc/udev/rules.d/99-usb-follower.rules
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", ATTRS{serial}=="FTA7O35H", MODE="0666", ATTR{latency_timer}="1", SYMLINK+="USBleader", RUN+="/bin/sh -c '\''echo 1 > /sys/bus/usb-serial/devices/%k/latency_timer'\''"' | sudo tee /etc/udev/rules.d/99-usb-leader.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
