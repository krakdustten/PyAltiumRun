import winreg
from typing import List, Optional, Any


def get_installed_versions() -> List[str]:
    ol: List[str] = []
    top_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Altium\Builds", 0, winreg.KEY_READ)
    i: int = 0
    while True:
        try:
            build_key_name = winreg.EnumKey(top_key, i)
            build_key_path = "%s\\%s" % (r"SOFTWARE\Altium\Builds", build_key_name)
            build_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, build_key_path, 0, winreg.KEY_READ)
            full_build_str = winreg.QueryValueEx(build_key, "FullBuild")[0]
            if type(full_build_str) is str:
                ol.append(full_build_str)
            i += 1
        except WindowsError:
            break
    return ol


def get_install_path(version: Optional[str] = None) -> Optional[str]:
    var = get_build_var("ProgramsInstallPath", version)
    if type(var) is str:
        return var
    return None


def get_build_var(var_name: str, version: Optional[str] = None) -> Any:
    top_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Altium\Builds", 0, winreg.KEY_READ)
    i: int = 0
    while True:
        try:
            build_key_name = winreg.EnumKey(top_key, i)
            build_key_path = "%s\\%s" % (r"SOFTWARE\Altium\Builds", build_key_name)
            build_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, build_key_path, 0, winreg.KEY_READ)
            full_build_str = winreg.QueryValueEx(build_key, "FullBuild")[0]
            build_str = winreg.QueryValueEx(build_key, "Build")[0]
            var_str = winreg.QueryValueEx(build_key, var_name)[0]
            if version is None:
                return var_str
            if type(full_build_str) is str:
                if full_build_str == version:
                    return var_str
            if type(build_str) is str:
                if build_str == version:
                    return var_str
            i += 1
        except WindowsError:
            return None
