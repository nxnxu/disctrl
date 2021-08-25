import subprocess
import os
import tkinter as tk

# TODO Check exceptions while running commands
# TODO A label to show error messages
# TODO Script needs sudo permission
# TODO Fix backlight maximum value, currently it is set to 100

SCRIPT_DIR = os.path.dirname(__file__)


def execute_shell_command(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout.decode('ascii'), stderr.decode('ascii'), str(proc.returncode)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.create_brightness_widget()
        self.create_backlight_widget()
        self.create_redshift_widget()
        self.set_scale_values()

    def create_brightness_widget(self):
        self.brightness = tk.Scale(self.master, from_=1, to=100, length=200, command=self.change_brightness,
                                   orient=tk.HORIZONTAL)
        self.brightness.pack(side="top")
        self.l1 = tk.Label(self.master, text='Brightness')
        self.l1.pack(side='top')

    def create_backlight_widget(self):
        self.backlight = tk.Scale(self.master, from_=1, to=100, length=200, command=self.change_backlight,
                                  orient=tk.HORIZONTAL)
        self.backlight.pack(side="top")
        self.l2 = tk.Label(self.master, text='Backlight')
        self.l2.pack(side='top')

    def create_redshift_widget(self):
        redshift_frame = tk.Frame(self.master)
        redshift_frame.pack(side='top')
        reset_redshift_button = tk.Button(redshift_frame, text="Reset RedShift", command=self.reset_redshift)
        redshift_button = tk.Button(redshift_frame, text="RedShift", command=self.redshift)
        reset_redshift_button.pack(side="left")
        redshift_button.pack(side="left")

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

    def reset_redshift(self):
        cmd = 'redshift -x'
        execute_shell_command(cmd)
        self.set_scale_values()


root = tk.Tk()
root.title('disctrl')
root.geometry('300x200')
app = Application(master=root)
app.mainloop()
