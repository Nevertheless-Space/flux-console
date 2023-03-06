# NTL Flux Console

## Summary

This is an experimental UI for the FluxCD Kubernetes Resources.

This UI will rely on the `KUBECONFIG` environment variable for the Kubernetes API.

## Prerequisites

- Flux CLI (`>= 0.29.0` Recommended)
- Helm CLI (`>= 3.7.0` Recommended)
- Kubectl CLI (`>= 1.20.0` Recommended)

## Search

### Main Search

Words in the search, obtained by splitting on single spaces, will be used in this way:

- All the strings will be converted in lowercase
- **Basic search**: `<word>` or `<word1> <word2> <word3>`
  - All the rows containing all the words in any column, except for the `Suspended` column, will be returned
- **Exclusion search**: `!<word>` or `!<word1> !<word2> !<word3>`
  - All the rows NOT containing all the words in any column, except for the `Suspended` column, will be returned
- **Column search**: `helmrelease:myhelmrelease` or `helmrelease:myhelmrelease1 status:true namespace:mynamespace suspended:true`
  - All the rows with the EXACT match of `<column name>:<column value>` will be returned
- All the concepts previously illustrated can be combined with each other

### KUBECONFIG Contexts Search

Words in the search, obtained by splitting on single spaces, will be used in this way:

- All the strings will be converted in lowercase
- Basic multi-keywords search: `<word>` or `<word1> <word2> <word3>`
  - All the KUBECONFIG Contexts containing all the words will be returned

The search will be triggered by the `ENTER` button pression.

## Utils

### get-latest-version.ps1

Using the Powershell script located [here](./utils/get-latest-version.ps1), getting the latest versions will be easier.

The script will: **delete everything in the running folder** except itself, and then download the latest version. So, <u>put the script (without changing its name) in a folder together with the NTL Flux Console only</u>.

Usage:
1. Be sure the NTL Flux Console is closed
2. Run the script
3. Open the new NTL Flux Console