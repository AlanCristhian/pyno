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

            foreground="#cfcfcf",
            background="#282828",
            insertbackground="#ffffff",
            font=("Consolas", 16)
        )
        self.main.grid(row=0, column=0)


if __name__ == "__main__":
    app = App()
    app.deiconify()
    app.mainloop()
