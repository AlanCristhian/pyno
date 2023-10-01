import ctypes
import tkinter

import settings


class App(tkinter.Tk, settings.TkConfiguration):

    def __init__(self) -> None:
        super().__init__()
        settings.TkConfiguration.__init__(self, self)

        self.set_user_configuration("test_settings.ini")

        # Create each widget
        self.main = tkinter.Text(
            self,
            relief="flat",
            borderwidth=0,
            padx=0,
            pady=0,
            font=self.configuration.font,
            **self.configuration.main,
        )
        self.main.grid(row=0, column=0,
            sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)
        self.main.grid_columnconfigure(0, weight=1)
        self.monitor_color_mode(self.filename)


if __name__ == "__main__":
    app = App()
    app.deiconify()
    app.main.focus_set()
    app.mainloop()
