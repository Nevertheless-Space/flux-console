from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
from flux.FluxCRsFrame import FluxCRsFrame

class ImageAutomationFrame(FluxCRsFrame):

  def __init__(self, frame, style):
    self.columns_keys = ("type", "namespace", "image", "message", "status", "suspended")
    super().__init__(frame, style)

  def initTreeview(self):
    super().initTreeview()
    self.table.heading("type", text="Type", command=lambda: self.sortColumn(column_id="type"))
    self.table.column("type", stretch=NO, width=180*self.style.multiplier, minwidth=0)
    self.table.heading("namespace", text="Namespace", command=lambda: self.sortColumn(column_id="namespace"))
    self.table.column("namespace", stretch=NO, width=250*self.style.multiplier, minwidth=0)
    self.table.heading("image", text="Image", command=lambda: self.sortColumn(column_id="image"))
    self.table.heading("message", text="Message", command=lambda: self.sortColumn(column_id="message"))
    self.table.heading("status", text="Status", command=lambda: self.sortColumn(column_id="status"))
    self.table.column("status", stretch=NO, width=60*self.style.multiplier, minwidth=0, anchor=CENTER)
    self.table.heading("suspended", text="Suspended", command=lambda: self.sortColumn(column_id="suspended"))
    self.table.column("suspended", stretch=NO, width=100*self.style.multiplier, minwidth=0, anchor=CENTER)

  def initContextMenu(self):
    super().initContextMenu()
    self.ctx_menu.add_command(label="Status", command=lambda: threading.Thread(target=self.status_popup).start())
    self.ctx_menu.add_command(label="Manifest", command=lambda: threading.Thread(target=self.manifest_popup).start())
    self.ctx_menu.add_separator()
    self.ctx_menu.add_command(label="Reconcile", command=lambda: threading.Thread(self.fluxCommandPopup(resource=f"image {self.getImageTypeCommand()}", verb="reconcile")).start())
    self.ctx_menu.add_command(label="Suspend", command=lambda: self.fluxCommand(resource=f"image {self.getImageTypeCommand()}", verb="suspend", options="--all"))
    self.ctx_menu.add_command(label="Resume", command=lambda: self.fluxCommand(resource=f"image {self.getImageTypeCommand()}", verb="resume", options="--all --wait=false"))
    self.ctx_menu.add_command(label="Suspend + Resume", command=self.suspendResume)

  def loadData(self):
    self.fluxcrs = self.k8s.getAllImages()
    self.table_data = []
    try:
      for index in range(len(self.fluxcrs)):
        suspended = None
        try:
          suspended = str(self.fluxcrs[index]["spec"]["suspend"])
        except:
          suspended = "False"

        item = {
          "index": index,
          "type": self.fluxcrs[index]["kind"],
          "namespace": self.fluxcrs[index]["metadata"]["namespace"],
          "image": self.fluxcrs[index]["metadata"]["name"],
          "message": self.fluxcrs[index]["status"]["conditions"][0]["message"],
          "status": self.fluxcrs[index]["status"]["conditions"][0]["status"],
          "suspended": suspended,
        }
        self.table_data.append(item)
    except Exception as e:
      messagebox.showerror(title="Kubectl Error", message=e)

  def getImageTypeCommand(self):
    fluxcr = self.getFluxCR(self.table.focus())
    kind = fluxcr["kind"]
    if kind.lower() == "ImagePolicy".lower():
      return "policy"
    elif kind.lower() == "ImageRepository".lower():
      return "repository"
    elif kind.lower() == "ImageUpdateAutomation".lower():
      return "update"

  def suspendResume(self):
    self.fluxCommand(resource=f"image {self.getImageTypeCommand()}", verb="suspend", options="--all")
    self.fluxCommand(resource=f"image {self.getImageTypeCommand()}", verb="resume", options="--all --wait=false")
  
  def fluxCommandPopup(self, resource, verb, options=""):
    if "policy" in resource and verb == "reconcile":
      messagebox.showerror(title="Flux Error", message="You cannot reconcile an ImagePolicy resource")
    else: super().fluxCommandPopup(resource, verb, options)