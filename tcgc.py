#!/usr/bin/python3

# image processing library
from PIL import Image
from math import ceil
import logging
import subprocess
from os.path import basename, exists, isdir
from os import listdir, makedirs
from sys import exit

class TCGC:

    def __init__(self):
        logging.basicConfig(level="DEBUG")
        self.height_physical_inches = 2.5
        self.width_physical_inches = 3.5
        self.tmp_dir = "/tmp/tcgc"
        self.tmp_dir_individuals = self.tmp_dir + "/individuals"
        self.tmp_dir_horizontal = self.tmp_dir + "/horizontal"
        self.tmp_dir_vertical = self.tmp_dir + "/vertical"

        if not exists(self.tmp_dir):
            makedirs(self.tmp_dir)
            makedirs(self.tmp_dir + "/individuals")
            makedirs(self.tmp_dir + "/horizontal")
            makedirs(self.tmp_dir + "/vertical")

    def find_first_image(self, images_dir):
        first_image_name = listdir(images_dir)[0]
        first_image = images_dir + "/" + first_image_name
        logging.debug("First image found: %s" % first_image)
        return first_image

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
        card_file_name = basename(image_path)
        convert_cmd_args = ['-units', 'PixelsPerInch', '-density', ppi, image_path, self.tmp_dir + "/individuals/" + card_file_name]
        self.convert(convert_cmd_args)
        return True

    def convert_merge(self, convert_merge_method, image_paths):

        if convert_merge_method == "vertical":
            convert_merge_arg = "-append"
        elif convert_merge_method == "horizontal":
            convert_merge_arg = "+append"
        else:
            logging.error("Incorrect convert_merge_method specificed." +
                          " Please use horizontal or vertical.")
            exit(1)

        convert_cmd_args = [convert_merge_arg, *image_paths, self.tmp_dir + "/" + convert_merge_method + "/" + "out.jpg"]
        self.convert(convert_cmd_args) 
        return True

    def convert_batch_individuals(self, images_dir):

        first_image = self.find_first_image(images_dir)
        first_img_info = self.img_info(first_image)
        ppi = self.calc_ppi(first_img_info)

        for image in listdir(images_dir):
            image_path = images_dir + "/" + image

            if not isdir(image_path):
                logging.debug("Convert batch processing the image: %s" % image)
                self.convert_img(image_path, ppi)

        return True

    def convert_batch_append(self):
        image_count = 0
        image_paths = []

        for image in listdir(self.tmp_dir_individuals):
            image_count += 1

            if image_count > 4:
                self.convert_merge("vertical", image_paths)
                # Reset the count and paths if 4 cards have processed already
                image_count = 0
                image_paths = []
            elif image_count <= 4:
                image_path = images_dir + "/" + image
                image_paths.append(image_path)

        return True

tcgc = TCGC()
images_dir = "/tmp/cards"
tcgc.convert_batch_individuals(images_dir)
tcgc.convert_batch_append()
