#!/usr/bin/env python3

from argparse import ArgumentParser
from cgc import CGC


if __name__ == "__main__":
    log_level_arg = "INFO"
    tmp_dest_dir_arg = "/tmp/cgc"
    parser = ArgumentParser()
    parser.add_argument("--src", help="the source directory.")
    parser.add_argument("--dest", help="the destination directory.")
    parser.add_argument("--ppi-height", help="the desired height in inches.",
                        type=int)
    parser.add_argument("--ppi-width", help="the desired width in inches.",
                        type=int)
    parser.add_argument("-v", help="verbose logging.", action="store_true")
    args = parser.parse_args()

    if args.v:
        log_level_arg = "DEBUG"

    if args.dest:
        tmp_dest_dir_arg = args.dest

    # The destination directory must be set during initialization
    # to create the necessary directories.
    cgc = CGC(tmp_dest_dir=tmp_dest_dir_arg, log_level=log_level_arg)

    if args.src:
        cgc.tmp_src_dir = args.src

    if args.ppi_height:
        cgc.height_physical_inches = args.ppi_height

    if args.ppi_width:
        cgc.height_physical_width = args.ppi_width

    cgc.convert_batch_append_all()
