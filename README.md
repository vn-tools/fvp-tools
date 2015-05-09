FVP tools
---------

Tools for translating games based on FVP engine.

### `bin_archiver`

BIN archive packer and unpacker. Does not convert images for performance
reasons: if you often need to repack, converting *all* images would take too
much time. Instead, you select one image to convert, and then pack the files.

### `hcb_compiler`

Script (de)compiler (original author -
[SaintLouisX](http://www.hongfire.com/forum/showthread.php/433568))

Modifications from original version:

- Python 3 support
- Heavily optimized (compiling is about 5x faster, decompiling about 2x faster)
- Better user friendliness (no more exceptions when running without arguments)
- Simplified code structure so it's much easier to add support for possible new
  features
