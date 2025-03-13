# pylint: disable=consider-using-f-string

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Union

import pytest
from plumbum import ProcessExecutionError
from plumbum import local

log = logging.getLogger(__name__)


def _default_venv_dir():
    return Path(tempfile.mkdtemp())


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: Union[str, bytes]
    stderr: Union[str, bytes]
    cmdline: list


@dataclass
class VirtualEnv:
    venv_dir: Path = field(default_factory=_default_venv_dir, kw_only=True)
    env: dict = field(default_factory=dict, kw_only=True)
    system_site_packages: bool = field(default=False, kw_only=True)
    full_environ: dict = field(init=False, repr=False)
    venv_python: Path = field(init=False, repr=False)
    venv_bin_dir: Path = field(init=False, repr=False)

    def __post_init__(self):
        if platform.system() == "Windows":
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
        self.venv_bin_dir = self.venv_python.parent
        environ = os.environ.copy()
        environ["VIRTUAL_ENV"] = str(self.venv_dir)
        environ["PATH"] = f"{self.venv_bin_dir}{os.pathsep}{environ['PATH']}"
        if self.env:
            environ.update(self.env)
        self.full_environ = environ

    def __enter__(self):
        try:
            self._create_virtualenv()
        except subprocess.CalledProcessError as err:
            raise AssertionError("Failed to create virtualenv") from err
        return self

    def __exit__(self, *args):
        shutil.rmtree(str(self.venv_dir), ignore_errors=True)

    def install(self, *args, **kwargs):
        return self.run_module("pip", "install", *args, **kwargs)

    def uninstall(self, *args, **kwargs):
        return self.run_module("pip", "uninstall", "-y", *args, **kwargs)

    def run_module(self, module, *args, **kwargs):
        return self.run(str(self.venv_python), "-m", module, *args, **kwargs)

    def run(self, *args, **kwargs):
        check = kwargs.pop("check", True)
        # kwargs.setdefault("cwd", tempfile.gettempdir())
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
        kwargs.setdefault("universal_newlines", True)
        if env_kwarg := kwargs.pop("env", None):
            env = self.full_environ.copy()
            env.update(env_kwarg)
        else:
            env = self.full_environ
        proc = subprocess.run(args, check=False, env=env, **kwargs)

        ret = ProcessResult(
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            cmdline=proc.args,
        )
        log.debug(ret)
        if check is True:
            proc.check_returncode()

        return ret

    @staticmethod
    def get_real_python():
        """
        The reason why the virtualenv creation is proxied by this function is mostly
        because under windows, we can't seem to properly create a virtualenv off of
        another virtualenv(we can on linux) and also because, we really don't want to
        test virtualenv creation off of another virtualenv, we want a virtualenv created
        from the original python.
        Also, on windows, we must also point to the virtualenv binary outside the existing
        virtualenv because it will fail otherwise
        """
        try:
            if sys.platform.startswith("win"):
                return os.path.join(sys.real_prefix, os.path.basename(sys.executable))
            python_binary_names = [
                "python{}.{}".format(*sys.version_info),
                "python{}".format(*sys.version_info),
                "python",
            ]
            for binary_name in python_binary_names:
                python = os.path.join(sys.real_prefix, "bin", binary_name)
                if os.path.exists(python):
                    break
            else:
                raise AssertionError(
                    "Couldn't find a python binary name under '{}' matching: {}".format(
                        os.path.join(sys.real_prefix, "bin"), python_binary_names
                    )
                )
            return python
        except AttributeError:
            return sys.executable

    def run_code(self, code_string, python=None, **kwargs):
        if code_string.startswith("\n"):
            code_string = code_string[1:]
        code_string = textwrap.dedent(code_string).rstrip()
        log.debug("Code to run passed to python:\n>>>>>>>>>>\n%s\n<<<<<<<<<<", code_string)
        if python is None:
            python = str(self.venv_python)
        return self.run(python, "-c", code_string, **kwargs)

    def get_installed_packages(self):
        data = {}
        ret = self.run_module("pip", "list", "--format", "json")
        for pkginfo in json.loads(ret.stdout):
            data[pkginfo["name"]] = pkginfo["version"]
        return data

    def _create_virtualenv(self):
        virtualenv = shutil.which("virtualenv")
        if not virtualenv:
            pytest.fail("'virtualenv' binary not found")
        cmd = [
            virtualenv,
            f"--python={self.get_real_python()}",
        ]
        if self.system_site_packages:
            cmd.append("--system-site-packages")
        cmd.append(str(self.venv_dir))
        self.run(*cmd, cwd=str(self.venv_dir.parent))
        self.run_module("ensurepip")
        log.debug("Created virtualenv in %s", self.venv_dir)


@dataclass
class ProjectVenv(VirtualEnv):
    project_dir: Path = Path(".")

    def __post_init__(self):
        self.env.update(
            {
                "COVERAGE_FILE": "",
                "COVERAGE_RUN": "",
                "NOX_CURRENT_SESSION": "",
                "PYTEST_VERSION": "",
                "PYTEST_CURRENT_TEST": "",
            }
        )
        self.venv_dir = self.project_dir / ".venv"
        super().__post_init__()

    def _create_virtualenv(self):
        with local.cwd(self.project_dir):
            try:
                local["git"]("status")
            except ProcessExecutionError:
                # installation needs to be run inside a git repository
                local["git"]("init", "--initial-branch=main")
        if not (self.venv_dir / "pyvenv.cfg").exists():
            super()._create_virtualenv()
        self.install(f"{self.project_dir}[dev,docs,tests]")
