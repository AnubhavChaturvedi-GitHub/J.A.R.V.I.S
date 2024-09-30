import argparse
import sys

import winotify
from winotify import Notification, audio

audio_map = {key.lower(): value for key, value in audio.__dict__.items() if not key.startswith("__")}


def main():
    parser = argparse.ArgumentParser(prog="winotify[-nc]", description="Show notification toast on Windows 10."
                                     "Use 'winotify-nc' for no console window.")
    parser.version = winotify.__version__
    parser.add_argument('-id',
                        '--app-id',
                        metavar="NAME",
                        default="windows app",
                        help="Your app name")
    parser.add_argument("-t",
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
                        help="the icon path for the notification (note: the path must be absolute)")
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

    toast.show()


if __name__ == '__main__':
    main()

