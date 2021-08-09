import unittest

from main import getType

class ScraperTests(unittest.TestCase):
    def test_get_type(self):
        tests = (
            ('[GB] GMK Trüffelschwein // August 5 - September 6, 2021', 0),
            ('[GB] KAT Overgrown // August 5 - September 5, 2021', 0),
            ('[GB] ePBT Acid House and Sweet Girl // August 5 - September 5', 0),
            ('[In-Stock] DROP + MARVEL MT3 Black Panther // August 2, 2021', 0)
            ('[GB] Harimau & Penyu Switch // August 8 - August 31, 2021', 1),
            ('[GB] Latrialum Deskmat // August 6 - August 20, 2021', 2),
            ('[GB] Freebird60 // August 2 - September 2, 2021', 3),
            ('[GB] LW-67 // July 31 - August 31, 2021', 3),
            ('[GB] Alter Keyboard // July 21 - August 2, 2021', 3)
            ('[GB] Work Louder // August 5, 2021 - 100 units', 4)
        )
        for title, output in tests:
            with self.subTest():
                self.assertEqual(getType(title), output)
