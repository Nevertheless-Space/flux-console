import os
from tkinter import messagebox
from kubernetes import client, config # https://github.com/kubernetes-client/python/blob/v24.2.0/kubernetes/README.md

class FluxClient():

  flux_api_groups = None
  crd = None

  def __init__(self):
    try: self.clientInit()
    except Exception as e:
      messagebox.showerror(title="Kubebernetes API Error", message=e)
      exit()

  def clientInit(self, quit=True):
    config.load_kube_config(os.environ.get("KUBECONFIG"))
    self.flux_api_groups = {
      "helmreleases": {
          "group": "helm.toolkit.fluxcd.io",
          "version": self.getCRDVersion("helm.toolkit.fluxcd.io")
        },
      "kustomizations": {
        "group": "kustomize.toolkit.fluxcd.io",
        "version": self.getCRDVersion("kustomize.toolkit.fluxcd.io")
      },
      "sources": {
        "group": "source.toolkit.fluxcd.io",
        "version": self.getCRDVersion("source.toolkit.fluxcd.io"),
        "plurals": [ "gitrepositories", "buckets", "helmrepositories", "helmcharts" ]
      },
      "images": {
        "group": "image.toolkit.fluxcd.io",
        "version": self.getCRDVersion("image.toolkit.fluxcd.io"),
        "plurals": [ "imagepolicies", "imagerepositories", "imageupdateautomations" ]
      }
    }
    self.crd = client.CustomObjectsApi()

  def getCRDVersion(self, target_group):
      for group in client.ApisApi().get_api_versions().groups:
        if group.name == target_group:
          versions = []
          for group_version in group.versions:
            versions.append(group_version.version)
          return versions

  def getAllKustomizations(self):
    for version in self.flux_api_groups["kustomizations"]["version"]:
      return self.crd.list_cluster_custom_object(self.flux_api_groups["kustomizations"]["group"], version,"kustomizations")["items"]

  def getAllHelmReleases(self):
    for version in self.flux_api_groups["helmreleases"]["version"]:
      return self.crd.list_cluster_custom_object(self.flux_api_groups["helmreleases"]["group"], version,"helmreleases")["items"]

  def getAllSources(self, plurals=[]):
    for version in self.flux_api_groups["sources"]["version"]:
      sources = []
      if len(plurals) == 0:
        plurals = self.flux_api_groups["sources"]["plurals"]
      for plural in plurals:
        sources = self.crd.list_cluster_custom_object(self.flux_api_groups["sources"]["group"], version,plural)["items"] + sources
      return sources

  def getAllImages(self, plurals=[]):
    for version in self.flux_api_groups["images"]["version"]:
      images = []
      if len(plurals) == 0:
        plurals = self.flux_api_groups["images"]["plurals"]
      for plural in plurals:
        images = self.crd.list_cluster_custom_object(self.flux_api_groups["images"]["group"], version,plural)["items"] + images
      return images