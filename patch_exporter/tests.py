import unittest

from patch_exporter.helper import BoundingBox


class TestBoundingBoxIntersection(unittest.TestCase):
    def test_partial_overlap(self):
        """
        Test case where the two bounding boxes partially overlap.
        """
        box1 = BoundingBox.from_coords(1, 1, 5, 5)
        box2 = BoundingBox.from_coords(3, 3, 7, 7)
        intersection_box = box1.intersection(box2)
        intersection_box2 = box2.intersection(box1)

        self.assertIsNotNone(intersection_box)
        self.assertEqual(intersection_box, BoundingBox.from_coords(3, 3, 5, 5))
        self.assertEqual(intersection_box.area, intersection_box2.area)
        self.assertEqual(intersection_box.area, 4)

    def test_no_overlap(self):
        """
        Test case where the two bounding boxes do not overlap at all.
        """
        box1 = BoundingBox.from_coords(1, 1, 3, 3)
        box2 = BoundingBox.from_coords(4, 4, 6, 6)
        intersection_box = box1.intersection(box2)

        self.assertIsNone(intersection_box)

    def test_contained(self):
        """
        Test case where one bounding box is completely contained within the other.
        """
        box1 = BoundingBox.from_coords(1, 1, 10, 10)
        box2 = BoundingBox.from_coords(3, 3, 6, 6)
        intersection_box = box1.intersection(box2)
        intersection_box2 = box2.intersection(box1)

        self.assertIsNotNone(intersection_box)
        self.assertEqual(intersection_box, BoundingBox.from_coords(3, 3, 6, 6))
        self.assertEqual(intersection_box.area, intersection_box2.area)
        self.assertEqual(intersection_box.area, 9)

    def test_identical_boxes(self):
        """
        Test case where the two bounding boxes are exactly the same.
        """
        box1 = BoundingBox.from_coords(2, 2, 8, 8)
        box2 = BoundingBox.from_coords(2, 2, 8, 8)
        intersection_box = box1.intersection(box2)

        self.assertIsNotNone(intersection_box)
        self.assertEqual(intersection_box, BoundingBox.from_coords(2, 2, 8, 8))
        self.assertEqual(intersection_box.area, 36)


if __name__ == "__main__":
    unittest.main()
