from Xlib import X, XK                      # X server and X keyboard
from Xlib.display import Display            # X display
from Xlib.display import colormap           # X colourmap
from threading import Thread
import configparser
import subprocess
import logging
import time


logging.basicConfig(filename='NiceWM.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

def log(message):
   logging.debug(message)

class wm(object):
    """Initialise WM variables and open display"""
    def __init__(self):
        self.windows = []  # List of opened windows
        self.display = Display()  # Initialise display
        self.colormap = self.display.screen().default_colormap  # Initialise colourmap
        self.rootWindow = self.display.screen().root  # Get root window
        self.activeWindow=None
        self.currentMode=None
        self.activeWindowFullscreen=False
        self.displayWidth = self.rootWindow.get_geometry().width  # Get width of display
        self.displayHeight = self.rootWindow.get_geometry().height  # Get height of display
        self.rootWindow.change_attributes(event_mask = X.SubstructureRedirectMask)  # Redirect events from root window
        self.configureKeys()  # Configure key bindings
        self.readConfig()
        self.workspaces=[]
        log("initialized WM and opened display")
    
    


    def readConfig(self):
        parser = configparser.ConfigParser()
        parser.read('config.ini')
        self.inactiveColour=parser.get("Theme","inactive-window-color")
        self.activeColour=parser.get("Theme","active-window-color")
        self.wallpaper=parser.get("Theme","wallpaper")
        self.borderSize=parser.get("Theme","border-size")
        self.startupScriptPath=parser.get("Options","startup-script-path")
        self.startupScriptCommand=parser.get("Options","startup-script-command")
        subprocess.Popen([self.startupScriptCommand,self.startupScriptPath])
        self.defaultBrowser=parser.get("Defaults","browser")
        self.defaultTerminal=parser.get("Defaults","terminal")
        self.keymap=parser.get("Options","keymap")
        
    
        subprocess.Popen(['setxkbmap','-layout',self.keymap])
        if not self.wallpaper == "None":
            subprocess.Popen(["feh","--bg-scale",self.wallpaper])
        log("read config file")

    def redraw(self):
        self.updateBorders()
        self.handleEvents()
        if len(self.windows) >= 1 and self.activeWindow == None:
            self.activeWindow = self.windows[1]
    
    def killWindow(self):
        try:
            subprocess.Popen(["killall",self.activeWindowName])
            self.activeWindow.destroy()
            self.windows.remove(self.activeWindow)
            self.activeWindow = None
            log(f"killed window name: {self.activeWindowName}")
        except Exception as e:
            log(f"EXCEPCION on killWindow() : {e} ")



    
    def updateBorders(self):
        for window in self.windows:
            window.configure(border_width = int(self.borderSize))
            window.change_attributes(None,border_pixel=int(self.borderSize))
            self.display.sync()


    def handleEvents(self):
        ignoredEvents = [3, 33, 34, 23]  # Blacklisted events
        if self.display.pending_events() > 0:
            event = self.display.next_event()  # Get next event from display 
        else:
            return
        if event.type == X.MapRequest: self.handleMap(event)  # Send mapping events to the mapping handler
        elif event.type == X.KeyPress: self.handleKeyPress(event)  # Send keypress event to the keypress handler
   

    """Handle a mapping request"""
    def handleMap(self, event):
        self.windows.append(event.window)  # Add the window identifier to a list of open windows
        self.activeWindow = event.window  # Set the active window to the mapped window
        self.activeWindowName = event.window.get_wm_name()  # Set the active window name to the window title
        event.window.map()  # Map the window


    def grabKey(self, codes, modifier):
        for code in codes:  # For each code
            self.rootWindow.grab_key(code, modifier, 1, X.GrabModeAsync, X.GrabModeAsync)  # Receive events when the key is pressed


    def configureKeys(self):
        self.left = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Left))  # Assign a list of possible keycodes to the variable
        self.right = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Right))
        self.up = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Up))
        self.down = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Down))
        self.close = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_X))
        self.enter = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Return))
        self.d = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_D))
        self.q = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Q))
        self.r = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_R))
        self.f =set(code for code, index in self.display.keysym_to_keycodes(XK.XK_F))
        self.esc = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Escape) )
        self.h =set(code for code, index in self.display.keysym_to_keycodes(XK.XK_H))
        self.j = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_J))
        self.k =set(code for code, index in self.display.keysym_to_keycodes(XK.XK_K))
        self.l =set(code for code, index in self.display.keysym_to_keycodes(XK.XK_L))
        self.g =set(code for code, index in self.display.keysym_to_keycodes(XK.XK_G))
        self.grabbedKeys = [self.left,self.g, self.right, self.up, self.down, self.close, self.enter, self.d, self.q, self.r,self.f,self.esc, self.h,self.j,self.k,self.l]
        for key in self.grabbedKeys:  # For each key to grab,
            self.grabKey(key, X.Mod1Mask)  # Grab the key with the modifer of Alt


    def moveWindow(self, direction):
        log("moved window")
        try:
            if direction == "left":
                windowX = self.activeWindow.get_geometry().x  # Get the current position of the active window
                self.activeWindow.configure(x=windowX-5)  # Decrease the X position to move it left
            elif direction == "right":
                windowX = self.activeWindow.get_geometry().x
                self.activeWindow.configure(x=windowX+5)
            elif direction == "up":
                windowY = self.activeWindow.get_geometry().y
                self.activeWindow.configure(y=windowY-5)    
            elif direction == "down":
                windowY = self.activeWindow.get_geometry().y
                self.activeWindow.configure(y=windowY+5)
        except AttributeError:
                pass

    def resize(self, direction):
        windowGeometry = self.activeWindow.get_geometry()
        if direction == 0:
            self.activeWindow.configure(width=windowGeometry.width+5, x = windowGeometry.x -5)
        elif direction == 1:
            self.activeWindow.configure(width=windowGeometry.width-5, x = windowGeometry.x + 5)
        elif direction == 2:
            self.activeWindow.configure(height=windowGeometry.height-5, y=windowGeometry.y + 5)
        else:
            self.activeWindow.configure(height=windowGeometry.height+5, y=windowGeometry.y -5)

    
    def handleKeyPress(self, event):

        if event.detail in self.left: self.moveWindow("left")
        elif event.detail in self.right: self.moveWindow("right")
        elif event.detail in self.up: self.moveWindow("up")
        elif event.detail in self.down: self.moveWindow("down") 
        if event.detail in self.enter: 
            self.runProcess(self.defaultTerminal)      # Alt+ENTER: Launch a terminal
        elif event.detail in self.d: 
            self.runProcess(["rofi","-show","run"])      # Alt+D: Launch a program launcher
        elif event.detail in self.q: 
            self.killWindow()                                      # ALT+Q: Close a window
        if event.detail in self.h:
            self.resize(2)
        elif event.detail in self.j:
            self.resize(3)
        elif event.detail in self.k:
            self.resize(1)
        elif event.detail in self.l:
            self.resize(0)
        
        elif event.detail in self.f:
            self.activeWindow.configure(x=0,width=1920,y=0,height=1080)
        elif event.detail in self.g:
             self.activeWindow.configure(x=0,width=1000,y=0,height=800)

        
        if event.detail in self.h:
            self.resize(2)
        elif event.detail in self.j:
            self.resize(3)
        elif event.detail in self.k:
            self.resize(1)
        elif event.detail in self.l:
            self.resize(0)



    def runProcess(self,command):
        try:
            subprocess.Popen(command)
        except Exception:
            pass


WM=wm()

def main():
    while True:
        try:
            WM.redraw()
            time.sleep(0.001)
        except Exception as e:
            log(e)
main()
