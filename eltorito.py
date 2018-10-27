#!/usr/bin/python3
"""
Extract El Torito image from a bootable CD (or image).

Reference:
https://userpages.uni-koblenz.de/~krienke/ftp/noarch/geteltorito/
https://en.wikipedia.org/wiki/El_Torito_(CD-ROM_standard)
"""
import argparse
import os
import struct

V_SECTOR_SIZE = 512
SECTOR_SIZE = 2048


def _get_sector(number, count, file_input):
    """Get a sector."""
    with open(file_input, 'rb') as f:
        f.seek(number * SECTOR_SIZE, 0)
        sector = f.read(V_SECTOR_SIZE * count)
        if len(sector) != V_SECTOR_SIZE * count:
            print("Invalid sector read")
        return sector


def _extract(input_file, output_file):
    """Extract image."""
    sector = _get_sector(17, 1, input_file)
    # we only need the first section of this segment
    segment = struct.unpack("<B5sB32s32sL", sector[0:75])
    boot = segment[0]
    iso = segment[1].decode("ascii")
    vers = segment[2]
    spec = segment[3].decode("ascii").strip()
    spec = "".join([x for x in spec if (x >= 'A' and x <= 'Z') or x == ' '])
    # 4 is unused
    partition = segment[5]
    if iso != "CD001" or spec.strip() != "EL TORITO SPECIFICATION":
        print("This is not a bootable cd-image")
        exit(1)
    print("boot catalog starts at {}".format(partition))
    sector = _get_sector(partition, 1, input_file)
    segment = struct.unpack("<BBH24sHBB", sector[0:32])
    header = segment[0]
    platform = segment[1]
    # skip 2
    manufacturer = segment[3].decode("ascii")
    # skip 4
    five = segment[5]
    aa = segment[6]
    if header != 1 or five != int("0x55", 16) or aa != int("0xaa", 16):
        print("Invalid validation entry")
        exit(1)
    print("Manufacturer: {}".format(manufacturer))
    platform_string = "unknown"
    if platform == 0:
        platform_string = "x86"
    elif platform == 1:
        platform_string = "PowerPC"
    elif platform == 2:
        platform_string = "Mac"
    print("Image architecture: {}".format(platform_string))
    segment = struct.unpack("<BBHBBHLB", sector[32:45])
    boot = segment[0]
    media = segment[1]
    load = segment[2]
    sys = segment[3]
    # skip 4
    cnt = segment[5]
    start = segment[6]
    # skip 7
    if boot != int("0x88", 16):
        print("Boot indicator is not 0x88, not bootable")
        exit(1)
    media_type = "unknown"
    count = 0
    if media == 0:
        media_type = "no emulation"
        count = 0
    elif media == 1:
        media_type = "1.2meg floppy"
        count = 1200 * 1024 / V_SECTOR_SIZE
    elif media == 2:
        media_type = "1.44meg floppy"
        count = 1440 * 1024 / V_SECTOR_SIZE
    elif media == 3:
        media_type = "2.88meg floppy"
        count = 2880 * 1024 / V_SECTOR_SIZE
    elif media == 4:
        media_type = "harddisk"
        mbr = _get_sector(start, 1, input_file)
        part = mbr[446:462]
        segment = struct.unpack("<8sLL", part)
        # skip 0
        first = segment[1]
        size = segment[2]
        count = first + size
    if count == 0:
        count = cnt
    print("Boot media is: {}".format(media_type))
    print("Starts at {} and has {} sectors (@ {} bytes)".format(start,
                                                                count,
                                                                V_SECTOR_SIZE))
    image = _get_sector(start, count, input_file)
    with open(output_file, 'wb') as f:
        f.write(image)
    print("Image written")


def main():
    """Main entry."""
    parser = argparse.ArgumentParser("el torito image extraction")
    parser.add_argument("input", help="cd image to read")
    parser.add_argument("output", help="output file")
    args = parser.parse_args()
    if not os.path.exists(args.input):
        print("unable to find {}".format(args.input))
        exit(1)
    if os.path.exists(args.output):
        print("output file already exists {}".format(args.output))
        exit(1)
    _extract(args.input, args.output)


if __name__ == "__main__":
    main()
