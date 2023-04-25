from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
from flux.FluxCRsFrame import FluxCRsFrame

class EventsFrame(FluxCRsFrame):

  def __init__(self, frame, style):
    self.columns_keys = ("timestamp", "kind", "namespace", "name", "type", "message")
    super().__init__(frame, style)

  def initTreeview(self):
    super().initTreeview()
    self.table.heading("timestamp", text="Timestamp (Last Seen)", command=lambda: self.sortColumn(column_id="timestamp"))
    self.table.column("timestamp", stretch=NO, width=200*self.style.multiplier, minwidth=0)
    self.table.heading("kind", text="Kind", command=lambda: self.sortColumn(column_id="kind"))
    self.table.column("kind", stretch=NO, width=100*self.style.multiplier, minwidth=0)
    self.table.heading("namespace", text="Namespace", command=lambda: self.sortColumn(column_id="namespace"))
    self.table.column("namespace", stretch=NO, width=250*self.style.multiplier, minwidth=0)
    self.table.heading("name", text="Name", command=lambda: self.sortColumn(column_id="name"))
    self.table.column("name", stretch=NO, width=250*self.style.multiplier, minwidth=0)
    self.table.heading("type", text="Type", command=lambda: self.sortColumn(column_id="type"))
    self.table.column("type", stretch=NO, width=80*self.style.multiplier, minwidth=0, anchor=CENTER)
    self.table.heading("message", text="Message", command=lambda: self.sortColumn(column_id="message"))

  def initContextMenu(self):
    super().initContextMenu()
    self.ctx_menu.add_command(label="Details", command=lambda: threading.Thread(target=self.details_popup).start())

  def loadData(self):
    from kubernetes import client    
    self.fluxcrs = self.k8s.getAllEvents()
    self.table_data = []
    try:
      for index in range(len(self.fluxcrs)):
        timestamp = None
        if self.fluxcrs[index].last_timestamp == None: timestamp = self.fluxcrs[index].event_time
        else: timestamp = self.fluxcrs[index].last_timestamp
        item = {
          "index": index,
          "timestamp": str(timestamp),
          "kind": self.fluxcrs[index].involved_object.kind,
          "namespace": self.fluxcrs[index].involved_object.namespace,
          "name": self.fluxcrs[index].involved_object.name,
          "type": self.fluxcrs[index].type,
          "message": self.fluxcrs[index].message
        }
        self.table_data.append(item)
    except Exception as e:
      messagebox.showerror(title="Kubectl Error", message=e)

  def search(self, text, update=True, values_start_index=1, values_end_index=None):
    super().search(text, update, values_start_index, values_end_index)

  def details_popup(self):

    fluxcr = self.getFluxCR(self.table.focus())
    if fluxcr == None: return

    kind = fluxcr.involved_object.kind
    name = fluxcr.involved_object.name
    namespace = fluxcr.involved_object.namespace

    frame_secondary_window = Toplevel()
    frame_secondary_window.title(f"{kind} Event: {name}.{namespace}")
    frame_secondary_window.geometry(self.style.getPopupGeometry())
    frame_secondary_window.iconbitmap(self.style.icon_path)

    frame_content = Frame(frame_secondary_window)
    frame_content.pack(fill=BOTH, expand=TRUE,padx=5*self.style.multiplier, pady=5*self.style.multiplier)

    # Text widget
    text = Text(frame_content, wrap="word", font=self.style.getTextFont01(), foreground=self.style.text_font01_color)
    text.pack(fill=BOTH, expand=TRUE)

    text.insert(END, f"TYPE: {str(fluxcr.type)}\n")
    text.insert(END, f"REASON: {str(fluxcr.reason)}\n")
    text.insert(END, f"COUNT: {str(fluxcr.count)}\n")
    text.insert(END, f"EVENT TIME: {str(fluxcr.event_time)}\n")
    text.insert(END, f"LAST TIMESTAMP: {str(fluxcr.last_timestamp)}\n")
    text.insert(END, f"FIRST TIMESTAMP: {str(fluxcr.first_timestamp)}\n")
    text.insert(END, "\n")
    text.insert(END, fluxcr.message)
    text.config(state=DISABLED)