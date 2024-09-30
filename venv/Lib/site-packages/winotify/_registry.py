from os import path
import sys
import winreg

HKEY = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\Classes\{}"
SHELLKEY = r"shell\open\command"


class P:
    def __init__(self, p, s):
        self.p, self.s = p, s

    def __repr__(self): return self.s
    def __str__(self): return self.p


# path to python.exe
PY_EXE = P(path.join(path.dirname(sys.executable), "python.exe"), "PY_EXE")
# path to pythonw.exe
PYW_EXE = P(path.join(path.dirname(sys.executable), "pythonw.exe"), "PYW_EXE")



class InvalidKeyStructure(Exception): pass


class Registry:
    def __init__(self, app_id: str, executable=PY_EXE, script_path: str = '', *, force_override=False):
        """
        register app_id to Windows Registry as a protocol,
        eg. the app_id is "My Awesome App" can be called from browser or run.exe by typing "my-awesome-app:[Params]"
        Params can be a function name to call

        Args:
            app_id: your app name, make it readable to your user. It can contain spaces, however special characters
                    (eg. é) are not supported.
            executable: set the default interpreter or executable to run when a notification is clicked,
                        default is `PY_EXE` which is python.exe. To hide cmd flashing when a notification is clicked,
                        use `PYW_EXE`.
            script_path: The script path, usually `__file__`.
            force_override: If True, force replace the exists registry value in Windows Registry. Default is False.
                            Set it True if you want to change default interpreter or script path.

        Raises:
            InvalidKeyStructure: If `force_override` is True but the registry value is not created by winotify or
                                 the key structure is invalid.
        """

        self.app = format_name(app_id)
        self._key = SUBKEY.format(self.app)
        self.executable = executable
        self.path = script_path
        self._override = force_override

        self.reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        self._register()

    def _validate_structure(self):
        key = winreg.OpenKey(self.reg, self._key)
        try:
            winreg.OpenKey(key, SHELLKEY).Close()
        except WindowsError:
            raise InvalidKeyStructure(f'The registry from "{self.app}" was not created by winotify or the structure '
                                      f'is invalid')

    def _key_exist(self) -> bool:
        try:
            winreg.OpenKey(HKEY, self._key).Close()
            return True
        except WindowsError:
            return False

    def _register(self):

        if self._key_exist() and self._override:
            self._validate_structure()  # validate

        key = winreg.CreateKey(self.reg, self._key)
        with key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f"URL:{self.app}")
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
            subkey = winreg.CreateKey(key, SHELLKEY)
            with subkey:
                winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, f'{self.executable} {self.path} %1')


def format_name(name: str):
    return name.replace(' ', '-')
