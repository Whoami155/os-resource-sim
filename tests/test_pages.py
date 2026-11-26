import unittest

from simulators import replace_pages


class PageReplacementTests(unittest.TestCase):
    def test_reference_workload(self):
        pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        for policy, expected in [('FIFO', 10), ('LRU', 9), ('OPT', 7)]:
            with self.subTest(policy=policy):
                trace, faults = replace_pages(pages, 3, policy)
                self.assertEqual(faults, expected)
                self.assertEqual(len(trace), len(pages))
                self.assertTrue(all(len(frames) <= 3 for _, frames, _ in trace))

    def test_invalid_frame_count(self):
        with self.assertRaises(ValueError):
            replace_pages([0], 0, 'FIFO')
