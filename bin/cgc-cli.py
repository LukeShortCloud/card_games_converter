#!/usr/bin/env python3
"""A command-line interface utility for managing Card Games Converter (CGC)."""

from argparse import ArgumentParser
from sys import stderr
from cgc.cgc import CGC


def main():
    """The main function for handling all of the CGC CLI arguments and
    initializing a CGC object.
    """
    log_level_arg = "INFO"
    tmp_dest_dir_arg = "/tmp/cgc"
    parser = ArgumentParser()
    parser.add_argument("--src", help="the source directory")
    parser.add_argument("--dest", help="the destination directory")
    parser.add_argument("--ppi-height", help="the desired height in inches",
                        type=int)
    parser.add_argument("--ppi-width", help="the desired width in inches",
                        type=int)
    parser.add_argument("--single", help="convert a single card to a" + \
                        " printable format.")
    parser.add_argument("--cache", help="the cache mode to use: name, none, "
                        "or sha512 (default: none)", default="none", type=str)
    parser.add_argument("-v", help="verbose logging", action="store_true")
    parser.add_argument("--version", help="display the CGC version",
                        action="store_true")
    args = parser.parse_args()

    if args.v:
        log_level_arg = "DEBUG"

    if args.dest:
        tmp_dest_dir_arg = args.dest

    # The destination directory must be set during initialization
    # to create the necessary directories.
    cgc = CGC(tmp_dest_dir=tmp_dest_dir_arg, log_level=log_level_arg)

    if args.version:
        print(cgc.get_version())

    if args.src:
        cgc.tmp_src_dir = args.src

    if args.ppi_height:
        cgc.height_physical_inches = args.ppi_height

    if args.ppi_width:
        cgc.height_physical_width = args.ppi_width

    if args.cache:

        if args.cache not in ["name", "none", "sha512"]:
            stderr.write("Invalid cache mode specified. Use name or sha512. "
                         "No cache will be used.")
        else:
            cgc.cache_mode = args.cache

    # The last argument to process is to see what action should be done
    # (processing one or all cards).
    if args.single:
        cgc.convert_single(args.single)
    else:
        cgc.convert_batch_append_all()


if __name__ == '__main__':
    main()
