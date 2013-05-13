import os
import tty
import select
import sys
import termios

from sh import egrep

# TODO Better error handling
# TODO Proper encapsulation
# TODO Polish threading model


class Interact(object):
    def __init__(self):
        self.count = 0
        self.muted = False

    def __call__(self, line, stdin, process):
        if self.count >= 100:
            process.kill()
            self.count = 0
            print
        else:
            self.count += 1
            if not self.muted:
                print line,
            else:
                process.kill()
                self.count = 0
                print

    def mute(self):
        self.muted = True


class TermSearch(object):
    def __init__(self, path):
        self.s = ''
        self.old_settings = termios.tcgetattr(sys.stdin)
        self.old = None
        self.path = path

    def escape(self, s):
        escape_chars = ['(', ')', '.']

        for c in escape_chars:
            return s.replace(c, '\\' + c)

        return s

    def start(self):
        try:
            tty.setcbreak(sys.stdin.fileno())
            while 1:
                if self.isData():
                    c = sys.stdin.read(1)
                    self.s += c
                    if c == '\x1b': # ESC
                        break
                    if c == '\x0A': # Return
                        continue;
                    if c == '\x7f': # Backspace
                        self.s = self.s[:-2]

                    if self.s != '':
                        n = Interact()
                        egrep(
                            # Recursive
                            "-R",
                            # Case insensitive
                            "-i",
                            # Prefix line number
                            "-n",
                            # Ignore binary
                            "-I",
                            # Max 3 results per file
                            "-m", 3,
                            # 2 lines of context
                            "-C", 2,
                            self.escape(self.s), self.path, _bg=True, _out=n)
                        if self.old is not None:
                            self.old.mute()
                            print
                            print '-----------------------------------------'
                            print self.s
                        self.old = n
        
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def isData(self):
        return select.select([sys.stdin], [], [], 250) == ([sys.stdin], [], [])

if __name__ == '__main__':
    if len(sys.argv) == 2:
        TermSearch(sys.argv[1]).start()
    else:
        TermSearch().start()
