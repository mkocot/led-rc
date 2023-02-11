# How to use IR Receiver on OrangePi PC
## Simple as 1-2-3
1. Load module `sudo modprobe sunxi_cir`
2. Enable nec protocol `echo +nec | sudo tee /sys/class/rc/rc0/protocols`
3. Load keytables `ir-keytable -w korbox.toml`
## Tips&Tricks:
* You can add `sunxi_cir` to /etc/modprobe.d/
### Detecting RC codes
1. Run `ir-keytable -t` and note somewhere `scancode` detected after button press
2. Put scancodes to toml file
3. Porfit?
