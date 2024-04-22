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

### Setting docs generation project

`docs-generation` folder is the python project to generate html documentation.

`./docs-generation/pyproject.toml` is the Poetry file project. It should run with python 3.9 or up.

Should run once the following commands. This is an example with pyenv and python 3.11.

```bash
cd docs-generation
pyenv local 3.11
poetry env use 3.11
poetry install
```

### Generation docs.

From project root folder.

```bash
export VERSION=0.0.4
./scripts/generate-docs.sh
```

# Finite State API

For more information about Finite State's APIs, see: [https://docs.finitestate.io](https://docs.finitestate.io).

Our teams are working to add additional programming language and package manager support for Finite State SDKs.
