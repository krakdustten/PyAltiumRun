from PyAltiumRun.AltiumRun import AltiumRun
from PyAltiumRun.helpers import AltiumHelper

run = AltiumRun(use_internal_logger=True)
run.set_project_to_open(r"C:\Users\Dylan\Downloads\iSensProV4_battery_connection2_v2-(src,fab,pcba)\SRC-iSensProV4_battery_connection2_v2-A.3\iSensProV4_battery_connection2_v2.PrjPcb")
run.set_function_parameters("test", 123, 785.04, False, True, ["test", 123, 87.0271, True, "why"])
run.run()

