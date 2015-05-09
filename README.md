FVP tools
---------

Tools for translating games based on FVP engine.

### `bin_archiver`

BIN archive packer and unpacker. Does not convert images for performance
reasons: if you often need to repack, converting *all* images would take too
much time. Instead, you select one image to convert, and then pack the files.

NOTE: when packing, make sure the folder doesn't contain any files other than
files unpacked from original archive, otherwise the game will crash. This is a
limitation of FVP games since they expect a fixed number of files.

### `nvsg_converter`

Image converter. Converts image files to png and vice versa. For mass
conversion, use shell scripts:

    mkdir converted
    cd folder
    for x in *; do
        ../nvsg_converter --decode "$x" ../converted/"$x.png"
    done

will convert everything in folder to PNG.

Caveats:

1. NVSG images have no extensions (like pretty much everything else in FVP
   games).
2. You must pass `-x` and `-y`, and optionally `--image_count` when encoding
   images back, or there are good chances your graphic won't be rendered.

### `hcb_compiler`

Script (de)compiler (original author -
[SaintLouisX](http://www.hongfire.com/forum/showthread.php/433568))

Modifications from original version:

- Python 3 support
- Heavily optimized (compiling is about 5x faster, decompiling about 2x faster)
- Better user friendliness (no more exceptions when running without arguments)
- Simplified code structure so it's much easier to add support for possible new
  features
