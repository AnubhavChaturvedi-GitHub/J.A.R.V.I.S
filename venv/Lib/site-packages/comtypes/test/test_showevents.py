import doctest
import sys
import re
import unittest


class SixDocChecker(doctest.OutputChecker):
    # see https://dirkjan.ochtman.nl/writing/2014/07/06/single-source-python-23-doctests.html
    def check_output(self, want, got, optionflags):
        if sys.version_info >= (3, 0):
            want = re.sub(r"u'(.*?)'", r"'\1'", want)
            want = re.sub(r'u"(.*?)"', r'"\1"', want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def load_tests(loader, tests, ignore):
    import comtypes.test.test_showevents

    tests.addTests(
        doctest.DocTestSuite(comtypes.test.test_showevents, checker=SixDocChecker())
    )
    return tests


class ShowEventsExamples:
    def StdFont_ShowEvents(self):
        """
        >>> from comtypes.client import CreateObject, GetModule, ShowEvents, PumpEvents
        >>> _ = GetModule('scrrun.dll')  # generating `Scripting` also generates `stdole`
        >>> from comtypes.gen import stdole
        >>> font = CreateObject(stdole.StdFont)
        >>> conn = ShowEvents(font)
        # event found: FontEvents_FontChanged
        >>> font.Name = 'Arial'
        Event FontEvents_FontChanged(None, u'Name')
        >>> font.Italic = True
        Event FontEvents_FontChanged(None, u'Italic')
        >>> PumpEvents(0.01)  # just calling. assertion does in `test_pump_events.py`
        >>> conn.disconnect()
        """
        pass


if __name__ == "__main__":
    unittest.main()
