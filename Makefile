INSTALL=/usr/bin/
analyze:
	pip install pep257 pycodestyle
	pycodestyle eltorito.py
	pep257 eltorito.py

install:
	cp eltorito.py $(INSTALL)/eltorito
