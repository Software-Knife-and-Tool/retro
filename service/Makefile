#
# moderne display service
#
all:
	echo "install: install (needs root)"

install:
	cp pigpiod.service /etc/systemd/system
	systemctl start pigpiod
	systemctl enable pigpiod

