from typing import override

import abc
import ctypes
import configparser
import pathlib
import sys
import tkinter

import darkdetect  # type: ignore[import]


TConfig = configparser.ConfigParser | None


class Base(metaclass=abc.ABCMeta):
    def set_user_configuration(self, filename: str) -> None:
        if filename:
            self.settings: TConfig = configparser.ConfigParser()
            self.settings.read(filename)
        else:
            self.settings = self.load_settings("pyno")

        if not self.settings:
            return

        if self.settings["view"]["ModeScheme"] == "light":
            self.set_light_theme()
        elif self.settings["view"]["ModeScheme"] == "dark":
            self.set_dark_theme()
        elif self.settings["view"]["ModeScheme"] == "system":
            if darkdetect.isDark():
                self.set_dark_theme()
            else:
                self.set_light_theme()
        else:
            self.set_notify_error(ValueError("view.ModelScheme"))

    def load_settings(self, app_name: str) -> TConfig:
        home = pathlib.Path.home()
        etc = pathlib.Path("/etc")
        files = [
            etc/app_name/"config",
            etc/f"{app_name}rc",
            home/".config"/app_name/"config",
            home/".config"/app_name,
            home/f".{app_name}"/"config",
            home/f".{app_name}rc",
            pathlib.Path(f".{app_name}rc"),
        ]

        all_parts = pathlib.Path().absolute().parts
        user_parts: list[pathlib.Path] = []
        for i in reversed(all_parts):
            if i == "home":
                user_parts.reverse()
                break
            else:
                user_parts.append(pathlib.Path(i)/f".{app_name}rc")

        files.extend(user_parts)

        existent_files = [i for i in files if i.is_file()]
        if existent_files:
            settings = configparser.ConfigParser()
            settings.read(existent_files)
            return settings
        else:
            return None

    @abc.abstractmethod
    def set_light_theme(self) -> None:
        pass

    @abc.abstractmethod
    def set_dark_theme(self) -> None:
        pass

    @abc.abstractmethod
    def set_notify_error(self, error: Exception) -> None:
        pass


class TestConfiguration(Base):

    @override
    def set_light_theme(self) -> None:
        pass

    @override
    def set_dark_theme(self) -> None:
        pass

    @override
    def set_notify_error(self, error: Exception) -> None:
        pass


class TkConfiguration(Base):

    def __init__(self, root: tkinter.Tk) -> None:
        self.root = root

    @override
    def set_user_configuration(self, filename: str = "") -> None:
        if sys.platform == "win32":

            # The tkinter theme is white. So if the app change the theme, first
            # The default is vibible an then it change. To avoid that, i hide
            # the app until the theme is fully loaded.
            self.root.withdraw()
            try:

                # Set high dpi resolution
                ctypes.windll.shcore.SetProcessDpiAwareness(True)
            except (AttributeError, OSError):
                pass

        super().set_user_configuration(filename)

    @override
    def set_light_theme(self) -> None:
        pass

    @override
    def set_dark_theme(self) -> None:
        if sys.platform == "win32":

            # Set dark title bar
            if darkdetect.isDark():
                self.root.update()
                parent_window = ctypes.windll.user32.GetParent(
                    self.root.winfo_id())
                rendering_policy = 20
                value = ctypes.c_int(True)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    parent_window,
                    rendering_policy,
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )

    @override
    def set_notify_error(self, error: Exception) -> None:
        pass
