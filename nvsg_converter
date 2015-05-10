#!/usr/bin/python3
import argparse
import sys
import zlib
from PIL import Image
from open_ext import open_ext

HZC1_MAGIC = b'hzc1'
NVSG_MAGIC = b'NVSG'

def swap_channels(img):
    channels = list(img.split())
    channels[0], channels[2] = channels[2], channels[0]
    return Image.merge(img.mode, channels)

def convert_to_png(input_file, output_file):
    if input_file.read(len(HZC1_MAGIC)) != HZC1_MAGIC:
        raise RuntimeError('Not a NVSG file')
    uncompressed_size = input_file.read_u32_le()
    nvsg_header_size = input_file.read_u32_le()
    if input_file.read(len(NVSG_MAGIC)) != NVSG_MAGIC:
        raise RuntimeError('Not a NVSG file')

    unk = []
    unk.append(input_file.read_u16_le()) #always 256?
    format = input_file.read_u16_le()
    width = input_file.read_u16_le()
    height = input_file.read_u16_le()
    x = input_file.read_u16_le() #not sure if coordinates, but seems close
    y = input_file.read_u16_le()
    unk.append(input_file.read_u16_le())
    unk.append(input_file.read_u16_le())
    image_count = input_file.read_u32_le()
    unk.append(input_file.read_u32_le())
    unk.append(input_file.read_u32_le())

    data = input_file.read_until_end()
    data = zlib.decompress(data)

    if format == 0:
        img = swap_channels(Image.fromstring('RGB', (width, height), data))
    elif format == 1:
        img = swap_channels(Image.fromstring('RGBA', (width, height), data))
    elif format == 2:
        height *= image_count
        img = swap_channels(Image.fromstring('RGBA', (width, height), data))
        print('Make sure to pass --image_count %d when converting back!' % (image_count))
    elif format == 3:
        img = Image.fromstring('L', (width, height), data)
    elif format == 4:
        raise NotImplementedError('1 bit images are not implemented')
    else:
        raise NotImplementedError('Unknown image format')
    img.save(output_file, 'png')
    print('Make sure to pass -x %d -y %d converting back!' % (x, y))

def convert_from_png(input_file, output_file, image_count, x, y):
    img = Image.open(input_file)
    img.load()
    width, height = img.size
    if image_count != 1:
        if img.mode != 'RGBA':
            raise RuntimeError('Image strides must be saved with alpha channel.')
        format = 2
        height = int(height / image_count)
        img = swap_channels(img)
    elif img.mode == 'RGBA':
        format = 1
        img = swap_channels(img)
    elif img.mode == 'RGB':
        format = 0
        img = swap_channels(img)

    data = img.tostring()

    output_file.write(HZC1_MAGIC)
    output_file.write_u32_le(len(data))
    output_file.write_u32_le(0x20)
    output_file.write(NVSG_MAGIC)
    output_file.write_u16_le(256)
    output_file.write_u16_le(format)
    output_file.write_u16_le(width)
    output_file.write_u16_le(height)
    output_file.write_u16_le(x)
    output_file.write_u16_le(y)
    output_file.write_u16_le(0)
    output_file.write_u16_le(0)
    output_file.write_u32_le(image_count)
    output_file.write_u32_le(0)
    output_file.write_u32_le(0)
    output_file.write(zlib.compress(data))

def main():
    parser = argparse.ArgumentParser(description='Converts NVSG to PNG and vice versa')
    parser.add_argument('--image_count', type=int, default=1, help='used in encoding character avatars')
    parser.add_argument('-x', nargs='?', type=int, default=0, help='used in encoding')
    parser.add_argument('-y', nargs='?', type=int, default=0, help='used in encoding')
    parser.add_argument('infile', nargs='?', type=open_ext.ArgParser('rb'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=open_ext.ArgParser('wb'), default=sys.stdout)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--decode', action='store_true', help='converts NVSG to PNG')
    group.add_argument('--encode', action='store_false', help='converts PNG to NVSG')
    result = parser.parse_args()
    if result.decode:
        convert_to_png(result.infile, result.outfile)
    else:
        convert_from_png(result.infile, result.outfile, result.image_count, result.x, result.y)

if __name__ == '__main__':
    main()
