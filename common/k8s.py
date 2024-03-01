import os
from tkinter import messagebox
from kubernetes import client, config # https://github.com/kubernetes-client/python/blob/v24.2.0/kubernetes/README.md

# Raised when there are issues with the K8s Client
class KubernetesAPI(Exception):
  pass

class FluxClient():

  flux_api_groups = None
  crd = None
  events = None

  def __init__(self):
    try: self.clientInit()
    except Exception as e:
      raise KubernetesAPI(e)

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
    self.events = client.CoreV1Api()

  def getCRDVersion(self, target_group):
    for group in client.ApisApi().get_api_versions().groups:
      if group.name == target_group:
        versions = []
        for group_version in group.versions:
          versions.append(group_version.version)
        return versions

  def removeDuplicates(self, elements):
    result = []
    checked_element = []
    for element in elements:
      element_signature = element["kind"] + element["metadata"]["name"] + element["metadata"]["namespace"]
      if element_signature not in checked_element:
        checked_element.append(element_signature)
        result.append(element)
    return result

  def getAllKustomizations(self):
    kustomizations = []
    for version in self.flux_api_groups["kustomizations"]["version"]:
      kustomizations = kustomizations + self.crd.list_cluster_custom_object(self.flux_api_groups["kustomizations"]["group"], version,"kustomizations")["items"]
    return self.removeDuplicates(kustomizations)

  def getAllHelmReleases(self):
    helmreleases = []
    for version in self.flux_api_groups["helmreleases"]["version"]:
      helmreleases = helmreleases + self.crd.list_cluster_custom_object(self.flux_api_groups["helmreleases"]["group"], version,"helmreleases")["items"]
    return self.removeDuplicates(helmreleases)

  def getAllSources(self, plurals=[]):
    sources = []
    for version in self.flux_api_groups["sources"]["version"]:
      if len(plurals) == 0:
        plurals = self.flux_api_groups["sources"]["plurals"]
      for plural in plurals:
        try: sources = sources + self.crd.list_cluster_custom_object(self.flux_api_groups["sources"]["group"],version,plural)["items"]
        except: pass
    return self.removeDuplicates(sources)

  def getAllImages(self, plurals=[]):
    images = []
    for version in self.flux_api_groups["images"]["version"]:
      if len(plurals) == 0:
        plurals = self.flux_api_groups["images"]["plurals"]
      for plural in plurals:
        try: images = images + self.crd.list_cluster_custom_object(self.flux_api_groups["images"]["group"],version,plural)["items"]
        except: pass
    return self.removeDuplicates(images)
  
  def getAllEvents(self, limit=25):
    return self.events.list_event_for_all_namespaces(limit=limit).items