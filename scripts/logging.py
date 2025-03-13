import sys

class Logger:
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("track.log", "w")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def close(self):
        self.log.close()

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass