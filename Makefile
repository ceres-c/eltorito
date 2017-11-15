SRC=eltorito.py
INSTALL=/usr/bin/
analyze:
	pip install pep257 pycodestyle
	pycodestyle $(SRC)
	pep257 $(SRC)

install:
	cp eltorito.py $(INSTALL)/eltorito
