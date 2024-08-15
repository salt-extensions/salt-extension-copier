from collections import ChainMap
from pathlib import Path

import yaml
from copier import run_copy
from copier import run_update
from pytest_copie.plugin import Copie
from pytest_copie.plugin import Result
from pytest_copie.plugin import _add_yaml_include_constructor


def load_copier_yaml(template_dir: Path | None = None) -> ChainMap:
    template_dir = template_dir or Path(".")
    files = template_dir.glob("copier.*")
    try:
        copier_yaml = next(f for f in files if f.suffix in [".yaml", ".yml"])
    except StopIteration as err:
        raise FileNotFoundError("No copier.yaml configuration file found.") from err
    _add_yaml_include_constructor(template_dir)
    return ChainMap(*list(yaml.safe_load_all(copier_yaml.read_text())))


class UpgradedCopie(Copie):

    def copy(
        self,
        extra_answers: dict | None = None,
        template_dir: Path | None = None,
        vcs_ref: str = "HEAD",
    ) -> Result:
        """
        Patch Copie to accept a ``vcs_ref`` parameter.

        This method is copied from pytest_copie.Copie.copy
        """
        # set the template dir and the associated copier.yaml file
        template_dir = template_dir or self.default_template_dir

        # create a new output_dir in the test dir based on the counter value
        (output_dir := self.test_dir / f"copie{self.counter:03d}").mkdir()
        self.counter += 1

        try:
            # make sure the copiercopier project is using subdirectories
            all_params = load_copier_yaml(template_dir)
            if not any("_subdirectory" in params for params in all_params):
                raise ValueError(
                    "The plugin can only work for templates using subdirectories, "
                    '"_subdirectory" key is missing from copier.yaml'
                )

            worker = run_copy(
                src_path=str(template_dir),
                dst_path=str(output_dir),
                unsafe=True,
                defaults=True,
                user_defaults=extra_answers if extra_answers is not None else {},
                vcs_ref=vcs_ref,
            )

            # refresh project_dir with the generated one
            # the project path will be the first child of the ouptut_dir
            project_dir = Path(worker.dst_path)

            # refresh answers with the generated ones and remove private stuff
            answers = worker._answers_to_remember()
            answers = {q: a for q, a in answers.items() if not q.startswith("_")}

            return Result(project_dir=project_dir, answers=answers)

        except SystemExit as e:
            return Result(exception=e, exit_code=e.code)
        except Exception as e:  # pylint: disable=broad-except
            return Result(exception=e, exit_code=-1)

    def update(
        self, project_dir: Path, extra_answers: dict | None = None, vcs_ref: str = "HEAD"
    ) -> Result:
        try:
            worker = run_update(
                dst_path=project_dir,
                unsafe=True,
                defaults=True,
                skip_answered=True,
                overwrite=True,
                user_defaults=extra_answers if extra_answers is not None else {},
                vcs_ref=vcs_ref,
            )

            # refresh answers with the generated ones and remove private stuff
            answers = worker._answers_to_remember()
            answers = {q: a for q, a in answers.items() if not q.startswith("_")}

            return Result(project_dir=project_dir, answers=answers)

        except SystemExit as err:
            return Result(exception=err, exit_code=err.code)
        except Exception as err:  # pylint: disable=broad-except
            return Result(exception=err, exit_code=-1)
