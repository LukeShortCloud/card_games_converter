#!/usr/bin/python3

# image processing library
from PIL import Image
from math import ceil
import logging
import subprocess

class TCGC:

    def __init__(self):
        logging.basicConfig(level="DEBUG")
        self.height_physical_inches = 2.5
        self.width_physical_inches = 3.5

    def img_info(self, image_path):
        with Image.open(image_path) as image:
            height, width = image.size
        return height, width

    def calc_ppi(self, image_dimensions):
        height_ppi = image_dimensions[0] / self.height_physical_inches
        width_ppi = image_dimensions[1] / self.width_physical_inches
        logging.debug("Height PPI = %d, Width PPI = %d" % (height_ppi, width_ppi))
        # Find the average PPI and round up.
        ppi = ceil((height_ppi + width_ppi) / 2)
        return ppi

    def convert(self, convert_cmd_args):
        cmd = ['convert']

        for item in convert_cmd_args:
            cmd.append(str(item))

        logging.debug("convert command: %s" % " ".join(cmd))
        convert_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, stderr = convert_process.communicate()
        logging.debug("convert command rc: %s" % convert_process.wait())
        logging.debug("convert command stdout: %s" % stdout)
        logging.debug("convert command stderr: %s" % stderr)
        return stdout

    def convert_img(self, image_path, ppi):
        convert_cmd_args = ['-units', 'PixelsPerInch', '-density', ppi, image_path, image_path + "NEWPPI"]
        self.convert(convert_cmd_args) 
        return True

    def convert_batch(self):
        return


tcgc = TCGC()
image_path = "/home/ekultails/Downloads/55-snowtrooperofficer.jpg"
image_dimensions = tcgc.img_info(image_path)
ppi = tcgc.calc_ppi(image_dimensions)
tcgc.convert_img(image_path, ppi)
