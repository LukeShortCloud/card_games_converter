#!/usr/bin/env python3

import tempfile
import unittest
from os import listdir, makedirs, remove
from os.path import basename, exists, isfile, join
from shutil import copyfile, rmtree
from PIL import Image
import urllib.request
import ssl
from cgc.cgc import CGC


class CGCUnitTests(unittest.TestCase):

    def setUp(self):
        self.tmp_root_dir = tempfile.gettempdir()
        self.cards_source_dir = join(self.tmp_root_dir, "cards")
        self.last_image_card = join(self.tmp_root_dir, "cards", "9.jpg")
        self.example_card_url = "https://swtcgidc.files.wordpress.com/2018/08/card-of-the-week-bosb029_starkiller_base_b.jpg"

        if not exists(self.cards_source_dir):
            makedirs(self.cards_source_dir)

        if not exists(self.last_image_card):
            # The certificate reports false-positive errors.
            ssl._create_default_https_context = ssl._create_unverified_context
            urllib.request.urlretrieve(self.example_card_url,
                                       self.last_image_card)

        # Copy the image 8 times (for a total of 9 images).
        for count in range(1, 9):
            copyfile(self.last_image_card, join(self.cards_source_dir,
                                                str(count) + ".jpg"))

        self.cgc = CGC(log_level="DEBUG")
        self.tmp_card = join(self.cgc.tmp_dest_dir, "123.jpg")

    def test_find_first_image(self):
        return_status = False
        first_image_found = self.cgc.find_first_image(self.cards_source_dir)

        # The first card found can actually be any file in the directory
        # since it is not sorted (and does not need to be sorted).
        for image in listdir(self.cards_source_dir):
            image_name_full = join(self.cards_source_dir, image)

            if image_name_full == first_image_found:
                return_status = True

        self.assertTrue(return_status)

    def test_image_info(self):
        get_image_info = self.cgc.image_info(self.last_image_card)

        for measurement in get_image_info:

            if not isinstance(measurement, int):
                self.assertTrue(False)

    def test_calc_ppi(self):
        image_dimensions = [364, 260]
        self.assertEqual(self.cgc.calc_ppi(image_dimensions), 104)

    def test_image_rotate(self):
        image_dimensions_old = self.cgc.image_info(self.last_image_card)
        return_status = self.cgc.image_rotate(self.last_image_card,
                                                self.tmp_card)
        image_dimensions_new = self.cgc.image_info(self.tmp_card)

        # The dimensions should be different after rotating.
        if (image_dimensions_old[0] == image_dimensions_new[0]) or \
           (not return_status):
            self.assertTrue(False)

    def test_image_rotate_by_dimensions(self):
        rotate_image = join(self.cgc.tmp_dest_dir, "rotate.jpg")
        copyfile(self.last_image_card, rotate_image)
        # Return a list of: width, height
        rotate_image_original = self.cgc.image_info(rotate_image)
        return_status = self.cgc.image_rotate_by_dimensions(rotate_image)
        rotate_image_new = self.cgc.image_info(rotate_image)

        if not return_status:
            self.assertTrue(False)

        # Images only get rotated if the width is larger than the height.
        if rotate_image_original[1] < rotate_image_original[0]:
            self.assertTrue(rotate_image_new[1] < rotate_image_new[0])

        if rotate_image_original[1] > rotate_image_original[0]:
            self.assertTrue(rotate_image_new[1] < rotate_image_new[0])

    def test_image_density_change(self):
        # Set a temporary card to have the pixels per inch density of 104.
        self.cgc.image_density_change(self.last_image_card,
                                      self.tmp_card, 104)
        image = Image.open(self.tmp_card)
        print("IMAGE DENSITY: {}".format(image.info["dpi"]))

        # Both the X and Y resolution dimensions should have the same density.
        if image.info["dpi"][0] != 104 or image.info["dpi"][1] != 104:
            self.assertTrue(False)

    def test_images_merge(self):
        card_1 = join(self.cgc.tmp_src_dir, "1.jpg")
        card_2 = join(self.cgc.tmp_src_dir, "2.jpg")
        image_paths = [card_1, card_2]
        cards_merged_full_path = join(tempfile.gettempdir(), "cgc", "vertical", "merged.jpg")
        cards_merged = basename(cards_merged_full_path)

        if (not self.cgc.images_merge("vertical", image_paths, cards_merged)) \
            or (not isfile(cards_merged_full_path)):
            self.assertTrue(False)

        remove(cards_merged_full_path)

    def test_convert_single(self, cache_mode=None):

        if cache_mode == "name" or cache_mode == "sha512":
            self.cgc.cache_mode = cache_mode

        test_image_src = join(self.cgc.tmp_src_dir, "single.jpg")
        test_image_dest = join(self.cgc.tmp_dir_individual, "single.jpg")
        copyfile(join(self.cgc.tmp_src_dir, "1.jpg"), test_image_src)

        if not self.cgc.convert_single(test_image_src):
            self.assertTrue(False)
            return False

        remove(test_image_src)
        remove(test_image_dest)
        return True

    def test_convert_single_cache(self):

        for cache_mode in ["name", "sha512"]:
            self.assertTrue(self.test_convert_single(cache_mode))

    def test_convert_batch_directory(self):
        return_status = self.cgc.convert_batch_directory(self.cards_source_dir)
        individual_images = listdir(self.cgc.tmp_dir_individual)

        # There should be a total of nine cards converted from this test.
        if (len(individual_images) != 9) or (not return_status):
            self.assertTrue(False)

    def test_convert_batch_append_all(self):
        return_status = self.cgc.convert_batch_append_all()
        self.cgc.convert_batch_append_all()
        listdir_vertical = listdir(self.cgc.tmp_dir_vertical)
        listdir_horizontal = listdir(self.cgc.tmp_dir_horizontal)

        # There should be 3 vertical images (each with 1, 4, and 4 images).
        if len(listdir_vertical) != 3:
            self.assertTrue(False)
        # There should be 2 horizontal images (each with 1 and 8 images
        # or with 4 and 5 images).
        elif len(listdir_horizontal) != 2:
            self.assertTrue(False)
        elif return_status == False:
            self.assertTrue(False)

    def tearDown(self):
        rmtree(self.cards_source_dir)
        rmtree(self.cgc.tmp_dest_dir)


if __name__ == '__main__':
    unittest.main()
