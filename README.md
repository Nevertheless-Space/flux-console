# NTL Flux Console

## Summary

This is an experimental UI for the FluxCD Kubernetes Resources.

This UI will rely on the `KUBECONFIG` environment variable for the Kubernetes API.

## Prerequisites

- Flux CLI (`>= 0.29` Recommended)
- Helm CLI (`>= 3.7.0` Recommended)
- Kubectl CLI (`>= 1.20` Recommended)

## Search

Words in the search, obtained by splitting on single spaces, will be used in this way:

- All the strings will be converted in lowercase
- **Basic search**: `<word>` or `<word1> <word2> <word3>`
  - All the rows containing all the words in any column, except for the `Suspended` column, will be returned
- **Exclusion search**: `!<word>` or `!<word1> !<word2> !<word3>`
  - All the rows NOT containing all the words in any column, except for the `Suspended` column, will be returned
- **Column search**: `helmrelease:myhelmrelease` or `helmrelease:myhelmrelease1 status:true namespace:mynamespace suspended:true`
  - All the rows with the EXACT match of `<column name>:<column value>` will be returned
- All the concepts previously illustrated can be combined with each other