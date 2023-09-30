import pathlib
import unittest

import settings


def create_config_file(mode_scheme: str = "light") -> None:
    original_lines = (
        "[view]",
        "# Valid values: light, dark and system",
        f"ModeScheme={mode_scheme}",
    )
    lines = [i + "\n" for i in original_lines]
    with open(".pynorc", "w") as file:
        file.writelines(lines)


class UserConfigurationCase(unittest.TestCase):
    def test_default_config(self) -> None:
        configuration = settings.TestConfiguration()
        configuration.set_user_configuration("")
        self.assertFalse(configuration.settings)

    def test_use_custom_config(self) -> None:
        create_config_file()
        configuration = settings.TestConfiguration()
        configuration.set_user_configuration(".pynorc")
        self.assertTrue(configuration.settings)
        pathlib.Path(".pynorc").unlink()


if __name__ == "__main__":
    unittest.main()
