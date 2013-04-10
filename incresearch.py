import tty, select, sys, termios

from sh import egrep

# TODO Better error handling
# TODO Proper encapsulation
# TODO Polish threading model

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
s = ''
p = None

class Interact(object):
    def __init__(self):
        self.count = 0
        self.muted = False

    def __call__(self, line, stdin, process):
        if self.count >= 10:
            try:
                p.kill()
            except:
                pass
            finally:
                self.count = 0
                print
        else:
            self.count += 1
            if not self.muted:
                print line,
            else:
                try:
                    p.kill()
                except:
                    pass
                finally:
                    self.count = 0
                    print

    def mute(self):
        self.muted = True


try:
    tty.setcbreak(sys.stdin.fileno())
    old = None
    while 1:
        if isData():
            c = sys.stdin.read(1)
            s = s + c
            if c == '\x1b': # ESC
                break
            if c == '\x0A': # Return
                continue;
            if c == '\x7f': # Backspace
                s = s[:-2]

            if s != '':
                try:
                    n = Interact()
                    p = egrep(
                            # Recursive
                            "-R",
                            # Case insensitive
                            "-i",
                            # Prefix line number
                            "-n",
                            # Max 3 results per file
                            "-m", 3,
                            # 2 lines of context
                            "-C", 2,
                            s, "../../mule/habitat/web-ui/",_bg=True,_out=n)
                    if old is not None:
                        old.mute()
                        print
                        print '-----------------------------------------'
                        print s
                    old = n
                except:
                    pass

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
