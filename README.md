PyAltiumRun

[![PyPI version](https://badgen.net/pypi/v/PyAltiumRun)](https://pypi.org/project/PyAltiumRun/)  [![PyPI version](https://badgen.net/pypi/license/PyAltiumRun)](https://github.com/krakdustten/PyAltiumRun/blob/master/LICENSE) [![PyPI version](https://badgen.net/pypi/python/PyAltiumRun)](https://pypi.org/project/PyAltiumRun/)

A Python interface that can run Delphiscript scripts in [Altium Designer](https://www.altium.com/).

New features can be requested in the [Github Issues](https://github.com/krakdustten/PyAltiumRun/issues).

## Installation requirements

Altium designer must be installed before running this library.

## Quick start

~~~python
from PyAltiumRun.AltiumRun import AltiumRun

run = AltiumRun(use_internal_logger=True)                       #Create runner object
run.clear_log_file()                                            #Clear the logs of the previous run
run.set_project_to_open(r"Altium_project/Arduino_uno.PrjPcb")   #Define an Altium project to open
run.add_script(r"Altium_scripts/generate_docs.pas")             #Add a script to the runner
run.set_function("gen_docs", "Arduino_uno")                     #Set the function to run
run.run()                                                       #Run
~~~
