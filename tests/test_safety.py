# Test safety module
import unittest
from src.safety import SafetyChecker

class TestSafety(unittest.TestCase):
    def test_is_safe(self):
        checker = SafetyChecker()
        self.assertTrue(checker.is_safe("ls"))

if __name__ == "__main__":
    unittest.main()
