"""Unit tests for the template module."""

import os
import shutil
import tempfile
import unittest
from kattis_cli import template


class TestTemplate(unittest.TestCase):
    """Unit tests for the template module.
    """

    def setUp(self) -> None:
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_create_python_template(self) -> None:
        """Test python template."""
        template.create_template('python', 'testprob')
        print(os.path.curdir)
        self.assertTrue(os.path.exists('testprob.py'))
        with open('testprob.py', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('def main() -> None:', content)

    def test_create_java_template(self) -> None:
        """Test Java template."""
        template.create_template('java', 'testprob')
        self.assertTrue(os.path.exists('Testprob.java'))
        with open('Testprob.java', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('public class Testprob {', content)

    def test_create_cpp_template(self) -> None:
        """Test CPP template."""
        template.create_template('cpp', 'testprob')
        self.assertTrue(os.path.exists('testprob.cpp'))
        with open('testprob.cpp', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('#include <iostream>', content)

    def test_invalid_language(self) -> None:
        """Test invalid language"""
        template.create_template('invalid_lang', 'testprob')
        self.assertFalse(os.path.exists('testprob.invalid_lang'))

    def test_create_python_template_src(self) -> None:
        """Test python src style project structure"""
        template.create_template('python3', 'cold', True)
        file_path = os.path.join('src', 'cold', 'cold.py')
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.exists(os.path.join('tests', 'test_cold.py')))
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('def main() -> None:', content)
            self.assertIn('if __name__ == "__main__":', content)
