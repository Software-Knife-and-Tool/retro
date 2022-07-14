#
# retro development
#
.PHONY: install blank unblank retro app ufw

BASE = ../
LIB = ./retro-lib
PACKAGES = $(BASE)/retro/modules:$(BASE)/.local/lib/python3.9/site-packages

install:
	@sudo apt install -y python3-pip pigpiod
	@pip3 install bottle jyserver pigpio
	@sudo make -C ./service install

ufw:
	@sudo apt install -y ufw
	@sudo ufw allow ssh
	@sudo ufw allow 8080
	@sudo ufw allow 443
	@sudo ufw enable
	@sudo ufw status	

unblank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 $(LIB)/unblank.py

blank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 $(LIB)/blank.py

retro:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 $(LIB)/retro.py

app:
	@env "PYTHONPATH=$(PACKAGES)" python3 $(LIB)/app.py
