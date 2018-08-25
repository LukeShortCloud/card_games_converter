# Card Games Converter (CGC)

This program is used to batch convert standard 2.5 by 3.5 inches cards into a printable format. Each card in the `/tmp/cards/` directory will be rotated, have it's pixel per inch density changed to be the actual physical card size, and then combine up to 8 cards per page to print. The completed images are saved to `/tmp/cgc/horizontal/`.

This is aimed for use with independent and free card games that are intended for personal use.

## Installation

Install ImageMagick and Python 3 on a Linux system.

## Usage

* Create the directory `/tmp/cards/`.
* Copy individual images of cards to that directory.
* Execute CGC: `$ python3 cgc.py`.
* Print the resulting pages from `/tmp/cgc/horizontal/`.

## License

Apache v2.0
