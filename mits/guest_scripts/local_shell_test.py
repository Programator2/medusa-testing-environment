import unittest
from local_shell import LocalShell


class LocalShellTest(unittest.TestCase):
    def test_execute_cmd_returns_stdout(self):
        cmd = 'echo test'
        shell = LocalShell()
        result = shell.execute_cmd(cmd)
        self.assertEqual(result, 'test\n')

    def test_execute_cmd_empty_value_error(self):
        shell = LocalShell()
        with self.assertRaises(ValueError):
            shell.execute_cmd('')


    def test_execute_cmd_none_type_error(self):
        shell = LocalShell()
        with self.assertRaises(TypeError):
            shell.execute_cmd(None)


if __name__ == '__main__':
    unittest.main()
