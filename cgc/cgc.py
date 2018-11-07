#!/usr/bin/env python3
"""cgc provides a single class named CGC for processing card images into a
   printable format
"""

import logging
import subprocess
from os import listdir, makedirs
from os.path import basename, exists, isdir
from math import ceil
from hashlib import sha512
# Image processing library.
from PIL import Image
import pkg_resources


class CGC:
    """CGC provides methods for reformatting cards into printable sheets."""

    def __init__(self, tmp_dest_dir="/tmp/cgc", height_physical_inches=2.5,
                 width_physical_inches=3.5, log_level="INFO"):
        """Initialize CGC by creating temporary directories
        and setting the standard phsical size of a card.

        Args:
            height_physical_inches (int)
            width_physical_inches (int)
        """
        logging.basicConfig(level=log_level)
        self.cache_mode = None
        self.height_physical_inches = height_physical_inches
        self.width_physical_inches = width_physical_inches
        self.tmp_src_dir = "/tmp/cards"
        self.tmp_dest_dir = tmp_dest_dir
        self.tmp_dir_individual = self.tmp_dest_dir + "/individual"
        self.tmp_dir_horizontal = self.tmp_dest_dir + "/horizontal"
        self.tmp_dir_vertical = self.tmp_dest_dir + "/vertical"

        if not exists(self.tmp_dest_dir):

            try:
                makedirs(self.tmp_dest_dir)
                makedirs(self.tmp_dir_individual)
                makedirs(self.tmp_dir_horizontal)
                makedirs(self.tmp_dir_vertical)
            # Disable a false-positive error about the variable name "e"
            # not being valid snake_case.
            # pylint: disable=C0103
            except IOError as e:
                logging.critical("Failed to make temporary directories.\n%s", e)

    @staticmethod
    def get_version():
        """Returns the CGC package version string."""
        return pkg_resources.require("cgc")[0].version

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
            list: width, height
        """

        with Image.open(image_path) as image:
            width, height = image.size

        return width, height

    def calc_ppi(self, image_dimensions):
        """Calculate the pixels per inch density based on the desired
        physical dimensions of an image and the virtual dimensions of
        an image.

        Args:
            image_dimensions (list): width, height

        Returns:
            ppi (int)
        """
        width_ppi = image_dimensions[0] / self.width_physical_inches
        height_ppi = image_dimensions[1] / self.height_physical_inches
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
                stdout (str bytes)
                stderr (str bytes)
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

    def image_rotate(self, image_path_src, image_path_dest, degrees=90):
        """Execute the convert command to rotate an image.

        Args:
            image_path (str)
            degrees (int)

        Returns:
            boolean: If the convert command completed successfully.
        """
        image = Image.open(image_path_src)
        image_rotated = image.rotate(angle=90, expand=True)
        image_rotated.save(image_path_dest)
        return True

    def image_rotate_by_dimensions(self, image_path):
        """Rotate an image only if the width is greater than the height.

        Args:
            image_path (str)

        Returns:
            boolean: If the image was successfully rotated.
        """
        width, height = self.image_info(image_path)

        if width < height:
            logging.debug("Rotating image: %s", image_path)

            if not self.image_rotate(image_path, image_path):
                return False

        return True

    def image_density_change(self, image_path_src, image_path_dest, ppi):
        """Change the density of the pixels per inch of an image.

        Args:
            image_path_src (str): The original full image path to convert
            image_path_dest (str): The new full image path to save to
            ppi (int): The desired pixels per inch density

        Returns:
            boolean: If the convert density command finished successfully
        """
        image = Image.open(image_path_src)
        image.save(image_path_dest, dpi=(ppi, ppi))
        return True

    @staticmethod
    def listdir_full_path(src):
        """Return a list of full paths to each file in a directory.

        Args:
            src (str): The source directory to look for files in.

        Yields:
            list: The full path of each file in a directory.
        """

        for file in listdir(src):
            yield src + "/" + file

    def cache_mode_name(self, src_dir=None, dest_dir=None):
        """Use a cache by comparing file names from a source and destination
        directory. If the file name from the source directory is missing in the
        destination then it will be returned. It is assumed that those file
        images need to be proccessed.

        Args:
            None

        Returns:
            list: The full path to each file that is missing in the destination
                  directory.
        """

        # These variables cannot be assigned as arugments because the "self"
        # variable is not available yet during the function initialization.
        if src_dir is None:
            src_dir = self.tmp_src_dir

        if dest_dir is None:
            dest_dir = self.tmp_dir_individual

        dest_full_paths = list(self.listdir_full_path(dest_dir))
        files_cache_invalid = []
        src_file_found = False

        for src_file in listdir(src_dir):

            for dest_full_path in dest_full_paths:

                if dest_full_path.endswith(src_file):
                    src_file_found = True

            if not src_file_found:
                files_cache_invalid.append(src_dir + "/" + src_file)

        logging.debug("Cache is invalid for: %s", files_cache_invalid)
        return files_cache_invalid

    def cache_mode_sha512(self, src_dir=None, dest_dir=None):
        """Use a cache by comparing SHA512 checksums for each file from a
        source and destination directory. If the checksum is the same then
        the destination file might not have been processed yet. It is assumed
        that those file images need to be proccessed.

        Args:
            None

        Returns:
            list: The full path to each file that has the same checksum in the
                  source and destination directory.
        """

        if src_dir is None:
            src_dir = self.tmp_src_dir

        if dest_dir is None:
            dest_dir = self.tmp_dir_individual

        dest_full_paths = list(self.listdir_full_path(dest_dir))
        files_cache_invalid = []
        src_hash = ""
        dest_hash = ""

        for src_file in listdir(src_dir):
            src_full_path = src_dir + "/" + src_file

            for dest_full_path in dest_full_paths:

                if dest_full_path.endswith(src_file):

                    with open(dest_full_path, "rb") as dest_full_path_file:
                        dest_hash = sha512(dest_full_path_file.read()).hexdigest()
                        logging.debug("dest_full_path: %s", dest_full_path)
                        logging.debug("dest_hash: %s", dest_hash)

                    with open(src_full_path, "rb") as src_full_path_file:
                        src_hash = sha512(src_full_path_file.read()).hexdigest()
                        logging.debug("src_full_path: %s", src_full_path)
                        logging.debug("src_hash: %s", src_hash)

                    if src_hash == dest_hash:
                        # Assume that if the file is exactly the same it probably
                        # needs to be processed.
                        files_cache_invalid.append(src_full_path)

        if files_cache_invalid != []:
            logging.debug("Cache is invalid for: %s", files_cache_invalid)

        return files_cache_invalid

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
               self.tmp_dest_dir + "/" + convert_merge_method +
               "/" + merged_image_name]

        if self.run_cmd(cmd)["rc"] != 0:
            return False

        return True

    def convert_single(self, image_path_src, ppi=None):
        """Convert a single image to be a different density and rotate it
        90 degrees if it is vertical.

        Args:
            image_path_src (str): The image to convert

        Returns:
            boolean: If any of the convert commands failed
        """
        logging.debug("Doing a full image conversion for: %s", image_path_src)

        if ppi is None:
            image_dimensions = self.image_info(image_path_src)
            ppi = self.calc_ppi(image_dimensions)

        card_file_name = basename(image_path_src)
        image_path_dest = (self.tmp_dir_individual + "/" +
                           card_file_name)

        if not self.image_density_change(image_path_src,
                                          image_path_dest, ppi):
            return False

        if not self.image_rotate_by_dimensions(image_path_dest):
            return False

        return True

    def convert_batch_directory(self, images_dir):
        """Convert an entire directory from a specified path to be
        a different density and rotate them if needed. (Both the
        "image_density_change" and "image_rotate_by_dimensions" methods
        are used on each image.

        Args:
            images_dir (str)

        Returns:
            boolean: If any of the convert commands failed
        """
        first_image = self.find_first_image(images_dir)
        first_image_info = self.image_info(first_image)
        ppi = self.calc_ppi(first_image_info)
        image_paths_src = []

        if self.cache_mode == "name":
            image_paths_src = self.cache_mode_name()
        elif self.cache_mode == "sha512":
            image_paths_src = self.cache_mode_sha512()
        else:

            for image in listdir(images_dir):
                image_paths_src.append(images_dir + "/" + image)

        for image_path_src in image_paths_src:

            if not isdir(image_path_src):
                self.convert_single(image_path_src, ppi)

        return True

    def convert_batch_append(self, append_method):
        """Merge individual images in batches of 4 vertically
        or batches of 2 horizontally for optimal printing space
        usage.

        Args:
            append_method (str): Append images either by "vertical" or "horizontal"

        Returns:
            boolean: If any of the methods failed
        """

        if append_method == "vertical":
            images = listdir(self.tmp_dir_individual)
            image_count_max = 4
            tmp_dir_append = self.tmp_dir_individual
        elif append_method == "horizontal":
            images = listdir(self.tmp_dir_vertical)
            image_count_max = 2
            tmp_dir_append = self.tmp_dir_vertical
        else:
            logging.critical("Incorrect append_method provided. Use vertical or horizontal.")
            return False

        total_count = 0
        image_count = 0
        image_paths = []
        number_of_images = len(images)
        logging.debug("Number of total images found: %s", str(number_of_images))

        for image in images:
            total_count += 1
            image_count += 1
            image_paths.append(tmp_dir_append + "/" + image)

            if image_count >= image_count_max:

                if not self.convert_merge(append_method, image_paths,
                                          str(total_count) + ".jpg"):
                    return False

                # Reset the count and paths if 2 (horizontal) or 4 (veritcal)
                # cards have been processed already.
                image_count = 0
                image_paths = []
            elif image_count < image_count_max:

                # If this is the last image, then merge all of the
                # remaining images.
                if total_count == number_of_images:

                    if not self.convert_merge(append_method, image_paths,
                                              str(total_count) + ".jpg"):
                        return False

        return True

    def convert_batch_append_all(self):
        """Merge all individual cards into a printable set. The cards are
        assumed to have already had their density changed and have been
        rotated by the "convert_batch_directory" method. "convert_batch_append"
        will process both "vertical" and "horizontal" appending.

        Args:
            None

        Returns:
            boolean: If any of the methods failed
        """

        if not self.convert_batch_directory(self.tmp_src_dir):
            return False

        if not self.convert_batch_append(append_method="vertical"):
            return False

        if not self.convert_batch_append(append_method="horizontal"):
            return False

        return True
