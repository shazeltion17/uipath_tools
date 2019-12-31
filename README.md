# uipath_tools

*Python wrapper for UiPath Orchestrator.  Do simply things like create a robot, create a machine, start a job, stop a job.*

## Install
To install the package use:
```shell
pip install uipath_tools
```

## Usage
To use, simply authenticate:
```python
from uipath_tools import uipathorchestratorapi as uip

con = uip.UiPathConnection('<url>', '<tenant>', '<username>', '<password>')
con.authenticate()
releaseKey = con.getReleaseKey("<job_environment>")
con.startJob(releaseKey)
```
