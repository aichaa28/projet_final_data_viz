import unittest
from dataviz_claude.api import ask_claude

class TestClaudeAPI(unittest.TestCase):
    def test_api_response(self):
        response = ask_claude("Test?")
        self.assertTrue(isinstance(response, str))

if __name__ == "__main__":
    unittest.main()
