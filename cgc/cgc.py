#!/usr/bin/env python3
"""cgc provides a single class named CGC for processing card images into a
   printable format
"""

from sys import exit as sys_exit
import logging
import tempfile
from multiprocessing import Queue, Process
from os import listdir, makedirs
from os.path import basename, exists, isdir, join
from math import ceil
from hashlib import sha512
import img2pdf
# Image processing library.
from PIL import Image
import pkg_resources


class CGC:
    """CGC provides methods for reformatting cards into printable sheets."""

    def __init__(self, tmp_dest_dir=join(tempfile.gettempdir(), "cgc"),
                 height_physical_inches=2.5,
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
        self.tmp_src_dir = join(tempfile.gettempdir(), "cards")
        self.tmp_dest_dir = tmp_dest_dir
        self.tmp_dir_individual = join(self.tmp_dest_dir, "individual")
        self.tmp_dir_horizontal = join(self.tmp_dest_dir, "horizontal")
        self.tmp_dir_vertical = join(self.tmp_dest_dir, "vertical")
        self.tmp_dir_pdfs = join(self.tmp_dest_dir, "pdfs")
        self.cgc_managed_dirs = [self.tmp_dest_dir, self.tmp_dir_individual,
                                 self.tmp_dir_horizontal, self.tmp_dir_vertical,
                                 self.tmp_dir_pdfs]
        self.queue = Queue()

        if not exists(self.tmp_dest_dir):

            try:

                for new_dir in self.cgc_managed_dirs:
                    makedirs(new_dir)

            # Disable a false-positive error about the variable name "e"
            # not being valid snake_case.
            # pylint: disable=C0103
            except IOError as e:
                logging.critical("Failed to create all temporary directories.\n%s", e)

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
        first_image = join(images_dir, first_image_name)
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
    def image_rotate(image_path_src, image_path_dest, degrees=90):
        """Execute the convert command to rotate an image.

        Args:
            image_path (str)
            degrees (int)

        Returns:
            boolean: If the convert command completed successfully.
        """
        image = Image.open(image_path_src)
        image_rotated = image.rotate(angle=degrees, expand=True)
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

    @staticmethod
    def image_density_change(image_path_src, image_path_dest, ppi):
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
            yield join(src, file)

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
                files_cache_invalid.append(join(src_dir, src_file))

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
            src_full_path = join(src_dir, src_file)

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

    def images_merge(self, images_merge_method, image_paths,
                     merged_image_name="out.jpg"):
        """Merge one or more images either vertically or horizontally.
        This requires that a new PIL image be created with the correct
        dimensions and then have all of the images pasted in it with a
        proper offset as to not overlap one another.

        Args:
            images_merge_method (str): vertical or horizontal
            image_paths (list)
            merged_image_name (str): the name to save the merged image as

        Returns:
            boolean: If the PIL image merge command finished successfully
        """
        image_paths_open = []
        image_heights = 0
        image_widths = 0
        merged_height = 0
        merged_width = 0
        image_heights_all = []
        image_widths_all = []

        for image in image_paths:
            image_open = Image.open(image)
            image_paths_open.append(image_open)
            image_heights += image_open.height
            image_heights_all.append(image_open.height)
            image_widths += image_open.width
            image_widths_all.append(image_open.width)

        if images_merge_method == "vertical":
            merged_height = image_heights
            # Find and use the width of the first image.
            merged_width = max(image_widths_all)
        elif images_merge_method == "horizontal":
            # Find and use the height of the first image.
            merged_height = max(image_heights_all)
            merged_width = image_widths
        else:
            logging.error("Incorrect images_merge_method specificed. \
                          Please use horizontal or vertical.")
            sys_exit(1)

        merged_image = Image.new("RGB", (merged_width, merged_height))
        merged_pixel_offset = 0

        for image in image_paths_open:

            if images_merge_method == "vertical":
                merged_image.paste(image, (0, merged_pixel_offset))
                merged_pixel_offset += image.height
            elif images_merge_method == "horizontal":
                merged_image.paste(image, (merged_pixel_offset, 0))
                merged_pixel_offset += image.width

        self.queue.put(merged_image.save(join(self.tmp_dest_dir,
                                              images_merge_method,
                                              merged_image_name)))
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
        image_path_dest = join(self.tmp_dir_individual, card_file_name)

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
        processes = []

        if self.cache_mode == "name":
            image_paths_src = self.cache_mode_name()
        elif self.cache_mode == "sha512":
            image_paths_src = self.cache_mode_sha512()
        else:

            for image in listdir(images_dir):
                image_paths_src.append(join(images_dir, image))

        for image_path_src in image_paths_src:

            if not isdir(image_path_src):
                convert_single_p = Process(target=self.convert_single,
                                           args=(image_path_src, ppi))
                processes.append(convert_single_p)
                convert_single_p.start()

        for process in processes:
            process.join()

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
        processes = []

        for image in images:
            total_count += 1
            image_count += 1
            image_paths.append(join(tmp_dir_append, image))

            if image_count >= image_count_max:
                images_merge_p = Process(target=self.images_merge,
                                         args=(append_method, image_paths,
                                               str(total_count) + ".jpg"))
                processes.append(images_merge_p)
                images_merge_p.start()
                # Reset the count and paths if 2 (horizontal) or 4 (veritcal)
                # cards have been processed already.
                image_count = 0
                image_paths = []
            elif image_count < image_count_max:

                # If this is the last image, then merge all of the
                # remaining images.
                if total_count == number_of_images:

                    if not self.images_merge(append_method, image_paths,
                                             str(total_count) + ".jpg"):
                        return False

        for process in processes:
            process.join()

        return True

    def convert_to_pdf(self):
        """Convert all images from the horizontal directory into PDFs.

        Args:
            None
        """
        images = listdir(self.tmp_dir_horizontal)
        count = 0

        for image_name in images:
            pdf_data = img2pdf.convert(join(self.tmp_dir_horizontal, image_name))
            file = open(join(self.tmp_dir_pdfs, str(count) + ".pdf"), "wb")
            file.write(pdf_data)
            file.close()
            count += 1

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

        if not self.convert_to_pdf():
            return False

        return True
