# Card Games Converter (CGC) - Technical Design Document

# Description

The "Card Games Converter" (CGC) is a utility for converting pictures of cards into a printable format.

# Technologies

* Python 3.6
    * PIL
* imagemagick
* Linux

# Functions

* find_first_image = Locate the first image in a directory.
    * Input
        * images_dir (str) = The images directory to search in.
    * Output
        * first_image (str) = The first image found.
* image_info = Find the resolution dimensions of an image.
    * Input
        * image_path (str) = The full path to an image.
    * Output
        * height (int)
        * width (int)
* calc_ppi = Calculate and return the PPI for an image based on it's height and width.
    * Input
        * image_dimensions (list) = The resolution height and width of an image.
    * Ouput
        * ppi (int) = The pixels per inch density.
* run_cmd = Execute a shell command.
    * Input
        * cmd (list) = A list of a command and arguments for it.
    * Ouput
        * cmd_return (dict)
            * rc (int) = Return code.
            * stdout (str bytes) = Standard output.
            * stderr (str bytes) = Standard error.
* convert_rotate = Rotate an image.
    * Input
        * image_path (str) = The full image path to use.
    * Ouput
        * boolean = If this method was successful.
* image_rotate_by_dimensions = Rotate an image if the width is greater than the height. This allows for stacking of images for a printable page of 8 cards.
    * Input
        * image_path (src) = The full path to the image.
    * Ouput
        * boolean = If this method was successful.
* convert_image_density = Convert a single image to a specific physical size density based on the PPI.
    * Input
        * image_path_src (str) = The full path to the source image to convert.
        * image_path_dest (str) = The full path to the destination image to save as.
        * ppi (int) = The desired pixels per inch density.
    * Ouput
        * boolean = If this method was successful.
* convert_merge = Merge one or more images together either vertically or horizontally.
    * Input
        * convert_merge_method (str) = Append the images together in the "vertical" or "horizontal" direction
        * images_paths (list) = A list of all of the full image paths to append together.
        * merged_image_name (str) = The full image path where the result will be saved to.
    * Ouput
        * boolean = If this method was successful.
* convert_batch_individual = Convert a batch of individual images into a format that can be properly appended. These will be rotated (if necessary) and have their PPI density changed.
    * Input
        * images_dir (str) = The directory of images that should be processed.
    * Ouput
        * boolean = If this method was successful.
* convert_batch_append = Batch append images in a certain direction
    * Input
        * append_method (str) = The way to append, either in the "vertical" or "horizontal" direction.
    * Ouput
        * boolean = If this method was successful.
* convert_batch_append_all = Batch convert all individual images into printable pages.
    * Input
        * None
    * Ouput
        * boolean = If this method was successful.

# CLI Arguments (cgc-cli)

* -h, --help = Show the help information.
* -s, --src = The source directory.
* -d, --dest = The destination directory.
* --ppi-size = The pixels per inch size to use.
* --ppi-length = The desired length in inches.
* --ppi-width = The desired width in inches.
* --single = Process a single source image instead of an entire directory.
* --no-clean = Do not clean up temporary files when complete.
* --cache {name|sha256} = The cache mode to use. Requires the use of `--no-clean`.
    * name = Use the image name to see if a temporary modified image exists.
    * sha256 = Use a checksum to see if an image has been modified already.

# Milestones

* 1.0.0 = All required functions are written and working.
* 1.1.0 = Tests are written and all relevant exceptions are added to the code.
* 1.2.0 = Programs works as a CLI utility with arguments.
* 1.3.0 = Caching is supported. Processing of individual images can be skipped by comparing the original and processed images. The check can use a name or a SHA256 checksum.
* 1.4.0 = Parallel processing is added.
* 1.5.0 = Image rotating and density resizing is handled by the Python PIL library instead of the `convert` command.
* 1.6.0 = Pip package support.
* 2.0.0 = API v1 is implemented.

# Development Time

| VERSION | TIME ESTIMATED (HOURS) | TIME ACTUAL (HOURS) |
| ------- | ---------------------- | ------------------- |
| 1.0.0 | 40 | 20 |
| 1.1.0 | 8 | 10 |
| 1.2.0 | 8 | |
| 1.3.0 | 4 | |
| 1.4.0 | 4 | |
| 1.5.0 | 8 | |
| 1.6.0 | 4 | |
| 2.0.0 | 40 | |

# Lessons Learned

* Methods need to be as small as possible to abide by modular OOP best practices.
* All function inputs and outputs need to be defined in the TDD before creating the program. The TDD serves a purpose of being pseudocode code. The extra time put into planning leads to faster development time.
* When creating a new method, the related docstrings and a unit test should also be created at the same time. This avoids time wasted on troubleshooting later on.

# TDD Revision History

* 2018-08-14
    * Initial draft created.
* 2018-08-16
    * Updated milestones versions. They no longer conflict with the original proof-of-concept version 0.1.0 shell script.
    * Added new milestone for having tests and exceptions written.
* 2018-08-26.0
    * Added new milestones for caching and having a Pip package.
    * Added existing functions.
    * Added inputs and outputs for functions.
    * Updated development time to be in hours.
    * Updated estimated hours to be more accurate.
    * Completed milestone `1.0.0`.
* 2018-08-26.1
    * Completed milestone `1.1.0`.
* 2018-09-03
    * Temporarily remove API requirements.
* 2018-09-08.0
    * Added CLI arguments.
    * Added lessons learned.
    * Added new milestone to exclusively use the Python PIL library for manipulating images.
* 2018-09-08.1
    * Refactored the convert_batch_append_all method to have less code and be more reusable.
* 2018-09-11
    * Corrected run_cmd outputs to show that bytes are returned.
