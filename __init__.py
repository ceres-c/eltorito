#!/usr/bin/python3

'''
Extract El Torito image from a bootable CD (or image).

Taken from https://github.com/enckse/eltorito and modified by ceres-c
to return a BufferIO object to avoid saving data on disk.

Reference:
https://userpages.uni-koblenz.de/~krienke/ftp/noarch/geteltorito/
https://en.wikipedia.org/wiki/El_Torito_(CD-ROM_standard)
'''
from io import BytesIO
import struct

V_SECTOR_SIZE = 512
SECTOR_SIZE = 2048

def _get_sector(file_handle, number, count):
	'''Get a sector.'''
	file_handle.seek(number * SECTOR_SIZE, 0)
	sector = file_handle.read(V_SECTOR_SIZE * count)
	if len(sector) != V_SECTOR_SIZE * count:
		raise ValueError('Invalid sector read')
	return sector

def extract(file_handle):
	'''Extract an image.

	Arguments:
	file_handle (file-like object) -- the input image
	Return:
	a dictionary:
	{
		info: {dictionary of image information},
		data: <BufferIO object with image data>
	}
	'''
	info = {}

	sector = _get_sector(file_handle, 17, 1)
	# we only need the first section of this segment
	segment = struct.unpack('<B5sB32s32sL', sector[0:75])
	# boot = segment[0] # Not returned
	info['iso'] = segment[1].decode('ascii')
	info['vers'] = segment[2]
	spec = segment[3].decode('ascii').strip()
	info['spec'] = ''.join([x for x in spec if (x >= 'A' and x <= 'Z') or x == ' '])
	# 4 is unused
	info['partition'] = segment[5]

	if info['iso'] != 'CD001' or info['spec'].strip() != 'EL TORITO SPECIFICATION':
		raise ValueError('This is not a bootable cd-image')

	sector = _get_sector(file_handle, info['partition'], 1)
	segment = struct.unpack('<BBH24sHBB', sector[0:32])
	header = segment[0]
	info['platform'] = segment[1]
	# skip 2
	info['manufacturer'] = segment[3].decode('ascii')
	# skip 4
	five = segment[5]
	aa = segment[6]
	if header != 1 or five != 0x55 or aa != 0xaa:
		raise ValueError('Invalid validation entry')

	info['platform_string'] = 'unknown'
	if info['platform'] == 0:
		info['platform_string'] = 'x86'
	elif info['platform'] == 1:
		info['platform_string'] = 'PowerPC'
	elif info['platform'] == 2:
		info['platform_string'] = 'Mac'

	segment = struct.unpack('<BBHBBHLB', sector[32:45])
	boot = segment[0]
	info['media'] = segment[1]
	load = segment[2]
	sys = segment[3]
	# skip 4
	cnt = segment[5]
	info['start'] = segment[6]
	# skip 7

	if boot != 0x88:
		raise ValueError('Boot indicator is not 0x88, not bootable')

	info['sector_size'] = V_SECTOR_SIZE
	info['media_type'] = 'unknown'
	info['sector_count'] = 0
	if info['media'] == 0:
		info['media_type'] = 'no emulation'
		info['sector_count'] = 0
	elif info['media'] == 1:
		info['media_type'] = '1.2meg floppy'
		info['sector_count'] = 1200 * 1024 / V_SECTOR_SIZE
	elif info['media'] == 2:
		info['media_type'] = '1.44meg floppy'
		info['sector_count'] = 1440 * 1024 / V_SECTOR_SIZE
	elif info['media'] == 3:
		info['media_type'] = '2.88meg floppy'
		info['sector_count'] = 2880 * 1024 / V_SECTOR_SIZE
	elif info['media'] == 4:
		info['media_type'] = 'harddisk'
		# mbr = _get_sector(start, 1, input_file)
		mbr = _get_sector(file_handle, info['start'], 1)
		part = mbr[446:462]
		segment = struct.unpack('<8sLL', part)
		# skip 0
		first = segment[1]
		size = segment[2]
		info['sector_count'] = first + size
	if info['sector_count'] == 0:
		info['sector_count'] = cnt

	image = _get_sector(file_handle, info['start'], info['sector_count'])
	return {
		'info': info,
		'data': BytesIO(image)
	}
