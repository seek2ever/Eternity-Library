from tkinter import Tk, Label, Button, Frame, StringVar
import time


class CounterApp:
    def __init__(self, root):
        self.root = root
        self.counter = 0
        self.stopwatch_running = False
        self.stopwatch_start = 0
        self.stopwatch_time = "00:00:00"
        self.initUI()

    def initUI(self):
        self.root.title("计数器")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        self.center_window()

        main_frame = Frame(self.root)
        main_frame.pack(expand=True, fill='both')
        self.counter_var = StringVar()
        self.counter_var.set(str(self.counter))
        self.display = Label(main_frame, textvariable=self.counter_var, font=('Arial', 48))
        self.display.pack(expand=True)

        self.stopwatch_var = StringVar()
        self.stopwatch_var.set("00:00:00")
        self.stopwatch_display = Label(main_frame, textvariable=self.stopwatch_var, font=('Arial', 24))
        self.stopwatch_display.pack(expand=True)
        button_frame = Frame(main_frame)
        button_frame.pack(expand=True, fill='x', pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        btn_increment = Button(button_frame, text="+1", command=self.increment_counter, width=10, height=2)
        btn_increment.grid(row=0, column=1, padx=10)
        btn_reset = Button(button_frame, text="重置", command=self.reset_counter, width=10, height=2)
        btn_reset.grid(row=0, column=2, padx=10)

        self.update_stopwatch()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def increment_counter(self):
        self.counter += 1
        self.counter_var.set(str(self.counter))
        self.reset_stopwatch()

    def reset_counter(self):
        self.counter = 0
        self.counter_var.set(str(self.counter))
        self.reset_stopwatch()

    def reset_stopwatch(self):
        self.stopwatch_start = time.time()
        self.stopwatch_time = "00:00:00"
        self.stopwatch_var.set(self.stopwatch_time)

    def update_stopwatch(self):
        if self.stopwatch_start == 0:
            self.stopwatch_start = time.time()

        elapsed = time.time() - self.stopwatch_start
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        if hours > 99 or minutes > 99 or seconds > 99:
            self.reset_stopwatch()
        else:
            self.stopwatch_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.stopwatch_var.set(self.stopwatch_time)

        self.root.after(1000, self.update_stopwatch)


if __name__ == '__main__':
    root = Tk()
    app = CounterApp(root)
    root.mainloop()
