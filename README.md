# Card Games Converter (CGC)

This program is used to batch convert standard 2.5 by 3.5 inches cards into a printable format. Each card in the `/tmp/cards/` directory will be rotated, have it's pixel per inch density changed to be the actual physical card size, and then combine up to 8 cards per page to print. The completed images are saved to `/tmp/cgc/horizontal/`.

This is aimed for use with independent and free card games that are intended for personal use.

## Installation

Install ImageMagick and Python 3 on a Linux system.

Stable CGC releases can be downloaded from [here](https://github.com/ekultails/card_games_converter/releases).

## Usage

Example Python code:

```
#!/usr/bin/python3

from cgc import CGC


cgc = CGC()
use_images_dir = "/tmp/cards"
cgc.convert_batch_individual(use_images_dir)
cgc.convert_batch_append_all()
```

* Create the directory `/tmp/cards/`.
* Copy individual images of cards to that directory.
* Execute the CGC program.
* Print the resulting pages from `/tmp/cgc/horizontal/`.

# Developers

Refer to the technical design document for more information about the development of CGC.

[cgc_tdd.md](cgc_tdd.md)

All of the code should get a perfect 10/10 Pylint score.

```
$ pylint cgc.py
No config file found, using default configuration

------------------------------------
Your code has been rated at 10.00/10
```

## License

Apache v2.0
