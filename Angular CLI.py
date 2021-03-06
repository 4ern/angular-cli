# Imports
import os
import platform
import shlex
import subprocess
import sublime
import sublime_plugin

class AngularCliCommand(sublime_plugin.WindowCommand):

    def run(self, *arg, **kwargs):
        try:
            self.ProjectPath   = self.window.folders()[0]
            self.command       = kwargs.get('command', None)
            self.b_input       = kwargs.get('input', False)
            self.s_input_label = kwargs.get('input_label', False)
            self.b_options     = kwargs.get('options', False)
            self.s_message     = kwargs.get('message', None)
            self.b_output      = kwargs.get('output', True)
            self.b_disabled    = kwargs.get('disabled', False)
            self.args          = ["ng"]

            if self.b_disabled != True:
                if self.command == 'kill':
                    self.run_kill_command()
                elif self.command is not None:
                    self.run_command(self.command)
                else:
                    sublime.active_window().active_view().show_popup(content="No command entered", max_width=800)
            else:
                sublime.active_window().active_view().show_popup(content=self.s_message, max_width=800)

        except IndexError:
            sublime.active_window().active_view().show_popup(content="Please open or create an Angular Project", max_width=800)

    def run_command(self, command):
        self.args.extend(shlex.split(str(self.command)))
        if self.b_input is True:
            self.window.show_input_panel(self.s_input_label, "", self.on_input, None, None)
        else:
            if self.b_options == True:
                self.window.show_input_panel("[options]", "", self.on_options, None, None)
            else:
                self.execute_command()

    def on_input(self, input):
        self.args.extend(shlex.split(str(input)))
        if self.b_options == True:
            self.window.show_input_panel("[options]", "", self.on_options, None, None)
        else:
            self.execute_command()

    def on_options(self, input):
        self.args.extend(shlex.split(str(input)))
        self.execute_command()

    # Try to kill running ng serve by finding process bound to port 4200
    def run_kill_command(self):
        if platform.system() == 'Windows': # Tested on Windows 10
            # via: https://stackoverflow.com/questions/39091735/port-4200-is-already-in-use-when-running-the-ng-serve-command
            self.args = 'for /f "tokens=5" %a in (\'netstat -ano ^| find "4200" ^| find "LISTENING"\') do taskkill /f /pid %a'
            self.execute_command()
        elif platform.system() == 'Linux': # Tested on Ubuntu Desktop 18.04.3 LTS
            self.args = ['killall', 'ng serve']
            self.execute_command()
        elif platform.system() == 'Darwin': # AKA Mac, untested
            self.args = ['killall', 'ng serve']
            self.execute_command()
        else:
            sublime.active_window().active_view().show_popup(content="Unable to detect operating system", max_width=800)

    def execute_command(self):
        if os.name != 'posix' and self.command != 'kill':
            self.args = subprocess.list2cmdline(self.args)

        try:

            # exec command
            self.window.run_command("exec", {
                    "cmd": self.args,
                    "shell": os.name == 'nt',
                    "working_dir": self.ProjectPath
                })

            # Show Message if not Non
            if self.s_message != None:
                sublime.active_window().active_view().show_popup(content=self.s_message, flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY, max_width=600)

            # Show Output if True
            if self.b_output == False:
                self.window.run_command("hide_panel", {"panel": "output.exec"})
            else:
                self.window.run_command("show_panel", {"panel": "output.exec"})

        except (IOError, OSError) as e:
            sublime.error_message('IOError or OSError - command aborted. Error: {}'.format(e))
