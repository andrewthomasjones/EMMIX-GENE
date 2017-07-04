import os
import win32api
import win32gui
import win32con
import threading

class MessageStore:
    "Message store"

    def __init__(self, filename=None):
        self.lines = []
        self.filename=filename
        if filename:
            self.restore(filename)
        
    def __del__(self):
        if self.filename:
            self.store(self.filename)

    def store(self, filename=None):
        if not filename:
            filename=self.filename
        open(filename, 'w').writelines(self.lines)

    def restore(self, filename):
        try:
            self.lines = open(filename, 'r').readlines()
        except IOError:
            self.lines=[] 
       
    def addMessage(self, msg):
        if not msg.endswith("\n"):
            msg += "\n";
        self.lines.append(msg)
        #
        # Add a messagebox
        NonBlockingMessageBox(0, msg, "EmmixGene", win32con.MB_ICONINFORMATION)

    def deleteAllMessages(self, REQUEST=None):
        "Removes all messages from the message store"
        os.remove(self.filename)
        if REQUEST:
            REQUEST.RESPONSE.redirect('/')

    def deleteMessageNumber(self, msg_number):
        try:
            del self.lines[msg_number]
        except IndexError:
            raise IndexError, "Message number does not exist"

    def getMessages(self):
        return self.lines

    def displayMessages(self):
        "Displays messages in HTML format"
        output = ""
        for line in self.lines:
            output += line + '<br/>'
        return output
        
def NonBlockingMessageBox(hwnd, message, title, style=0, language=0):
    """MessageBox function that does not block. 
For example:
    NonBlockingMessageBox(0, "Twinkle twinkle\nlittle star","Song", win32con.MB_ICONINFORMATION)
    """
    #
    # win32api.MessageBox(hwnd, message, title, style, language)
    #
    if hwnd==0:
        hwnd=win32gui.GetDesktopWindow()
    if language==0:
        language=win32api.MAKELANGID(win32con.LANG_NEUTRAL, win32con.SUBLANG_DEFAULT)
    if style==0:
        style=win32con.MB_OK
    args=(hwnd, message, title, style, language)
    t = threading.Thread(target=win32api.MessageBox, args=args)
    t.start()

if __name__ == '__main__':
    msgs = MessageStore('messages.txt')
    print msgs.getMessages()
    msgs.addMessage("Hello there!")
    print msgs.getMessages()
    NonBlockingMessageBox(0, "Hello\nWorld","Test", win32con.MB_OK|win32con.MB_ICONERROR)

