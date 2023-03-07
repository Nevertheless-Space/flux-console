# Changelog

All notable changes to this project are documented in this file.

## 0.6.1

- Autoreload mutex and exception management
- Helm Values multi windows support fix

## 0.6.0

- `KUBECONFIG` Contexts multi-keyword search
- `status.conditions` missing error handled
- The Kubeconfig Reload now will update also the `KUBECONFIG` Contexts
- Startup issues with the `KUBECONFIG` file handled
- Utility to get always the latest versions added: `utils/get-latest-version.ps1`

## 0.5.0

- Exception handling during the Auto Reload
- Last column sorting honored on reload
- `KUBECONFIG` Contexts switch dropdown menu
- Minor improvements

## 0.4.1

- Fixing `Menu > Reconcile > All GitRepository` output concurrency making the operations in sequence
- Trying to fix the closing window issue, handling the icon removal exceptions
- Fixing the Helm Values Revisions header size issue
- Helm get values and uninstall improvements and bug fixing

## 0.4.0

- Changelog added
- Flux Reconcile commands are now separate processes
- Dynamic icon generation
- Minor improvements