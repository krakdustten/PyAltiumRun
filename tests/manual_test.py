from PyAltiumRun.AltiumRun import AltiumRun

run = AltiumRun(use_internal_logger=True)
run.clear_log_file()
run.set_project_to_open(r"Altium_project/Arduino_uno.PrjPcb")
run.add_script(r"Altium_scripts/generate_docs.pas")
run.set_function("gen_docs", "Arduino_uno")
run.run()

