import subprocess
import os
import tkinter as tk

# TODO Check exceptions while running commands
# TODO A label to show error messages
# TODO Script needs sudo permission
# TODO Fix backlight maximum value, currently it is set to 100

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = '.'


def execute_shell_command(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout.decode('ascii'), stderr.decode('ascii'), str(proc.returncode)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.settings = []
        self.redshift_count = 0
        self.master = master
        self.pack()
        self.load_settings()
        self.create_widgets()

    def load_settings(self):
        open(f"{SCRIPT_DIR}/settings", "a").close()
        with open(f"{SCRIPT_DIR}/settings", "r") as f:
            for setting in f.readlines():
                setting = setting.strip().split(";")
                setting[1], setting[2], setting[3] = map(int, setting[1:])
                self.settings.append(tuple(setting))
            f.close()

    def create_widgets(self):
        self.create_brightness_widget()
        self.create_backlight_widget()
        self.create_redshift_widget()
        self.create_setting_widget()
        self.set_scale_values()

    def create_brightness_widget(self):
        self.brightness = tk.Scale(self.master, from_=1, to=100, length=200, command=self.change_brightness,
                                   orient=tk.HORIZONTAL)
        self.brightness.pack(side="top")
        tk.Label(self.master, text='Brightness').pack(side='top')

    def create_backlight_widget(self):
        self.backlight = tk.Scale(self.master, from_=1, to=100, length=200, command=self.change_backlight,
                                  orient=tk.HORIZONTAL)
        self.backlight.pack(side="top")
        tk.Label(self.master, text='Backlight').pack(side='top')

    def create_redshift_widget(self):
        redshift_frame = tk.Frame(self.master)
        redshift_frame.pack(side='top')
        reset_redshift_button = tk.Button(redshift_frame, text="Reset RedShift", command=self.reset_redshift)
        redshift_button = tk.Button(redshift_frame, text="RedShift", command=self.redshift)
        reset_redshift_button.pack(side="left")
        redshift_button.pack(side="left")

    def create_setting_widget(self):

        def set_setting(setting):
            brightness, backlight, redshift_count = setting[1:]
            self.change_brightness(brightness)
            self.change_backlight(backlight)
            if self.redshift_count != redshift_count:
                self.reset_redshift()
                for i in range(redshift_count):
                    self.redshift()

        def save_setting(name, parent_frame):
            if name and name not in [i[0] for i in self.settings]:
                s = (name, self.query_brightness(), self.query_backlight(), self.redshift_count)
                self.settings.append(s)
                with open(f"{SCRIPT_DIR}/settings", "a") as f:
                    value = ";".join(str(i) for i in s)
                    f.write(f"{value}\n")
                    f.close()
                row = len(self.settings) - 1
                tk.Label(parent_frame, text=s[0]).grid(row=row, column=0)
                tk.Button(parent_frame, text="Set", command=lambda: set_setting(s)).grid(row=row, column=1)

        frame1 = tk.Frame(self.master)
        frame2 = tk.Frame(self.master)
        entry = tk.Entry(frame1, bd=5)
        button = tk.Button(frame1, text="Save Setting", command=lambda: save_setting(entry.get(), frame2))

        frame1.pack(side="top", pady=(20, 0))
        entry.pack(side="left")
        button.pack(side="right")
        frame2.pack(side="top", pady=(20, 0))

        for index, setting in enumerate(self.settings):
            def func(index=index):
                set_setting(self.settings[index])

            tk.Label(frame2, text=setting[0]).grid(row=index, column=0)
            tk.Button(frame2, text="Set", command=func).grid(row=index, column=1)

    def set_scale_values(self):
        self.brightness.set(self.query_brightness())
        self.backlight.set(self.query_backlight())

    def query_brightness(self):
        cmd = f'{SCRIPT_DIR}/query_brightness.sh'
        return int(execute_shell_command(cmd)[0])

    def query_backlight(self):
        cmd = f'{SCRIPT_DIR}/query_backlight.sh'
        return int(execute_shell_command(cmd)[0])

    def change_brightness(self, brightness):
        cmd = f'sudo {SCRIPT_DIR}/change_brightness.sh {brightness}'
        execute_shell_command(cmd)
        self.set_scale_values()

    def change_backlight(self, backlight):
        cmd = f'sudo {SCRIPT_DIR}/change_backlight.sh {backlight}'
        execute_shell_command(cmd)
        self.set_scale_values()

    def redshift(self):
        cmd = 'redshift -O 4500'
        execute_shell_command(cmd)
        self.set_scale_values()
        self.redshift_count += 1

    def reset_redshift(self):
        cmd = 'redshift -x'
        execute_shell_command(cmd)
        self.set_scale_values()
        self.redshift_count = 0


root = tk.Tk()
root.title('disctrl - Display Controller')
app = Application(master=root)
app.mainloop()
