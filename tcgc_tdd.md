# TCGC - Technical Design Document

# Description

The "Trading Card Games Converter" (TCGC) is a utility for converting pictures of cards into a printable format.

# Technologies

* Python 3.6
    * falcon
* imagemagick
* Linux

# API

* v1
    * /resize/ = POST. Upload a picture, convert it's size, and download the converted picture.
        * height and width  = Specify a different physical size. The default is 2.5 inches high and 3.5 inches wide.

# Functions

* img_info = Return the height (int) and width (int) resolution of an image.
* calc_ppi = Calculate and return the PPI (int) for an image based on it's height and width.
* convert = Execute the "convert" Imagemagick command.
* convert_img = Convert a single image to a specific physical size.
* convert_batch = Batch convert images into printable pages.

# Milestones

* 1.1 = All required functions are written and working.
* 1.2 = Tests are written and all relevant exceptions are added to the code.
* 1.3 = Programs works as a CLI utility with arguments.
* 1.4 = Parallel processing is added.
* 2.0 = API v1 is implemented.

# Development Time

* VERSION,TIME ESTIMATED,TIME ACTUAL
* 1.1, 1 week
* 1.2, 1 week
* 1.3, 1 week
* 1.4, 1 week
* 2.0, 4 weeks

# TDD Revision History

* 2018-08-14
    * Initial draft created.
* 2018-08-16
    * Updated milestones versions. They no longer conflict with the original proof-of-concept version 0.1.0 shell script.
    * Added new milestone for having tests and exceptions written.
