analyze:
	pip install pep257 pycodestyle
	pycodestyle eltorito.py
	pep257 eltorito.py

install:
	install -Dm755 eltorito.py $(DESTDIR)/usr/bin/eltorito
