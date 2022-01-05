eltorito
===

A python library to extract 'el torito' images from bootable cd images/isos

# usage

clone the repository and
```python
import eltorito as et

INFILE = './distr.iso'
OUTFILE = './out.img'

with open(INFILE, 'rb') as infile_handle, open(OUTFILE, 'wb') as outfile_handle:
	extracted = et.extract(infile_handle)
	print(extracted['info']) # Image information
	outfile_handle.write(extracted['data'].getbuffer())
```
