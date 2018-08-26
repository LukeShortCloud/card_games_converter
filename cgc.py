#!/usr/bin/python3

import logging
import subprocess
from os import listdir, makedirs
from os.path import basename, exists, isdir
from math import ceil
# image processing library
from PIL import Image


class CGC:

    def __init__(self, height_physical_inches=2.5, width_physical_inches=3.5,
                 log_level="INFO"):
        """Initialize CGC by creating temporary directories
        and setting the standard phsical size of a card.

        Args:
            height_physical_inches (int)
            width_physical_inches (int)

        """
        logging.basicConfig(level=log_level)
        self.height_physical_inches = height_physical_inches
        self.width_physical_inches = width_physical_inches
        self.tmp_dir = "/tmp/cgc"
        self.tmp_dir_individual = self.tmp_dir + "/individual"
        self.tmp_dir_horizontal = self.tmp_dir + "/horizontal"
        self.tmp_dir_vertical = self.tmp_dir + "/vertical"

        if not exists(self.tmp_dir):

            try:
                makedirs(self.tmp_dir)
                makedirs(self.tmp_dir_individual)
                makedirs(self.tmp_dir_horizontal)
                makedirs(self.tmp_dir_vertical)
            # Disable a false-positive error about the variable name "e"
            # not being valid snake_case.
            # pylint: disable=C0103
            except IOError as e:
                logging.critical("Failed to make temporary directories.\n%s", e)

    @staticmethod
    def find_first_image(images_dir):
        """Locate the first image in a directory.

        Args:
            images_dir (str)

        Returns:
            first_image (str)

        """
        first_image_name = listdir(images_dir)[0]
        first_image = images_dir + "/" + first_image_name
        logging.debug("First image found: %s", first_image)
        return first_image

    @staticmethod
    def image_info(image_path):
        """Return the dimensions of an image.

        Args:
            image_path (str)

        Returns:
            list: height, width

        """

        with Image.open(image_path) as image:
            height, width = image.size

        return height, width

    def calc_ppi(self, image_dimensions):
        """Calculate the pixels per inch density based on the desired
        physical dimensions of an image and the virtual dimensions of
        an image.

        Args:
            image_dimensions (list): height, width

        Returns:
            ppi (int)

        """
        height_ppi = image_dimensions[0] / self.height_physical_inches
        width_ppi = image_dimensions[1] / self.width_physical_inches
        logging.debug("Height PPI = %d, Width PPI = %d", height_ppi,
                      width_ppi)
        # Find the average PPI and round up.
        ppi = ceil((height_ppi + width_ppi) / 2)
        return ppi

    @staticmethod
    def run_cmd(cmd):
        """Execute a command.

        Args:
            cmd (list): a list of a command and arguments

        Returns:
            cmd_return (dict):
                rc (int): return code
                stdout (str)
                stderr str)

        """
        cmd_return = {"rc": None, "stdout": None, "stderr": None}
        logging.debug("Running command: %s", " ".join(cmd))
        convert_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        cmd_return["stdout"], cmd_return["stderr"] = \
            convert_process.communicate()
        cmd_return["rc"] = int(convert_process.wait())
        logging.debug("convert command output: %s", str(cmd_return))
        return cmd_return

    def convert_rotate(self, image_path_src, image_path_dest, degrees="90"):
        """Execute the convert command to rotate an image.

        Args:
            image_path (str)
            degrees (int)

        Returns:
            boolean: If the convert command completed successfully.

        """
        cmd = ["convert", "-rotate", degrees, image_path_src,
               image_path_dest]

        if self.run_cmd(cmd)["rc"] != 0:
            return False

        return True

    def image_rotate_by_dimensions(self, image_path):
        """Rotate an image only if the width is greater than the height.

        Args:
            image_path (str)

        Returns:
            boolean: If the image was successfully rotated.

        """
        height, width = self.image_info(image_path)

        if width > height:
            logging.debug("Rotating image: %s", image_path)

            if not self.convert_rotate(image_path, image_path):
                return False

        return True

    def convert_image_density(self, image_path_src, image_path_dest, ppi):
        """Change the density of the pixels per inch of an image.

        Args:
            image_path_src (str): The original full image path to convert
            image_path_dest (str): The new full image path to save to
            ppi (int): The desired pixels per inch density

        Returns:
            boolean: If the convert density command finished successfully

        """
        cmd = ["convert", "-units", "PixelsPerInch", "-density", str(ppi),
               image_path_src, image_path_dest]

        if self.run_cmd(cmd)["rc"] != 0:
            return False

        return True

    def convert_merge(self, convert_merge_method, image_paths,
                      merged_image_name="out.jpg"):
        """Merge one or more images either vertically or horizontally.

        Args:
            convert_merge_method (str): vertical or horizontal
            image_paths (list)
            merged_image_name (str): the name to save the merged image as

        Returns:
            boolean: If the convert merge command finished successfully

        """
        convert_merge_arg = ""

        if convert_merge_method == "vertical":
            convert_merge_arg = "-append"
        elif convert_merge_method == "horizontal":
            convert_merge_arg = "+append"
        else:
            logging.error("Incorrect convert_merge_method specificed. \
                          Please use horizontal or vertical.")
            exit(1)

        cmd = ["convert", convert_merge_arg, *image_paths,
               self.tmp_dir + "/" + convert_merge_method +
               "/" + merged_image_name]

        if self.run_cmd(cmd)["rc"] != 0:
            return False

        return True

    def convert_batch_individual(self, images_dir):
        """Convert individual image paths from a specified path to be
        a different density and rotate them if needed. (Both the
        "convert_image_density" and "image_rotate_by_dimensions" methods
        are used on each image.

        Args:
            images_dir (str)

        Returns:
            boolean: If any of the convert commands failed

        """
        first_image = self.find_first_image(images_dir)
        first_image_info = self.image_info(first_image)
        ppi = self.calc_ppi(first_image_info)

        for image in listdir(images_dir):
            image_path_src = images_dir + "/" + image

            if not isdir(image_path_src):
                logging.debug("Convert batch individual processing the \
                              image: %s", image)
                card_file_name = basename(image_path_src)
                image_path_dest = (self.tmp_dir_individual + "/" +
                                   card_file_name)

                if not self.convert_image_density(image_path_src,
                                                  image_path_dest, ppi):
                    return False

                if not self.image_rotate_by_dimensions(image_path_dest):
                    return False

        return True

    def convert_batch_append_all(self):
        """Merge all individual cards into a printable set. The cards are
        assumed to have already had their density changed and have been
        rotated by the "convert_batch_individual" method.

        Args:
            None

        Returns:
            boolean: If any of the methods failed

        """
        total_count = 0
        image_count = 0
        image_paths = []
        images = listdir(self.tmp_dir_individual)
        number_of_images = len(images)
        logging.debug("Number of total images found: %s", str(number_of_images))

        for image in images:
            total_count += 1
            image_count += 1
            image_path = self.tmp_dir_individual + "/" + image
            image_paths.append(image_path)

            if image_count >= 4:

                if not self.convert_merge("vertical", image_paths,
                                          str(total_count) + ".jpg"):
                    return False

                # Reset the count and paths if 4 cards have processed already.
                image_count = 0
                image_paths = []
            elif image_count < 4:

                # If this is the last image, then merge all of the
                # remaining images.
                if total_count == number_of_images:

                    if not self.convert_merge("vertical", image_paths,
                                              str(total_count) + ".jpg"):
                        return False

        total_count = 0
        image_count = 0
        image_paths = []
        images_vertical = listdir(self.tmp_dir_vertical)
        number_of_vertical_images = len(images_vertical)

        for image in images_vertical:
            total_count += 1
            image_count += 1
            image_paths.append(self.tmp_dir_vertical + "/" + image)

            if image_count >= 2:

                if not self.convert_merge("horizontal", image_paths,
                                          str(total_count) + ".jpg"):
                    return False

                image_count = 0
                image_paths = []
            elif image_count < 2:

                if total_count == number_of_vertical_images:

                    if not self.convert_merge("horizontal", image_paths,
                                              str(total_count) + ".jpg"):
                        return False

        return True
