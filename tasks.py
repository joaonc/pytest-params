import os
from pathlib import Path

from invoke import Collection, Exit, task

os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = PROJECT_ROOT.name
SOURCE_DIR = PROJECT_ROOT / 'src' / PROJECT_NAME
BUILD_DIST_DIR = PROJECT_ROOT / 'dist'

# Requirements files
REQUIREMENTS_MAIN = 'main'
REQUIREMENTS_FILES = {
    REQUIREMENTS_MAIN: 'requirements',
    'dev': 'requirements-dev',
}
"""
Requirements files.
Order matters as most operations with multiple files need ``requirements.txt`` to be processed
first.
Add new requirements files here.
"""

REQUIREMENTS_TASK_HELP = {
    'requirements': '`.in` file. Full name not required, just the initial name after the dash '
    f'(ex. "dev"). For main file use "{REQUIREMENTS_MAIN}". Available requirements: '
    f'{", ".join(REQUIREMENTS_FILES)}.'
}


def _csstr_to_list(csstr: str) -> list[str]:
    """
    Convert a comma-separated string to list.
    """
    return [s.strip() for s in csstr.split(',')]


def _get_requirements_file(requirements: str, extension: str) -> str:
    """
    Return the full requirements file name (with extension).

    :param requirements: The requirements file to retrieve. Can be the whole filename
        (no extension), ex `'requirements-dev'` or just the initial portion, ex `'dev'`.
        Use `'main'` for the `requirements` file.
    :param extension: Requirements file extension. Can be either `'in'` or `'txt'`.
    """
    filename = REQUIREMENTS_FILES.get(requirements, requirements)
    if filename not in REQUIREMENTS_FILES.values():
        raise Exit(f'`{requirements}` is an unknown requirements file.')

    return f'{filename}.{extension.lstrip(".")}'


def _get_requirements_files(requirements: str | None, extension: str) -> list[str]:
    extension = extension.lstrip('.')
    if requirements is None:
        requirements_files = list(REQUIREMENTS_FILES)
    else:
        requirements_files = _csstr_to_list(requirements)

    # Get full filename+extension and sort by the order defined in `REQUIREMENTS_FILES`
    filenames = [
        _get_requirements_file(r, extension) for r in REQUIREMENTS_FILES if r in requirements_files
    ]

    return filenames


@task(
    help={'no_upload': 'Do not upload to Pypi.'},
)
def build_publish(c, no_upload: bool = False):
    """
    Publish package to Pypi.
    """
    dist_dir = BUILD_DIST_DIR / 'package'
    # Create distribution files (source and wheel)
    c.run('flit ... FINISH')
    # Upload to pypi
    if not no_upload:
        c.run(f'twine upload "{dist_dir}/*"')


@task
def lint_black(c, path='.'):
    c.run(f'black {path}')


@task
def lint_flake8(c, path='.'):
    c.run(f'flake8 {path}')


@task
def lint_isort(c, path='.'):
    c.run(f'isort {path}')


@task
def lint_mypy(c, path='.'):
    c.run(f'mypy {path}')


@task(lint_isort, lint_black, lint_flake8, lint_mypy)
def lint_all(c):
    """
    Run all linters.
    Config for each of the tools is in ``pyproject.toml`` and ``setup.cfg``.
    """
    print('Done')


@task
def test_unit(c):
    """
    Run unit tests.
    """
    c.run('python -m pytest')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_compile(c, requirements=None):
    """
    Compile requirements file(s).
    """
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_sync(c, requirements=None):
    """
    Synchronize environment with requirements file.
    """
    c.run(f'pip-sync {" ".join(_get_requirements_files(requirements, "txt"))}')


@task(
    help=REQUIREMENTS_TASK_HELP | {'package': 'Package to upgrade. Can be a comma separated list.'}
)
def pip_package(c, requirements, package):
    """
    Upgrade package.
    """
    packages = [p.strip() for p in package.split(',')]
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile --upgrade-package {" --upgrade-package ".join(packages)} {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_upgrade(c, requirements):
    """
    Try to upgrade all dependencies to their latest versions.
    """
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile --upgrade {filename}')


ns = Collection()  # Main namespace

test_collection = Collection('test')
test_collection.add_task(test_unit, 'unit')

build_collection = Collection('build')
build_collection.add_task(build_publish, 'publish')

lint_collection = Collection('lint')
lint_collection.add_task(lint_all, 'all')
lint_collection.add_task(lint_black, 'black')
lint_collection.add_task(lint_flake8, 'flake8')
lint_collection.add_task(lint_isort, 'isort')
lint_collection.add_task(lint_mypy, 'mypy')

pip_collection = Collection('pip')
pip_collection.add_task(pip_compile, 'compile')
pip_collection.add_task(pip_package, 'package')
pip_collection.add_task(pip_sync, 'sync')
pip_collection.add_task(pip_upgrade, 'upgrade')

ns.add_collection(build_collection)
ns.add_collection(lint_collection)
ns.add_collection(pip_collection)
ns.add_collection(test_collection)
