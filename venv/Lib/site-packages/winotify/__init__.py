"""
.. include:: ./documentation.md
"""


import queue
import os
import subprocess
import sys
import atexit
from tempfile import gettempdir
from typing import Callable, Union

from winotify import audio
from winotify._registry import Registry, format_name, PY_EXE, PYW_EXE
from winotify._communication import Listener, Sender


__author__ = "Versa Syahputra"
__version__ = "1.1.0"
__all__ = ["Notifier", "Notification", "Registry", "audio"]


TEMPLATE = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$Template = @"
<toast {launch} duration="{duration}">
    <visual>
        <binding template="ToastImageAndText02">
            <image id="1" src="{icon}" />
            <text id="1"><![CDATA[{title}]]></text>
            <text id="2"><![CDATA[{msg}]]></text>
        </binding>
    </visual>
    <actions>
        {actions}
    </actions>
    {audio}
</toast>
"@

$SerializedXml = New-Object Windows.Data.Xml.Dom.XmlDocument
$SerializedXml.LoadXml($Template)

$Toast = [Windows.UI.Notifications.ToastNotification]::new($SerializedXml)
$Toast.Tag = "{tag}"
$Toast.Group = "{group}"

$Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{app_id}")
$Notifier.Show($Toast);
"""

tempdir = gettempdir()


def _run_ps(*, file='', command=''):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass"]
    if file and command:
        raise ValueError
    elif file:
        cmd.extend(["-file", file])
    elif command:
        cmd.extend(['-Command', command])
    else:
        raise ValueError

    subprocess.Popen(
        cmd,
        # stdin, stdout, and stderr have to be defined here, because windows tries to duplicate these if not null
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,  # set to null because we don't need the output :)
        stderr=subprocess.DEVNULL,
        startupinfo=si
    )


class Notification(object):
    def __init__(self,
                 app_id: str,
                 title: str,
                 msg: str = "",
                 icon: str = "",
                 duration: str = 'short',
                 launch: str = ''):
        """
        Construct a new notification

        Args:
            app_id: your app name, make it readable to your user. It can contain spaces, however special characters
                    (eg. é) are not supported.
            title: The heading of the toast.
            msg: The content/message of the toast.
            icon: An optional path to an image to display on the left of the title & message.
                  Make sure the path is absolute.
            duration: How long the toast should show up for (short/long), default is short.
            launch: The url or callback to launch (invoked when the user clicks the notification)

        Notes:
            If you want to pass a callback to `launch` parameter,
            please use `create_notification` from `Notifier` object

        Raises:
            ValueError: If the duration specified is not short or long
        """

        self.app_id = app_id
        self.title = title
        self.msg = msg
        self.icon = icon
        self.duration = duration
        self.launch = launch
        self.audio = audio.Silent
        self.tag = self.title
        self.group = self.app_id
        self.actions = []
        self.script = ""
        if duration not in ("short", "long"):
            raise ValueError("Duration is not 'short' or 'long'")

    def set_audio(self, sound: audio.Sound, loop: bool):
        """
        Set the audio for the notification

        Args:
            sound: The audio to play when the notification is showing. Choose one from `winotify.audio` module,
                   (eg. audio.Default). The default for all notification is silent.
            loop: If True, the audio will play indefinitely until user click or dismis the notification.

        """

        self.audio = '<audio src="{}" loop="{}" />'.format(sound, str(loop).lower())

    def add_actions(self, label: str, launch: Union[str, Callable] = ""):
        """
        Add buttons to the notification. Each notification can have 5 buttons max.

        Args:
            label: The label of the button
            launch: The url to launch when clicking the button, 'file:///' protocol is allowed. Or a registered
                    callback function

        Returns: None

        Notes:
            Register a callback function using `Notifier.register_callback()` decorator before passing it here

        Raises:
              ValueError: If the callback function is not registered
        """

        if callable(launch):
            if hasattr(launch, 'url'):
                url = launch.url
            else:
                raise ValueError(f"{launch} is not registered")
        else:
            url = launch

        xml = '<action activationType="protocol" content="{label}" arguments="{link}" />'
        if len(self.actions) < 5:
            self.actions.append(xml.format(label=label, link=url))

    def build(self):
        """
        This method is deprecated, call `Notification.show()` directly instead.

        Warnings:
            DeprecationWarning

        """
        import warnings
        warnings.warn("build method is deprecated, call show directly instead", DeprecationWarning)
        return self

    def show(self):
        """
        Show the toast
        """
        if self.actions:
            self.actions = '\n'.join(self.actions)
        else:
            self.actions = ''

        if self.audio == audio.Silent:
            self.audio = '<audio silent="true" />'

        if self.launch:
            self.launch = 'activationType="protocol" launch="{}"'.format(self.launch)

        self.script = TEMPLATE.format(**self.__dict__)

        _run_ps(command=self.script)


class Notifier:
    def __init__(self, registry: Registry):
        """
        A `Notification` manager class.

        Args:
            registry: A `Registry` instance containing the `app_id`, default interpreter, and the script path.
        """
        self.app_id = registry.app
        self.icon = ""
        pidfile = os.path.join(tempdir, f'{self.app_id}.pid')

        # alias for callback_to_url()
        self.cb_url = self.callback_to_url

        if self._protocol_launched():
            # communicate to main process if it's alive
            self.func_to_call = sys.argv[1].split(':')[1]
            self._cb = {}  # callbacks are stored here because we have no listener
            if os.path.isfile(pidfile):
                sender = Sender(self.app_id)
                sender.send(self.func_to_call)
                sys.exit()
        else:
            self.listener = Listener(self.app_id)
            open(pidfile, 'w').write(str(os.getpid()))  # pid file
            atexit.register(os.unlink, pidfile)

    @property
    def callbacks(self):
        """
        Returns:
            A dictionary containing all registered callbacks, with each function's name as the key

        """
        if hasattr(self, 'listener'):
            return self.listener.callbacks
        else:
            return self._cb

    def set_icon(self, path: str):
        """
        Set icon globally for all notification
        Args:
            path: The absolute path of the icon

        Returns:
            None

        """
        self.icon = path

    def create_notification(self,
                            title: str,
                            msg: str = '',
                            icon: str = '',
                            duration: str = 'short',
                            launch: Union[str, Callable] = '') -> Notification:
        """

        See Also:
            `Notification`

        Notes:
            `launch` parameter can be a callback function here

        Returns:
            `Notification` object

        """
        if self.icon:
            icon = self.icon

        if callable(launch):
            url = self.callback_to_url(launch)
        else:
            url = launch

        notif = Notification(self.app_id, title, msg, icon, duration, url)
        return notif

    def start(self):
        """
        Start the listener thread. This method *must* be called first in the main function,
        Otherwise, all the callback function will never get called.

        Examples:
            ```python
            if __name__ == "__main__":
                notifier.start()
                ...
            ```
        """
        if self._protocol_launched():  # call the callback directly
            self.callbacks.get(self.func_to_call)()

        else:
            self.listener.callbacks.update(self.callbacks)
            self.listener.thread.start()

    def update(self):
        """
        check for available callback function in queue then call it
        this method *must* be called *every time* in loop.

        If all callback functions don't need to run in main thread, calling this functions is *optional*

        Examples:
            ```python
            # the main loop
            while True:
                notifier.update()
                ...
            ```
        """
        if self._protocol_launched():
            return

        q = self.listener.queue
        try:
            func = q.get_nowait()
            if callable(func):
                func()
            else:
                print(f"{func.__name__} ")
        except queue.Empty:
            pass

    def _protocol_launched(self) -> bool:
        """
        check whether the app is opened directly or via notification

        Returns:
            True, if opened from notification; False if opened directly
        """
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            return format_name(self.app_id) + ':' in arg and len(arg.split(':')) > 0
        else:
            return False

    def register_callback(self, func=None, *, run_in_main_thread=False):
        """
        A decorator to register a function to be used as a callback
        Args:
            func: the function to decorate
            run_in_main_thread: If True, the callback function will run in main thread

        Examples:
            ```python
            @notifier.register_callback
            def foo(): ...
            ```

        Returns:
            The registered function

        """
        def inner(f):
            if run_in_main_thread:
                f.rimt = run_in_main_thread
            self.callbacks[f.__name__] = f
            f.url = self.callback_to_url(f)
            return f

        if func is None:
            return inner
        else:
            return inner(func)

    def callback_to_url(self, func: Callable) -> str:
        """
        Translate the registered callback function `func` to url notation.

        Args:
            func: The registered callback function

        Returns:
             url-notation string eg. `my-app-id:foo`, where **my-app-id** is the app id and **foo** is the function name

        """

        if callable(func) and func.__name__ in self.callbacks:
            url = format_name(self.app_id) + ":" + func.__name__
            return url

    def clear(self):
        """
        Clear all notification created by `Notifier` from action center

        """

        cmd = f"""\
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        [Windows.UI.Notifications.ToastNotificationManager]::History.Clear('{self.app_id}')
        """
        _run_ps(command=cmd)
