from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import copy
import time
import yaml
import common.utils as utils
import common.k8s as k8s
import threading

class FluxCRsFrame():

  style = None

  frame_topbar = None
  frame_content = None
  frame_scrollbar = None

  k8s = None
  fluxcrs = None
  table_data = []

  columns_keys = None
  table = None
  table_count_label = None
  scrollbar = None
  search_entry = None
  last_column_sort = None
  autoreload_enabled = None
  autoreload_running = None
  autoreload_mutex = threading.Lock()
  ctx_menu = None

  def __init__(self, frame, style):
    self.style = style
    self.initFrames(frame)
    self.initTopBar()
    self.initTreeview()
    self.initScrollBar()
    self.k8s = k8s.FluxClient()
    self.reloadData()
    self.initContextMenu()

  def initFrames(self, frame):
    self.frame_topbar = Frame(frame)
    self.frame_topbar.pack(fill=X, side=TOP, padx=[self.style.fringe_padding, 3*self.style.fringe_padding], pady=[self.style.fringe_padding, 0])
    self.frame_content = Frame(frame)
    self.frame_content.pack(fill=BOTH, expand=TRUE, side=LEFT, padx=[self.style.fringe_padding, 0], pady=self.style.fringe_padding)
    self.frame_scrollbar = Frame(frame)
    self.frame_scrollbar.pack(fill=Y, expand=Y)

  def initTopBar(self):
    self.table_count_label = ttk.Label(self.frame_topbar, text="[-]")
    self.table_count_label.pack(side=LEFT)
    search_label = ttk.Label(self.frame_topbar, text="Search:")
    search_label.pack(side=LEFT)
    self.search_entry = ttk.Entry(self.frame_topbar, font=self.style.getMainFont())
    self.search_entry.pack(fill=X, expand=TRUE, side=LEFT, padx=self.style.fringe_padding)
    self.search_entry.bind('<Return>', lambda event: self.reloadData())
    button = ttk.Button(self.frame_topbar, text="Reload", command=self.reloadData)
    button.pack(side=LEFT)
    self.autoreload_enabled = BooleanVar()
    autoreload_label = ttk.Label(self.frame_topbar, text="Autoreload:")
    autoreload_label.pack(side=LEFT, padx=self.style.fringe_padding)
    self.autoreload_checkbutton = ttk.Checkbutton(self.frame_topbar, command=self.autoreload, variable=self.autoreload_enabled, onvalue=True, offvalue=False, takefocus=False)
    self.autoreload_checkbutton.pack(side=LEFT)

  def autoreload(self):
    self.autoreload_mutex.acquire()
    if self.autoreload_enabled.get() and not self.autoreload_running: threading.Thread(target=self.autoreloadRoutine).start()
    self.autoreload_mutex.release()

  def autoreloadRoutine(self):
    try:
      self.autoreload_mutex.acquire()
      self.autoreload_running = True
      self.autoreload_mutex.release()
      while self.autoreload_enabled.get():
        self.reloadData()
        time.sleep(5)
    except Exception as e:
      print(f"[Data Reload Error]: {e}")
    finally:
      self.autoreload_mutex.acquire()
      self.autoreload_enabled.set(value=False)
      self.autoreload_running = False
      self.autoreload_mutex.release()

  def initTreeview(self):
    self.table = ttk.Treeview(self.frame_content, columns=self.columns_keys, show='headings')
    self.table.pack(fill=BOTH, expand=TRUE)

  def initScrollBar(self):
    self.scrollbar = ttk.Scrollbar(self.frame_scrollbar, orient=VERTICAL, command=self.table.yview)
    self.scrollbar.pack(fill=Y, expand=Y)
    self.table.configure(yscrollcommand=self.scrollbar.set)

  def initContextMenu(self):
    self.ctx_menu = Menu(self.frame_content, tearoff=0)
    self.table.bind("<Button-3>", self.contextMenu_popup)

  def loadData(self):
    raise NotImplementedError("Must be implemented in the Child Class")

  def getStatusCondition(self, resource):
    try:
      for condition in resource["status"]["conditions"]:
        if condition["type"].lower() == "ready": return condition
      return resource["status"]["conditions"][0]
    except:
      return {"status": "-", "message": "-"}

  def reloadData(self):
    self.loadData()
    self.search(self.search_entry.get(), update=False)
    if self.last_column_sort != None: self.sortColumn(self.last_column_sort["column_id"], self.last_column_sort["reverse"], update=False)
    self.updateTable()

  def updateTable(self):
    self.table.delete(*self.table.get_children())
    for item in self.table_data:
      row = []
      for key in self.columns_keys:
        row.append(item[key])
      row.append(item["index"])
      self.table.insert('', END, values=row)
    self.table_count_label["text"] = f"[{len(self.table_data)}]"

  def fluxCommand(self, resource, verb, options=""):
    _current = self.table
    selected_items = _current.selection()
    if len(selected_items) == 0:
      messagebox.showerror(title="Empty Selection", message="No object selected!")
      return
    commands = []
    for item in selected_items:
      name = _current.item(item)["values"][self.columns_keys.index(resource.split(" ")[0])]
      namespace = _current.item(item)["values"][self.columns_keys.index("namespace")]
      commands.append(f"flux {verb} {resource} -n {namespace} {name} {options}")
    for command in commands:
      result = utils.generic_command(command)
      if "✗" in result["stderr"]:
        messagebox.showerror(title="Flux Error", message=result["stderr"])

  def fluxCommandPopup(self, resource, verb, options=""):
    _current = self.table
    selected_items = _current.selection()
    commands = []
    if len(selected_items) == 0:
      messagebox.showerror(title="Empty Selection", message="No object selected!")
      return
    popup_frame = utils.outputRedirectedPopup(title=f"{resource} {verb} {options}", style=self.style)
    processes = []
    try:
      for item in selected_items:
        name = _current.item(item)["values"][self.columns_keys.index(resource.split(" ")[0])]
        namespace = _current.item(item)["values"][self.columns_keys.index("namespace")]
        commands.append(f"flux {verb} {resource} -n {namespace} {name} {options}")
      for command in commands:
        processes.append(utils.subprocessRun(target_function=utils.redirectOutputCommand, args=(command,True)))
    except: pass
  
    popup_frame.protocol("WM_DELETE_WINDOW", func=lambda: utils.terminateFrameProcesses(popup_frame, processes))
    popup_frame.mainloop()

  def contextMenu_popup(self, event):
    try:
      self.ctx_menu.tk_popup(event.x_root, event.y_root)
    finally:
      self.ctx_menu.grab_release()

  def status_popup(self):

    fluxcr = self.getFluxCR(self.table.focus())
    if fluxcr == None: return

    kind = fluxcr["kind"]
    name = fluxcr["metadata"]["name"]
    namespace = fluxcr["metadata"]["namespace"]

    frame_secondary_window = Toplevel()
    frame_secondary_window.title(f"{kind} Status: {name}.{namespace}")
    frame_secondary_window.geometry(self.style.getPopupGeometry())
    frame_secondary_window.iconbitmap(self.style.icon_path)

    frame_content = Frame(frame_secondary_window)
    frame_content.pack(fill=BOTH, expand=TRUE,padx=5*self.style.multiplier, pady=5*self.style.multiplier)

    # Vertical Scrollbar
    scroll_v = Scrollbar(frame_content)
    scroll_v.pack(side=RIGHT,fill=Y)
    # Horizontal Scrollbar
    scroll_h = Scrollbar(frame_content, orient=HORIZONTAL)
    scroll_h.pack(side=BOTTOM, fill=X)
    # Text widget
    text = Text(frame_content, yscrollcommand= scroll_v.set, xscrollcommand = scroll_h.set, wrap="word", font=self.style.getTextFont01(), foreground=self.style.text_font01_color)

    text.pack(fill=BOTH, expand=TRUE)
    # Attact the scrollbar with the text widget
    scroll_h.config(command = text.xview)
    scroll_v.config(command = text.yview)

    first = True
    for item in fluxcr["status"]["conditions"]:
      if not first: text.insert(END, '------------------------------------------------------------------------------------------------------------------------------------------------------\n')
      else: first = False
      for key in item:
        text.insert(END, f'{key}: {item[key]}\n')
    text.config(state=DISABLED)

  def manifest_popup(self):

    fluxcr = self.getFluxCR(self.table.focus())
    if fluxcr == None: return

    kind = fluxcr["kind"]
    name = fluxcr["metadata"]["name"]
    namespace = fluxcr["metadata"]["namespace"]

    frame_secondary_window = Toplevel()
    frame_secondary_window.title(f"{kind} Manifest: {name}.{namespace}")
    frame_secondary_window.geometry(self.style.getPopupGeometry())
    frame_secondary_window.iconbitmap(self.style.icon_path)

    frame_content = Frame(frame_secondary_window)
    frame_content.pack(fill=BOTH, expand=TRUE,padx=5*self.style.multiplier, pady=5*self.style.multiplier)

    # Vertical Scrollbar
    scroll_v = Scrollbar(frame_content)
    scroll_v.pack(side=RIGHT,fill=Y)
    # Horizontal Scrollbar
    scroll_h = Scrollbar(frame_content, orient=HORIZONTAL)
    scroll_h.pack(side=BOTTOM, fill=X)
    # Text widget
    text = Text(frame_content, yscrollcommand= scroll_v.set, xscrollcommand = scroll_h.set, wrap=NONE, font=self.style.getTextFont01(), foreground=self.style.text_font01_color)

    text.pack(fill=BOTH, expand=TRUE)
    # Attact the scrollbar with the text widget
    scroll_h.config(command = text.xview)
    scroll_v.config(command = text.yview)

    _tmp = copy.deepcopy(fluxcr)

    del _tmp["status"]
    if _tmp["metadata"].get("managedFields"): del _tmp["metadata"]["managedFields"]
    del _tmp["metadata"]["creationTimestamp"]
    if _tmp["metadata"].get("finalizers"): del _tmp["metadata"]["finalizers"]
    del _tmp["metadata"]["generation"]
    del _tmp["metadata"]["resourceVersion"]
    del _tmp["metadata"]["uid"]
    if _tmp["metadata"].get("annotations"):
      if _tmp["metadata"]["annotations"].get("reconcile.fluxcd.io/requestedAt"):
        del _tmp["metadata"]["annotations"]["reconcile.fluxcd.io/requestedAt"]
        if len(_tmp["metadata"]["annotations"]) == 0: del _tmp["metadata"]["annotations"]

    text.insert(END, yaml.dump(_tmp).replace("  ", "    "))
    text.config(state=DISABLED)

  def getFluxCR(self, tableIndex):
    if tableIndex == '':
      messagebox.showerror(title="Invalid Index", message="The selected object is NOT valid!")
      return None
    index = self.table.item(tableIndex)["values"][-1]
    return self.fluxcrs[index]

  def sortColumn(self, column_id, reverse=False, update=True):
    self.table_data = sorted(self.table_data, key=lambda x: x[column_id], reverse=reverse)
    if update:
      self.last_column_sort = {"column_id": column_id, "reverse": reverse}
      self.updateTable()
      self.table.heading(column_id, command=lambda: self.sortColumn(column_id=column_id, reverse=not reverse))

  def match_found(self, text_1, text_2):
    text_1 = text_1.lower()
    text_2 = text_2.lower()
    if text_1 != '':
      if text_1[0] == '!':
        if text_1[1:] not in text_2: return True
        else: return False
      else:
        if text_1 in text_2: return True
        else: return False
    else:
      return True

  def search(self, text, update=True, values_start_index=1, values_end_index=-1):
    if text != '':
      current = self.table_data
      self.table_data = []
      
      for item in current:
        row_list = []
        for el in list(item.values()): row_list.append(str(el))
        row = " ".join(row_list[values_start_index:values_end_index]).lower()
        matched = True
        for keyword in text.lower().split(' '):
          if ':' in keyword:
            tmp = keyword.split(':')
            if matched and self.match_found(tmp[1], item[tmp[0]]): continue
            else:
              matched = False
              break
          else:
            if matched and self.match_found(keyword, row): continue
            else:
              matched = False
              break
        if matched: self.table_data.append(item)
      
      if update: self.updateTable()