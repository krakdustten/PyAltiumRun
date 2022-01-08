import sys
from time import sleep
from typing import List, Optional, Dict, Any
from PyAltiumRun.helpers import AltiumHelper
import os
import subprocess


class AltiumRun:
    def __init__(self, altium_version: Optional[str] = None, use_internal_logger: bool = True):
        self.set_used_altium_version()
        self._project_path = os.path.dirname(sys.argv[0]) + "/scripting_project"
        self.external_scripts_path: List[str] = []
        self._internal_scripts_path: List[str] = []

        self._use_internal_logger = use_internal_logger
        self._project_path_to_open: Optional[str] = None
        self._function_name_to_run: str = "main"
        self._function_parameters_to_run: List[Any] = []

        self._process: Optional[subprocess.Popen[bytes]] = None

    def get_altium_versions(self) -> List[str]:
        return AltiumHelper.get_installed_versions()

    def set_used_altium_version(self, version: Optional[str] = None) -> bool:
        altium_install = AltiumHelper.get_install_path(version)
        if altium_install is None:
            return False
        self._altium_path = altium_install + r"\X2.exe"
        return True

    def set_scripting_project_path(self, path: str) -> None:
        self._project_path = os.path.dirname(path)

    def get_scripting_project_path(self) -> str:
        return self._project_path

    def get_log_file_path(self) -> Optional[str]:
        if not self._use_internal_logger:
            return None
        return self._project_path + "/data/log.txt"

    def clear_log_file(self) -> None:
        log_file_path = self.get_log_file_path()
        if log_file_path is None:
            return
        file = open(log_file_path, 'w')
        file.close()

    def add_script(self, script_path: str) -> None:
        if script_path not in self.external_scripts_path:
            self.external_scripts_path.append(script_path)

    def remove_script(self, script_path: str) -> None:
        if script_path in self.external_scripts_path:
            self.external_scripts_path.remove(script_path)

    def clear_scripts(self) -> None:
        self.external_scripts_path.clear()

    def set_project_to_open(self, project_path: Optional[str]) -> None:
        self._project_path_to_open = project_path

    def get_project_to_open(self) -> Optional[str]:
        return self._project_path_to_open

    def set_function_name_to_run(self, function_name: str) -> None:
        self._function_name_to_run = function_name

    def get_function_name_to_run(self) -> str:
        return self._function_name_to_run

    def set_function_parameters(self, *args : List[Any]) -> None:
        self._function_parameters_to_run.clear()
        for arg in args:
            self._function_parameters_to_run.append(arg)

    def run(self) -> bool:
        self._internal_scripts_path.clear()
        if self._use_internal_logger:
            self._generate_logger_script()
        self._generate_main_script()
        self._generate_scripting_project()

        project = (self._project_path + "/script_project.PrjScr").replace("/", "\\")
        script = "main.pas>SCRIPTING_SYSTEM_MAIN"
        command = f"\"{self._altium_path}\" -RScriptingSystem:RunScript(ProjectName=\"{project}\"|ProcName=\"{script}\")"

        f_running = open(self._project_path + "/data/running", 'w')
        f_running.write("")
        f_running.close()

        self._process = subprocess.Popen(command)
        return self.wait_until_finished(1000)

    def wait_until_finished(self, timeout: float = 10.0) -> bool:
        if self._process is None:
            return True
        for i in range(int(timeout * 10)):
            if not os.path.isfile(self._project_path + "/data/running"):
                self._process.kill()
                return True
            if self._process.poll() is not None:
                return True
            sleep(0.1)
        return False

    def _generate_scripting_project(self) -> None:
        # Generate the path for the scripting project
        if not os.path.exists(self._project_path):
            os.makedirs(self._project_path)
        if not os.path.exists(self._project_path + "/data"):
            os.makedirs(self._project_path + "/data")

        with open(self._project_path + "/script_project.PrjScr", 'w') as f:
            f.write('[Design]\n')
            f.write('Version=1.0\n')
            f.write('\n')
            for i, script in enumerate(self._internal_scripts_path + self.external_scripts_path, start=1):
                f.write(f'[Document{i}]\n')
                f.write(f'DocumentPath={script}\n')
                f.write('\n')

    def _generate_logger_script(self) -> None:
        self._internal_scripts_path.append("logger.pas")
        variables = {
            "LogFilePath": self.get_log_file_path(),
        }
        file = open(str(variables["LogFilePath"]), 'a+')
        file.write("Startup Altium script\n")
        file.close()
        self._generate_script_from_base("logger.pas", variables)

    def _generate_main_script(self) -> None:
        self._internal_scripts_path.append("main.pas")
        parameters = ""
        for param in self._function_parameters_to_run:
            part = self._convert_param_to_delphi(param)
            if part is not None:
                parameters += part + ", "
        if len(parameters) > 0:
            parameters = parameters[:-2]
        variables = {
            "DataFolder": self._project_path + "/data/",
            "ProjectFilePath": self._project_path_to_open,
            "FunctionName": self._function_name_to_run,
            "FunctionParameters": parameters
        }
        self._generate_script_from_base("main.pas", variables)

    def _convert_param_to_delphi(self, param: Any) -> Optional[str]:
        if type(param) is str:
            return f"'{param}'"
        elif type(param) in [int, float]:
            return f"{param}"
        elif type(param) is bool:
            return f"{param}"
        elif type(param) is list:
            text = "["
            for par in param:
                part = self._convert_param_to_delphi(par)
                if part is not None:
                    text += part + ", "
            if len(text) > 0:
                text = text[:-2]
            return text + "]"
        print(type(param))
        return None

    def _generate_script_from_base(self, name: str, variables: Dict[str, Any] = {}) -> None:
        origin = os.path.dirname(os.path.abspath(__file__)) + '\\scriptingbase\\' + name
        destination = self._project_path + '/' + name
        self._generate_script_from_source(origin, destination, variables)

    def _generate_script_from_source(self, origin: str, destination: str, variables: Dict[str, Any] = {}) -> None:
        f_or = open(origin, 'r')
        f_de = open(destination, 'w')
        line = f_or.readline()
        while line:
            line = line.format(**variables)
            f_de.write(line)
            line = f_or.readline()
        f_or.close()
        f_de.close()



