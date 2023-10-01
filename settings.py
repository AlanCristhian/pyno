from tkinter import font
from typing import override

import abc
import ctypes
import configparser
import pathlib
import sys
import tkinter
import dataclasses

import darkdetect  # type: ignore[import]


type TConfig = configparser.ConfigParser | None


import time
import os


INI_TO_MAIN = {
    "highlightforegroundcolour": "selectforeground",
    "highlightbackgroundcolour": "selectbackground",
    "foregroundcolour": "foreground",
    "backgroundcolour": "background",
    "cursorcolour": "insertbackground",
}


@dataclasses.dataclass
class TkConfig:
    main: dict[str, str]
    font: tuple[str, int, str]


class Base(metaclass=abc.ABCMeta):
    config: TkConfig
    font: tuple[str, int, str]
    filename: str

    def set_user_configuration(self, filename: str) -> None:
        if filename:
            self.filename = filename
            self.settings: TConfig = configparser.ConfigParser()
            self.settings.read(filename)
        else:
            self.settings = self.load_settings("pyno")

        if not self.settings:
            return

        if self.settings["view"]["ColorMode"] == "light":
            self.set_light_theme()
        elif self.settings["view"]["ColorMode"] == "dark":
            self.set_dark_theme()
        elif self.settings["view"]["ColorMode"] == "system":
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
            home/".configuration"/app_name/"config",
            home/".configuration"/app_name,
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
        self.delay = 1000//1

        # The tkinter theme is white. So if the app change the theme, first
        # The default is vibible an then it change. To avoid that, i hide
        # the app until the theme is fully loaded.
        self.root.withdraw()
        self.root.bind("<<update-settings>>", self.update_settings)

    def monitor_color_mode(self, file):
        try:
            new_time = os.path.getmtime(file)
            new_color_mode = darkdetect.isDark()
            if new_time != self.old_time:
                self.old_time = new_time
                self.root.event_generate("<<update-settings>>")
            elif new_color_mode != self.old_color_mode:
                self.old_color_mode = new_color_mode
                self.root.event_generate("<<update-settings>>")
            self.root.after(1000, lambda: self.monitor_color_mode(file))
        except Exception as error:
            self.root.after_cancel(next_frame)

    def update_settings(self, event):
        self.set_user_configuration(self.filename)
        self.update_theme()

    def load_font(self) -> None:
        default_font = font.nametofont("TkFixedFont").actual()

        font_size = self.settings["view"]["FontHeight"]
        if font_size in {"system", ""}:
            font_size = default_font["size"]
        elif isinstance(font_size, int):
            default_font["size"] = font_size
        else:
            self.set_notify_error(ValueError("FontSize must be an integer."))

        font_family = self.settings["view"]["Font"]
        if font_family != "system":
            if font_family in font.families():
                self.default_font = (font_family, font_size, "normal")
            else:
                self.set_notify_error(
                    ValueError(f"{font_family} was not found."))
                self.default_font = tuple(default_font.values())[:3]
        elif sys.platform == "win32":
            if "Cascadia Code" in font.families():
                self.default_font = ("Cascadia Mono", font_size, "normal")
            elif "Consolas" in font.families():
                self.default_font = ("Consolas", font_size, "normal")
            else:
                self.default_font = tuple(default_font.values())[:3]
        elif sys.platform == "darwin":
            if "SF Mono" in font.families():
                self.default_font = ("SF Mono", font_size, "normal")
            elif "Menlo" in font.families():
                self.default_font = ("Menlo", font_size, "normal")
            else:
                self.default_font = tuple(default_font.values())[:3]
        elif sys.platform in {"linux", "linux2"}:
            if "Ubuntu Mono" in font.families():
                self.default_font = ("Ubuntu Mono", font_size, "normal")
            elif "DejaVu Sans Mono" in font.families():
                self.default_font = ("DejaVu Sans Mono", font_size, "normal")
            else:
                self.default_font = tuple(default_font.values())[:3]
        else:
            self.default_font = tuple(default_font.values())[:3]

        return self.default_font

    @override
    def set_user_configuration(self, filename: str = "") -> None:
        if sys.platform == "win32":
            try:
                # Set high dpi resolution
                ctypes.windll.shcore.SetProcessDpiAwareness(True)
            except (AttributeError, OSError):
                pass

        self.old_color_mode = darkdetect.isDark()
        super().set_user_configuration(filename)
        self.old_time = os.path.getmtime(filename)

    @override
    def set_light_theme(self) -> None:
        if sys.platform == "win32":

            # Set light title bar
            if self.settings["view"]["ColorMode"] == "system" \
            and darkdetect.isDark() \
            or self.settings["view"]["ColorMode"] == "light":
                self.root.update()
                parent_window = ctypes.windll.user32.GetParent(
                    self.root.winfo_id())
                rendering_policy = 20
                set_dark_mode = ctypes.c_int(False)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    parent_window,
                    rendering_policy,
                    ctypes.byref(set_dark_mode),
                    ctypes.sizeof(set_dark_mode)
                )
        self.configuration = TkConfig(
            main={
                INI_TO_MAIN[k]: v
                for k, v in self.settings["light"].items()
                if k in INI_TO_MAIN
            },
            font=self.load_font()
        )

    @override
    def set_dark_theme(self) -> None:
        if sys.platform == "win32":

            # Set dark title bar
            if self.settings["view"]["ColorMode"] == "system" \
            and darkdetect.isDark() \
            or self.settings["view"]["ColorMode"] == "dark":
                self.root.update()
                parent_window = ctypes.windll.user32.GetParent(
                    self.root.winfo_id())
                rendering_policy = 20
                set_dark_mode = ctypes.c_int(True)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    parent_window,
                    rendering_policy,
                    ctypes.byref(set_dark_mode),
                    ctypes.sizeof(set_dark_mode)
                )

        self.configuration = TkConfig(
            main={
                INI_TO_MAIN[k]: v
                for k, v in self.settings["dark"].items()
                if k in INI_TO_MAIN
            },
            font=self.load_font(),
        )

    def update_theme(self):
        if sys.platform == "win32" \
        and self.settings["view"]["ColorMode"] == "system":
            self.root.update()
            parent_window = ctypes.windll.user32.GetParent(
                self.root.winfo_id())
            rendering_policy = 20
            set_dark_mode = ctypes.c_int(darkdetect.isDark())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                parent_window,
                rendering_policy,
                ctypes.byref(set_dark_mode),
                ctypes.sizeof(set_dark_mode)
            )
        self.main.config(
            font=self.configuration.font,
            **self.configuration.main,
        )

    @override
    def set_notify_error(self, error: Exception) -> None:
        pass
