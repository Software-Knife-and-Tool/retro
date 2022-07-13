#
# retro development
#
.PHONY: install blank unblank retro app

BASE = /home/putnamjm

PACKAGES = $(BASE)/retro/modules:$(BASE)/.local/lib/python3.9/site-packages

install:
	@sudo apt install -y python3-pip pigpiod
	@pip3 install pigpio dbus-python
	@sudo make -C ../service install

unblank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 lib/unblank.py

blank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 lib/blank.py

retro:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 lib/retro.py

app:
	@env "PYTHONPATH=$(PACKAGES)" python3 lib/app.py
