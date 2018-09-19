# Card Games Converter (CGC)

[![Build Status](https://travis-ci.org/ekultails/card_games_converter.svg?branch=master)](https://travis-ci.org/ekultails/card_games_converter)

This program is used to batch convert standard 2.5 by 3.5 inches playing cards into a printable format. Each card in the `/tmp/cards/` directory will be rotated and have it's pixel per inch density changed to be the actual physical card size. Those card images will then be merged into stacks of 4 vertically. Next, every two stacks of 4 cards are merged horizontally to make a total of up to the maximum of 8 images per page to print. The completed images are saved to `/tmp/cgc/horizontal/`.

This is aimed for use with independent and free card games that are intended for personal use.

## Installation

Install ImageMagick and Python 3 on a Linux system.

Stable CGC releases can be downloaded from [here](https://github.com/ekultails/card_games_converter/releases).

## Usage

* Create the directory `/tmp/cards/`.
* Copy individual images of cards to be printed to that directory.
* Execute the CGC program: `./cgc-cli.py`
* Print the resulting pages from `/tmp/cgc/horizontal/`.

### CLI

Help options:

`./cgc-cli.py -h`

### Python Object

Minimal Python code example:

```
#!/usr/bin/env python3

from cgc import CGC


cgc = CGC()
cgc.convert_batch_append_all()
```

### Example Usage

#### Star Wars Trading Card Game (Wizards of the Coast)

The [Star Wars Trading Card Game (TCG)](http://starwars.wikia.com/wiki/Star_Wars_Trading_Card_Game) lasted from 2001 to 2005 before being cancelled. It is now unofficially maintained by the [Independent Development Committee (IDC)](https://swtcgidc.wordpress.com/) that continues to make new cards and expansion packs. The latest rulebook explaining how to play can be found [here](https://swtcgidc.wordpress.com/rules/).

Download the "Zipped Card JPGs" archive of an expansion pack of playing cards from [here](https://swtcgidc.wordpress.com/expansions-home/). Extract the archive and copy the desired cards to print into a different folder. Then use CGC to process the cards.

```
./cgc-cli.py --src /home/user/Documents/cards_to_print/
```

Printable pages of cards with the correct size and pixel density will be created and placed in the directory `/tmp/cgc/horizontal/`.

This utility avoids the need to use the "Printable PDFs" provided for some IDC expansions. Ink and paper are not wasted, a person can print the exact cards they want, and this addresses how not every expansion has "Printable PDFs" available.

# Developers

Refer to the technical design document for more information about the development of CGC.

[cgc_tdd.md](cgc_tdd.md)

All of the cgc.py code should get a perfect 10/10 Pylint score.

```
$ pylint cgc.py
No config file found, using default configuration

------------------------------------
Your code has been rated at 10.00/10
```

## License

Apache v2.0
