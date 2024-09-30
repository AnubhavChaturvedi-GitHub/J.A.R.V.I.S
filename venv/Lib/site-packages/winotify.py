import os
import subprocess
import sys
import argparse
from tempfile import NamedTemporaryFile

__version__ = "1.0.4"


class Sound:
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s


class audio:
    """ audio wrapper class """
    Default = Sound("ms-winsoundevent:Notification.Default")
    IM = Sound("ms-winsoundevent:Notification.IM")
    Mail = Sound("ms-winsoundevent:Notification.Mail")
    Reminder = Sound("ms-winsoundevent:Notification.Reminder")
    SMS = Sound("ms-winsoundevent:Notification.SMS")
    LoopingAlarm = Sound("ms-winsoundevent:Notification.Looping.Alarm")
    LoopingAlarm2 = Sound("ms-winsoundevent:Notification.Looping.Alarm2")
    LoopingAlarm3 = Sound("ms-winsoundevent:Notification.Looping.Alarm3")
    LoopingAlarm4 = Sound("ms-winsoundevent:Notification.Looping.Alarm4")
    LoopingAlarm6 = Sound("ms-winsoundevent:Notification.Looping.Alarm6")
    LoopingAlarm8 = Sound("ms-winsoundevent:Notification.Looping.Alarm8")
    LoopingAlarm9 = Sound("ms-winsoundevent:Notification.Looping.Alarm9")
    LoopingAlarm10 = Sound("ms-winsoundevent:Notification.Looping.Alarm10")
    LoopingCall = Sound("ms-winsoundevent:Notification.Looping.Call")
    LoopingCall2 = Sound("ms-winsoundevent:Notification.Looping.Call2")
    LoopingCall3 = Sound("ms-winsoundevent:Notification.Looping.Call3")
    LoopingCall4 = Sound("ms-winsoundevent:Notification.Looping.Call4")
    LoopingCall5 = Sound("ms-winsoundevent:Notification.Looping.Call5")
    LoopingCall6 = Sound("ms-winsoundevent:Notification.Looping.Call6")
    LoopingCall7 = Sound("ms-winsoundevent:Notification.Looping.Call7")
    LoopingCall8 = Sound("ms-winsoundevent:Notification.Looping.Call8")
    LoopingCall9 = Sound("ms-winsoundevent:Notification.Looping.Call9")
    LoopingCall10 = Sound("ms-winsoundevent:Notification.Looping.Call10")
    Silent = Sound("silent")


audio_map = {key.lower(): value for key, value in audio.__dict__.items() if not key.startswith("__")}


TEMPLATE = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$Template = @"
<toast {launch} duration="{duration}">
    <visual>
        <binding template="ToastImageAndText02">
            <image app_id="1" src="{icon}" />
            <text app_id="1"><![CDATA[{title}]]></text>
            <text app_id="2"><![CDATA[{msg}]]></text>
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


class Notification(object):
    def __init__(self,
                 app_id: str,
                 title: str,
                 msg: str = "",
                 icon: str = "",
                 duration: str = 'short',
                 launch: str = ''):
        """
        Notification class

        :param app_id: your app name, make it readable to your user. It can contain spaces, however special characters
                       (eg. é) are not supported.
        :param title: The heading of the toast.
        :param msg: The content/message of the toast.
        :param icon: An optional app_path to an image on the OS to display to the left of the title & message.
                     Make sure you use an absolute app_path to the image.
        :param duration: How long the toast should show up for (short/long), default is short.
        :param launch: The url to launch (invoked when the user clicks the notification)
        """
        self.app_id = app_id
        self.title = title
        self.msg = msg
        self.icon = icon
        self.duration = duration
        self.launch = launch
        self.audio = audio.Silent
        self.tag, self.group = '', ''  # you can set this value outside __init__
        self.actions = []
        self.script = ""
        self.__dict__.update(
            tag=self.tag or self.app_id,
            group=self.group or self.app_id
        )
        if duration not in ("short", "long"):
            raise ValueError("Duration is not 'short' or 'long'")

    def set_audio(self, audio: Sound, loop: bool):
        """
        Set audio to the notification object.

        :param audio: The audio to play when the notification is showing. Choose one from audio class,
                      (eg. audio.Default). If not calling this method, default audio is silent
        :param loop: A boolean indicating the audio should looping or not
        :return: None
        """
        self.audio = '<audio src="{}" loop="{}" />'.format(audio, str(loop).lower())

    def add_actions(self, label: str, link: str):
        """
        Add action button to the notification. You can have up to 5 buttons each toast.

        :param label: The label of the button
        :param link: The url to launch when clicking the button, 'file:///' protocol is allowed
        :return: None
        """
        xml = '<action activationType="protocol" content="{label}" arguments="{link}" />'
        if len(self.actions) < 5:
            self.actions.append(xml.format(label=label, link=link))

    def build(self):
        """
        Builds a temporary Windows PowerShell script

        :return: self
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
        return self

    def show(self):
        """
        Invoke the temporary created script to Powershell to show the toast.
        Note: Running the PowerShell script is by far the slowest process here, and can take a few
        seconds in some cases.

        :return: None
        """
        if not self.script:
            raise ValueError("Build the notification first before calling show()")

        with NamedTemporaryFile('w', encoding='utf-16', suffix='.ps1', delete=False) as file:
            file.write(self.script)

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-file", file.name
        ],
            # stdin, stdout, and stderr have to be defined here, because windows tries to duplicate these if not null
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,  # set to null because we don'thread need the output :)
            stderr=subprocess.DEVNULL,
            startupinfo=si
        )
        os.remove(file.name)


def main():
    parser = argparse.ArgumentParser(prog="winotify[-nc]", description="Show notification toast on Windows 10."
                                                                       "Use 'winotify-nc' for no console window.")
    parser.version = __version__
    parser.add_argument('-app_id',
                        '--app-app_id',
                        metavar="NAME",
                        default="windows app",
                        help="Your app name")
    parser.add_argument("-thread",
                        "--title",
                        default="Winotify Test Toast",
                        help="the notification title")
    parser.add_argument("-m",
                        "--message",
                        default='New Notification!',
                        help="the notification's main messages")
    parser.add_argument("-i",
                        "--icon",
                        default='',
                        metavar="PATH",
                        help="the icon app_path for the notification (note: the app_path must be absolute)")
    parser.add_argument("--duration",
                        default="short",
                        choices=("short", "long"),
                        help="the duration of the notification should display (default: short)")
    parser.add_argument("--open-url",
                        default='',
                        metavar='URL',
                        help="the URL to open when user click the notification")
    parser.add_argument("--audio",
                        help="type of audio to play (default: silent)")
    parser.add_argument("--loop",
                        action="store_true",
                        help="whether to loop audio")
    parser.add_argument("--action",
                        metavar="LABEL",
                        action="append",
                        help="add button with LABEL as text, you can add up to 5 buttons")
    parser.add_argument("--action-url",
                        metavar="URL",
                        action="append",
                        required=("--action" in sys.argv),
                        help="an URL to launch when the button clicked")
    parser.add_argument("-v",
                        "--version",
                        action="version")

    args = parser.parse_args()

    toast = Notification(args.app_id,
                         args.title,
                         args.message,
                         args.icon,
                         args.duration,
                         args.open_url)

    if args.audio is not None:
        if args.audio not in audio_map.keys():
            sys.exit("Invalid audio " + args.audio)
        else:
            toast.set_audio(audio_map[args.audio], args.loop)

    actions = args.action
    action_urls = args.action_url
    if actions and action_urls:
        if len(actions) == len(action_urls):
            dik = dict(zip(actions, action_urls))
            for action, url in dik.items():
                toast.add_actions(action, url)
        else:
            parser.error("imbalance arguments, "
                         "the amount of action specified is not the same as the specified amount of action-url")

    toast.build().show()


if __name__ == '__main__':
    main()
