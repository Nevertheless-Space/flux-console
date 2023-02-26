from tkinter import *
from tkinter import ttk
import common.icon as icon

class MainStyle():

  icon_path = '$$_temp.ico'
  style = None
  multiplier = None
  text = {
    "font": "Calibri",
    "size_normal": 7,
    "size_heading": 7,
  }
  rowheight = 20
  screen_width = None
  screen_height = None
  text_font01_color = "gray22"

  def __init__(self, screen_width, screen_height):
    icon.createIconFile(self.icon_path)
    self.style = ttk.Style()
    self.screen_width = screen_width
    self.screen_height = screen_height

    self.multiplier = 1
    if self.screen_width > 1920: self.multiplier = 2

    self.initWidgets()

  def initWidgets(self):
    self.style.configure("Treeview.Heading", rowheight=self.rowheight + (self.multiplier*10), font=(self.text["font"], self.text["size_heading"]  + (self.multiplier*2),'bold'))
    self.style.configure("Treeview", rowheight=self.rowheight + (self.multiplier*10), font=self.getMainFont())
    self.style.configure('TButton', font=self.getMainFont())
    self.style.configure('TLabel', font=self.getMainFont())
    self.style.configure('TEntry', font=self.getMainFont())
    self.style.configure('TNotebook.Tab', foreground="grey70", font=(self.text["font"], self.text["size_heading"]  + (self.multiplier*2)), padding=[ 10*self.multiplier,  5*self.multiplier,  10*self.multiplier,  5*self.multiplier])
    self.style.map("TNotebook.Tab", foreground=[("selected", "black")])
    self.style.layout("Tab", [('Notebook.tab', {'sticky': 'nswe', 'children':
      [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
          [('Notebook.label', {'side': 'top', 'sticky': ''})],
      })],
    })]
    )
    self.style.configure("Tab", focuscolor=self.style.configure(".")["background"])

  def getMainFont(self):
    return (self.text["font"], self.text["size_normal"] + (self.multiplier*2))

  def getMainGeometry(self):
    dimentions = {
      "width": (0.60 * self.screen_width),
      "height": (0.80 * self.screen_height),
      "right": (0.20 * self.screen_width) - 10*self.multiplier,
      "top": (0.10 * self.screen_height) - 10*self.multiplier,
    }
    return f"{int(dimentions['width'])}x{int(dimentions['height'])}+{int(dimentions['right'])}+{int(dimentions['top'])}"
  
  def getPopupGeometry(self):
    dimentions = {
      "width": (0.50 * self.screen_width),
      "height": (0.50 * self.screen_height),
      "right": (0.25 * self.screen_width) - 10*self.multiplier,
      "top": (0.25 * self.screen_height) - 10*self.multiplier,
    }
    return f"{int(dimentions['width'])}x{int(dimentions['height'])}+{int(dimentions['right'])}+{int(dimentions['top'])}"

  def getTextFont01(self):
    return ("Calibri", str(8 + 2*self.multiplier))