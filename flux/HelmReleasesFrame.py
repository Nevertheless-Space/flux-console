import json
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import common.utils as utils
import threading
from flux.FluxCRsFrame import FluxCRsFrame

class HelmReleasesFrame(FluxCRsFrame):

  selected_revision = {}
  helm_values_text = {}

  def __init__(self, frame, style):
    self.columns_keys = ("namespace", "helmrelease", "message", "chart", "status", "suspended")
    super().__init__(frame, style)

  def initTreeview(self):
    super().initTreeview()
    self.table.heading("namespace", text="Namespace", command=lambda: self.sortColumn(column_id="namespace"))
    self.table.column("namespace", stretch=NO, width=250*self.style.multiplier, minwidth=0)
    self.table.heading("helmrelease", text="HelmRelease", command=lambda: self.sortColumn(column_id="helmrelease"))
    self.table.heading("message", text="Message", command=lambda: self.sortColumn(column_id="message"))
    self.table.heading("chart", text="Chart", command=lambda: self.sortColumn(column_id="chart"))
    self.table.column("chart", stretch=NO, width=75*self.style.multiplier, minwidth=0, anchor=CENTER)
    self.table.heading("status", text="Status", command=lambda: self.sortColumn(column_id="status"))
    self.table.column("status", stretch=NO, width=60*self.style.multiplier, minwidth=0, anchor=CENTER)
    self.table.heading("suspended", text="Suspended", command=lambda: self.sortColumn(column_id="suspended"))
    self.table.column("suspended", stretch=NO, width=100*self.style.multiplier, minwidth=0, anchor=CENTER)

  def initContextMenu(self):
    super().initContextMenu()
    self.ctx_menu.add_command(label="Status", command=lambda: threading.Thread(target=self.status_popup).start())
    self.ctx_menu.add_command(label="Manifest", command=lambda: threading.Thread(target=self.manifest_popup).start())
    self.ctx_menu.add_separator()
    self.ctx_menu.add_command(label="Reconcile", command=lambda: threading.Thread(self.fluxCommandPopup(resource="helmrelease", verb="reconcile")).start())
    self.ctx_menu.add_command(label="Reconcile with Source", command=lambda: threading.Thread(self.fluxCommandPopup(resource="helmrelease", verb="reconcile", options="--with-source")).start())
    self.ctx_menu.add_command(label="Suspend", command=lambda: self.fluxCommand(resource="helmrelease", verb="suspend", options="--all"))
    self.ctx_menu.add_command(label="Resume", command=lambda: self.fluxCommand(resource="helmrelease", verb="resume", options="--all --wait=false"))
    self.ctx_menu.add_command(label="Suspend + Resume", command=self.suspendResume)
    self.ctx_menu.add_separator()
    self.ctx_menu.add_command(label="Helm Values", command=lambda: threading.Thread(target=self.helmValues_popup).start())
    
    self.ctx_menu_danger = Menu(self.ctx_menu, tearoff=0)
    self.ctx_menu_danger.add_command(label="Helm Uninstall", command=self.helmUnistall_popup)
    self.ctx_menu.add_cascade(label="Danger", menu=self.ctx_menu_danger)

  def loadData(self):
    self.fluxcrs = self.k8s.getAllHelmReleases()
    self.table_data = []
    try:
      for index in range(len(self.fluxcrs)):
        suspended = None
        try:
          suspended = str(self.fluxcrs[index]["spec"]["suspend"])
        except:
          suspended = "False"
        try:
          message = self.fluxcrs[index]["status"]["conditions"][0]["message"]
        except:
          message = "-"
        try:
          status = self.fluxcrs[index]["status"]["conditions"][0]["status"]
        except:
          status = "-"

        chart = "-"
        if self.fluxcrs[index]["status"].get("lastAttemptedRevision") != None: chart = self.fluxcrs[index]["status"]["lastAttemptedRevision"]

        item = {
          "index": index,
          "namespace": self.fluxcrs[index]["metadata"]["namespace"],
          "helmrelease": self.fluxcrs[index]["metadata"]["name"],
          "message": message,
          "chart": chart,
          "status": status,
          "suspended": suspended,
        }
        self.table_data.append(item)
    except Exception as e:
      messagebox.showerror(title="Kubectl Error", message=e)

  def suspendResume(self):
    self.fluxCommand(resource="helmrelease", verb="suspend", options="--all")
    self.fluxCommand(resource="helmrelease", verb="resume", options="--all --wait=false")

  def helmValues_popup_close(self, name, namespace, frame):
    try:
      del self.selected_revision[f"{name}.{namespace}"]
      del self.helm_values_text[f"{name}.{namespace}"]
    finally: frame.destroy()

  def helmValues_popup(self):

    helmrelease = self.getFluxCR(self.table.focus())
    if helmrelease == None: return

    name = helmrelease["spec"]["releaseName"]
    namespace = helmrelease["metadata"]["namespace"]

    frame_secondary_window = Toplevel()
    frame_secondary_window.title(f"Helm Values: {name}.{namespace}")
    frame_secondary_window.geometry(self.style.getPopupGeometry())
    frame_secondary_window.iconbitmap(self.style.icon_path)
    frame_secondary_window.protocol("WM_DELETE_WINDOW", func=lambda: self.helmValues_popup_close(name, namespace, frame_secondary_window))

    frame_header = Frame(frame_secondary_window)
    frame_header.pack(fill=X, expand=FALSE)
    frame_content = Frame(frame_secondary_window)
    frame_content.pack(fill=BOTH, expand=TRUE)

    helm_history = None
    history = utils.generic_command(f"helm history -n {namespace} {name} -o json")
    if history["stderr"] != "":
      messagebox.showerror(title="Helm Error", message=history["stderr"])
      frame_secondary_window.destroy()
      return
    else:
      helm_history = json.loads(str(history["stdout"][:-1]))

    self.selected_revision[f"{name}.{namespace}"] = StringVar()

    revisions = ttk.Combobox(frame_header, textvariable=self.selected_revision[f"{name}.{namespace}"], font=self.style.getMainFont())
    frame_header.option_add('*TCombobox*Listbox.font', self.style.getMainFont())
    revisions["values"] = [f'{revision["revision"]} - {revision["updated"]} - {revision["status"]} - {revision["description"]}' for revision in helm_history]
    revisions["state"] = 'readonly'
    self.selected_revision[f"{name}.{namespace}"].set(revisions["values"][-1])

    # Scrollbars
    scroll_v = Scrollbar(frame_content)
    scroll_v.pack(side=RIGHT,fill=Y)
    scroll_h = Scrollbar(frame_content, orient=HORIZONTAL)
    scroll_h.pack(side=BOTTOM, fill=X)

    revisions.bind('<<ComboboxSelected>>', lambda event: self.getHelmValuesRevision(name, namespace, frame_content, scroll_h, scroll_v))
    self.getHelmValuesRevision(name, namespace, frame_content, scroll_h, scroll_v)
    revisions.pack(fill=X, expand=TRUE, padx=20*self.style.multiplier)

  def getHelmValuesRevision(self, name, namespace, frame_content, scroll_h, scroll_v):
    revision = self.selected_revision[f"{name}.{namespace}"].get().split(" ")[0]
    result = utils.generic_command(f"helm get values -n {namespace} {name} --revision {revision}")
    if result["stderr"] != "":
      messagebox.showerror(title="Helm Error", message=result["stderr"])
      frame_content.destroy()
    else:
      if self.helm_values_text.get(f"{name}.{namespace}"): self.helm_values_text[f"{name}.{namespace}"].destroy()
      self.helm_values_text[f"{name}.{namespace}"] = Text(frame_content, yscrollcommand= scroll_v.set, xscrollcommand = scroll_h.set, wrap= NONE, font=self.style.getTextFont01(), foreground=self.style.text_font01_color)
      self.helm_values_text[f"{name}.{namespace}"].pack(fill=BOTH, expand=TRUE)
      scroll_h.config(command = self.helm_values_text[f"{name}.{namespace}"].xview)
      scroll_v.config(command = self.helm_values_text[f"{name}.{namespace}"].yview)
      self.helm_values_text[f"{name}.{namespace}"].insert(END, f"[REVISION {revision}] " + result["stdout"].replace("  ", "    "))
      self.helm_values_text[f"{name}.{namespace}"].config(state=DISABLED)

  def helmUnistall_popup(self):
    
    helmrelease = self.getFluxCR(self.table.focus())
    if helmrelease == None: return
    
    name = helmrelease["spec"]["releaseName"]
    namespace = helmrelease["metadata"]["namespace"]

    popup_frame = utils.outputRedirectedPopup(title=f"Helm Uninstall: {name}.{namespace}", style=self.style)
    result = utils.generic_command(f"helm uninstall -n {namespace} {name}")
    if result["stderr"] != "":
      messagebox.showerror(title="Helm Error", message=result["stderr"])
      popup_frame.destroy()
    else: print(result["stdout"])

    popup_frame.mainloop()