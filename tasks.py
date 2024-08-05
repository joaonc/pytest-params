import os
import re
from pathlib import Path

from invoke import Collection, Exit, task

os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = PROJECT_ROOT.name.replace('-', '_')  # 'pytest_params'
SOURCE_DIR = PROJECT_ROOT / 'src' / PROJECT_NAME

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

BUILD_DIST_DIR = PROJECT_ROOT / 'dist'

VERSION_FILES = [
    PROJECT_ROOT / 'pyproject.toml',
    SOURCE_DIR / '__init__.py',
]
"""
Files that contain the package version.
This version needs to be updated with each release.
"""


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


def _get_project_version() -> str:
    pattern = re.compile('''^[ _]*version[ _]*[:=] *['"](.*)['"]''', re.MULTILINE)
    versions = {}
    for file in VERSION_FILES:
        with open(file) as f:
            text = f.read()
        match = pattern.search(text)
        if not match:
            raise Exit(f'Could not find version in `{file.relative_to(PROJECT_ROOT)}`.')
        versions[file] = match.group(1)

    if len(set(versions.values())) != 1:
        raise Exit(
            'Version mismatch in files that contain versions.\n'
            + (
                '\n'.join(
                    f'{file.relative_to(PROJECT_ROOT)}: {version}'
                    for file, version in versions.items()
                )
            )
        )

    return list(versions.values())[0]


def _update_project_version(version: str):
    pattern = re.compile('''^([ _]*version[ _]*[:=] *['"])(.*)(['"].*)$''', re.MULTILINE)
    for file in VERSION_FILES:
        with open(file) as f:
            text = f.read()
        new_text = pattern.sub(lambda match: f'{match.group(1)}{version}{match.group(3)}', text)
        with open(file, 'w') as f:
            f.write(new_text)


def _get_release_name_and_tag(version: str) -> tuple[str, str]:
    """
    Generate release name and tag based on the version.

    :return: Tuple with release name (ex 'v1.2.3') and tag (ex '1.2.3').
    """
    return f'v{version}', version


def _get_version_from_release_name(release_name: str) -> str:
    if not release_name.startswith('v'):
        raise Exit(f'Invalid release name: {release_name}')
    return release_name[1:]


def _get_latest_release() -> tuple[str, str]:
    """
    Retrieves the latest release from GitHub.

    :return: Tuple with release name (ex 'v1.2.3') and tag (ex '1.2.3').
    """
    import json
    import subprocess

    release_info_json = subprocess.check_output(['gh', 'release', 'view', '--json', 'name,tagName'])
    release_info = json.loads(release_info_json)
    return release_info['name'], release_info['tagName']


@task(
    help={
        'version': 'Version in semantic versioning format (ex 1.5.0). '
        'If `version` is set, then `bump` cannot be used.',
        'bump': 'Portion of the version to increase, can be "major", "minor", or "patch".'
        'If `bump` is set, then `version` cannot be used.',
    },
)
def build_version(c, version: str = '', bump: str = ''):
    """
    Updates the files that contain the project version to the new version.
    """
    from semantic_version import Version

    v1 = Version(_get_project_version())
    if version and bump:
        raise Exit('Either `version` or `bump` can be set, not both.')
    if not (version or bump):
        try:
            bump = {'1': 'major', '2': 'minor', '3': 'patch'}[
                input(
                    f'Current version is `{v1}`, which portion to bump?'
                    '\n1 - Major\n2 - Minor\n3 - Patch\n> '
                )
            ]
        except KeyError:
            raise Exit('Invalid choice.')

    if version:
        v2 = Version(version)
        if v2 <= v1:
            raise Exit(f'New version `{v2}` needs to be greater than the existing version `{v1}`.')
    else:
        try:
            v2 = getattr(v1, f'next_{bump.lower().strip()}')()
        except AttributeError:
            raise Exit('Invalid `bump` choice.')

    _update_project_version(str(v2))
    print(
        f'New version is {v2}. Modified files have not been commited:\n'
        + '\n'.join(f'{file.relative_to(PROJECT_ROOT)}' for file in VERSION_FILES)
    )


@task
def build_clean(c):
    """
    Delete files created from previous builds.
    """
    import shutil

    shutil.rmtree(BUILD_DIST_DIR, ignore_errors=True)


@task(
    build_clean,
    help={'no_upload': 'Do not upload to Pypi.'},
)
def build_publish(c, no_upload: bool = False):
    """
    Build package and publish (upload) to Pypi.
    """
    # Create distribution files (source and wheel)
    c.run('flit build')

    # Upload to pypi
    if not no_upload:
        version = _get_project_version()
        response = input(f'Publishing version {version} to Pypi. Press Y to confirm. ')
        if response.lower().strip() == 'y':
            c.run('flit publish')
        else:
            print('Package not published to Pypi.')


@task(
    help={
        'notes': 'Release notes.',
        'notes_file': 'Read release notes from file. Ignores the `--notes` parameter.',
    },
)
def build_release(
    c,
    notes: str = '',
    notes_file: str = '',
):
    """
    Create a release and tag in GitHub from the current project version.
    """
    from packaging.version import Version

    if not notes and not notes_file:
        response = input('No release notes or notes file specified, continue? [Y/n]')
        response = response.strip().lower() or 'y'
        if response not in ['yes', 'y']:
            raise Exit('No release notes specified.')

    # Check that there's no release with the current version
    version = Version(_get_project_version())
    latest_release, latest_tag = _get_latest_release()
    latest_version = Version(_get_version_from_release_name(latest_release))
    if str(latest_version) != latest_tag:
        raise Exit(
            f'Invalid format in latest release or tag: Release: {latest_release}, Tag: {latest_tag}'
        )

    if latest_version >= version:
        raise Exit(
            f'Release/tag version being created ({version}) needs to be greater than the current '
            f'latest release version ({latest_version}).'
        )

    # Create release
    new_release, new_tag = _get_release_name_and_tag(str(version))
    command = f'gh release create "{new_tag}" --title "{new_release}" --generate-notes'
    if notes:
        command += f' --notes "{notes}"'
    if notes_file:
        notes_file_path = Path(notes_file)
        command += f' --notes-file "{notes_file_path.resolve(strict=True)}"'

    response = input(f'Creating GitHub release `{new_release}`. Press Y to confirm. ')
    if response.lower().strip() == 'y':
        c.run(command)
        print('GitHub release created. Upload artifacts with `build.upload`.')
    else:
        print('GitHub release not created.')


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
    Temporarily installs the `pytest-params` package.
    """
    c.run('flit install')
    c.run('python -m pytest')
    c.run('pip uninstall pytest-params -y')


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
build_collection.add_task(build_version, 'version')
build_collection.add_task(build_clean, 'clean')
build_collection.add_task(build_publish, 'publish')
build_collection.add_task(build_release, 'release')

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
