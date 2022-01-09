import sys
from time import sleep
from typing import List, Optional, Dict, Any
from PyAltiumRun.helpers import AltiumHelper
import os
import subprocess


class AltiumRun:
    """An Altium runner object

    This object holds the configuration parameters to create a Altium scripting project and run it accordingly.
    """

    def __init__(self, altium_version: Optional[str] = None, use_internal_logger: bool = True):
        self.set_used_altium_version()
        self._project_path = os.path.dirname(sys.argv[0]) + "/scripting_project"

        self.external_scripts_path: List[str] = []
        r"""A list of all the paths to the needed scripts."""

        self._internal_scripts_path: List[str] = []

        self._use_internal_logger = use_internal_logger
        self._project_path_to_open: Optional[str] = None
        self._function_name_to_run: str = "main"
        self._function_parameters_to_run: List[Any] = []

        self._process: Optional[subprocess.Popen[bytes]] = None

    def get_altium_versions(self) -> List[str]:
        r"""Gets all the installed Altium designer versions on this system.

        :return: A list of strings
        """
        return AltiumHelper.get_installed_versions()

    def set_used_altium_version(self, version: Optional[str] = None) -> bool:
        r"""Set the Altium version to use.
        The full version is needed by this function wich is given by :func:`AltiumRun.get_altium_versions`

        :param version: The full version of the Altium designer you want to use.
        :return: If the version set was succesfull or not.
        """
        altium_install = AltiumHelper.get_install_path(version)
        if altium_install is None:
            return False
        self._altium_path = altium_install + r"\X2.exe"
        return True

    def set_scripting_project_path(self, path: str) -> None:
        r"""Set the path where the scripting project will be created.
        By default this project will be created in a folder called "scripting_project" next to the main script.

        :param path: The wanted scripting project path, this can be relative to the main script or absolute.
        """
        self._project_path = os.path.dirname(path)

    def get_scripting_project_path(self) -> str:
        r"""Get the current scripting project path.

        :return: The current scripting project path in form of a string.
        """
        return self._project_path

    def get_log_file_path(self) -> Optional[str]:
        r"""Get the file path of the log file.

        :return: The current log file path in form of a string.
        Returns None if the internal logger is not used.
        """
        if not self._use_internal_logger:
            return None
        return os.path.abspath(self._project_path + "/data/log.txt")

    def clear_log_file(self) -> None:
        r"""Clear the log file.
        This function does nothing when the internal logger is not used.
        """
        log_file_path = self.get_log_file_path()
        if log_file_path is None:
            return
        try:
            file = open(log_file_path, 'w')
            file.close()
        except FileNotFoundError:
            return  # The directory was not created yet so the log is empty

    def add_script(self, script_path: str) -> None:
        r"""Add a script to the scripting project.
        This can be the main script to run or a library needed.

        :param script_path: The path to the script.
        """
        if script_path not in self.external_scripts_path:
            self.external_scripts_path.append(script_path)

    def remove_script(self, script_path: str) -> None:
        r"""Remove a script from the scripting project.

        :param script_path: The path to the script to remove.
        """
        if script_path in self.external_scripts_path:
            self.external_scripts_path.remove(script_path)

    def clear_scripts(self) -> None:
        r"""Remove all scipts from the scripting project."""
        self.external_scripts_path.clear()

    def set_project_to_open(self, project_path: Optional[str]) -> None:
        r"""Set the path to the Altium project to open.
        This is the PCB or MultiPCB project to run the given scripts on.
        None can be passed to this function to state that no project must be opened.

        :param project_path: The path to the project to open.
        """
        self._project_path_to_open = project_path

    def get_project_to_open(self) -> Optional[str]:
        r"""Get the path to the Altium project to open.
        This function returns None if no project has to be opened.

        :return: The path to the Altium project to open.
        """
        return self._project_path_to_open

    def set_function_name(self, function_name: str) -> None:
        r"""Set the name of the function to run in the Altium script.

        :param function_name: The name of the function to run in the Altium script as string.
        """
        self._function_name_to_run = function_name

    def get_function_name(self) -> str:
        r"""Get the name of the function to run in the Altium script.

        :return: The name of the function to run in the Altium script as string.
        """
        return self._function_name_to_run

    def set_function_parameters(self, *args: List[Any]) -> None:
        r"""Set the arguments given to the Altium script function.

        :param args: The arguments given to the Altium script function.
        """
        self._function_parameters_to_run.clear()
        for arg in args:
            self._function_parameters_to_run.append(arg)

    def set_function(self, function_name: str, *args: List[Any]) -> None:
        r"""Set the function name and arguments of the Altium script function needed to be run.

        :param function_name: The name of the function to run in the Altium script as string.
        :param args: The arguments given to the Altium script function.
        """
        self.set_function_name(function_name)
        self.set_function_parameters(*args)

    def run(self, wait_until_finished: bool = True, timeout: float = 10) -> bool:
        r"""Runs the script based on the settings defined.

        If Altium Designer is running it will run the script in that instance and leave it open.
        If Altium Desinger is not running it will start a new instance and close it when finished.

        This functions waits until the script is finished when the :param:`wait_until_finished` parameter is True.
        A timeout can be set for this waiting on finish.

        :param wait_until_finished: If the function should wait for the script to finish.
        :param timeout: The timeout when waiting for the script to finish.
        :return: True, if the script is finished.
        """
        # Generate the path for the scripting project
        if not os.path.exists(self._project_path):
            os.makedirs(self._project_path)
        if not os.path.exists(self._project_path + "/data"):
            os.makedirs(self._project_path + "/data")

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
        if wait_until_finished:
            return self.wait_until_finished(timeout)
        return self.wait_until_finished(0.1)

    def wait_until_finished(self, timeout: float = 10.0) -> bool:
        r"""Wait for a running script to finish.

        :param timeout: The timeout for this wait.
        :return: True, if the script finished successfully.
        """
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
        with open(self._project_path + "/script_project.PrjScr", 'w') as f:
            f.write('[Design]\n')
            f.write('Version=1.0\n')
            f.write('\n')
            for i, script in enumerate(self._internal_scripts_path + self.external_scripts_path, start=1):
                path = os.path.abspath(script)
                f.write(f'[Document{i}]\n')
                f.write(f'DocumentPath={path}\n')
                f.write('\n')

    def _generate_logger_script(self) -> None:
        self._internal_scripts_path.append(self._project_path + "/logger.pas")
        variables = {
            "LogFilePath": self.get_log_file_path(),
        }
        file = open(str(variables["LogFilePath"]), 'a+')
        file.write("Startup Altium script\n")
        file.close()
        self._generate_script_from_base("logger.pas", variables)

    def _generate_main_script(self) -> None:
        self._internal_scripts_path.append(self._project_path + "/main.pas")
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
            if len(text) > 1:
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
