#
#
#
.PHONY: install blank run

SRCS = ncs31x gra-afch

BASE = /home/putnamjm

PACKAGES = $(BASE)/moderne/modules:$(BASE)/.local/lib/python3.9/site-packages

install:
	@pip3 install pigpio python-pigpio python3-pigpio dbus-python

unblank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 unblank.py

blank:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 blank.py

moderne:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 moderne.py

