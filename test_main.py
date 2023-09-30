import gc
import sys
import tkinter
import unittest

import main


def get_dpi_awareness() -> bool:
    import ctypes
    import ctypes.wintypes

    dpi_aware = (
        ctypes.wintypes.HANDLE(-2),
        ctypes.wintypes.HANDLE(-3),
        ctypes.wintypes.HANDLE(-4),
    )
    dpi_unaware = (
        ctypes.wintypes.HANDLE(-1),
        ctypes.wintypes.HANDLE(-5),
    )
    awareness = ctypes.windll.user32.GetThreadDpiAwarenessContext()
    for value in (*dpi_aware, *dpi_unaware):
        if ctypes.windll.user32.AreDpiAwarenessContextsEqual(awareness, value):
            return value in dpi_aware
    raise ValueError(f'Unknown DPI context type ({awareness!r})')


class BaseCase(unittest.TestCase):
    app: main.App

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = main.App()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.update_idletasks()
        cls.app.destroy()
        del cls.app
        gc.collect()

    def tearDown(self) -> None:
        self.app.update()


class AppCase(BaseCase):

    def test_instance(self) -> None:
        self.assertIsInstance(self.app, tkinter.Tk)


class MainWidget(BaseCase):

    @unittest.skipUnless(sys.platform.startswith("win"), "Requires Windows")
    def test_dpi_awareness_on_windows(self) -> None:
        self.assertTrue(get_dpi_awareness())

    def test_instance(self) -> None:
        self.assertIsInstance(self.app.main, tkinter.Text)

    def test_visibility_on_grid(self) -> None:
        self.assertTrue(self.app.main.winfo_manager())

    def test_default_config(self) -> None:
        self.assertEqual(self.app.main["relief"], "flat")
        self.assertEqual(self.app.main["borderwidth"], 0)
        self.assertEqual(self.app.main["padx"], 0)
        self.assertEqual(self.app.main["pady"], 0)
        self.assertEqual(self.app.main["foreground"], "#cfcfcf")
        self.assertEqual(self.app.main["background"], "#282828")
        self.assertEqual(self.app.main["insertbackground"], "#ffffff")


if __name__ == "__main__":
    unittest.main()
