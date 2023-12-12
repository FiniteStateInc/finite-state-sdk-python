<p align="center">
  <img src="https://finitestate.io/hs-fs/hubfs/FS-Logo-Final-01.png" />
</p>

# What is [Finite State](https://finitestate.io)

[Finite State](https://finitestate.io) manages risk across your software supply chain so that you can minimize risk, ship confidently, and reduce attack surface. Finite State reduces software supply chain risk with end-to-end SBOM solutions for the connected world.

The cloud-based SaaS platform for SBOM and Product Security management enables you to:

* Generate and manage SBOMs in any format to create software transparency
* Orchestrate and correlate scan findings from over 120 top scanning tools
* Monitor AppSec and Product Security risk across product portfolios to visualize risk scoring and prioritize critical findings
* Leverage world-class binary SCA to generate the most thorough and accurate SBOMs available

# [Finite State](https://finitestate.io) SDK

Finite State's powerful GraphQL API gives you and your teams access to the incredibly rich data you have in the platform. These SDKs, tools, and examples help your team to connect to Finite State APIs quickly and easily.

# Installing the Python SDK

View the Python API Docs here: [https://finitestateinc.github.io/finite-state-sdk-python/finite_state_sdk.html](https://finitestateinc.github.io/finite-state-sdk-python/finite_state_sdk.html).

```
$ pip3 install finite-state-sdk
```

To use it:

```
import finite_state_sdk
```

## Generating the docs

```bash
pip3 install pdoc
export VERSION=0.0.4
pdoc -o docs -d google --logo "https://camo.githubusercontent.com/ea2191106c0aa7006f669bef130bf089bb3fedc0463bcecebeabbefd6b4362ad/68747470733a2f2f66696e69746573746174652e696f2f68732d66732f68756266732f46532d4c6f676f2d46696e616c2d30312e706e67" -t ./docs-template ./finite_state_sdk
```

# Finite State API

For more information about Finite State's APIs, see: [https://docs.finitestate.io](https://docs.finitestate.io).

Our teams are working to add additional programming language and package manager support for Finite State SDKs.
