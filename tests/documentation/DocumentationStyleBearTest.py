from queue import Queue
import os.path
import unittest

from coalib.settings.Section import Section
from coalib.testing.LocalBearTestHelper import execute_bear

from bears.documentation.DocumentationStyleBear import DocumentationStyleBear


def load_testfile(filename):
    filepath = os.path.join(os.path.dirname(__file__), "test_files",
                            "DocumentationStyleBear", filename)
    with open(filepath) as fl:
        return fl.read()


def test(test_file, expected_file):
    def test_function(self):
        test_file_content = load_testfile(test_file).splitlines(True)
        file_dict = {test_file: test_file_content}

        arguments = {'language': 'python', 'docstyle': 'default'}
        section = Section('test-section')
        for key, value in arguments.items():
            section[key] = value

        with execute_bear(
                DocumentationStyleBear(section, Queue()),
                test_file,
                test_file_content,
                **arguments) as results:

            for result in results:
                result.apply(file_dict)

        correct_file_dict = {
            test_file: load_testfile(expected_file).splitlines(True)}

        self.assertEqual(correct_file_dict, file_dict)

    return test_function


class DocumentationStyleBearTest(unittest.TestCase):
    test_bad1 = test("bad_file.py.test", "bad_file.py.test.correct")
    test_bad2 = test("bad_file2.py.test", "bad_file2.py.test.correct")
    test_bad3 = test("bad_file3.py.test", "bad_file3.py.test.correct")
    test_bad4 = test("bad_file4.py.test", "bad_file4.py.test.correct")
    test_good1 = test("good_file.py.test", "good_file.py.test")
    test_good2 = test("good_file2.py.test", "good_file2.py.test")
