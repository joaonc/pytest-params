# Publishing package
## Requirements
* `uv`  
  For the publishing process, [`uv`](https://docs.astral.sh/uv/) is used.  
  Install it separately (not via pip).
* Pypi account and API token  
  To publish to Pypi, an account is needed and an API token generated.  
  Go to [https://pypi.org](https://pypi.org/) and follow instructions.
* `UV_PUBLISH_TOKEN` environment variable  
  Set the Pypi token as an environment variable before publishing:
  ```
  $env:UV_PUBLISH_TOKEN = 'pypi-AhEIc...ktllA'
  ```
* GitHub CLI  
  This project uses [GitHub CLI](https://cli.github.com/) ([docs](https://cli.github.com/manual/))
  in the release process.

  You'll need to install and authenticate `gh` in order to perform the release tasks.

  To install, download the file in the link above and follow instructions.

  Authenticate with this command:
  ```
  gh auth login
  ```

## Workflow
For a full list of build related tasks:
```bash
python -m admin.build --help
```

1. Set/bump the version
   ```bash
   python -m admin.build version
   ```
   This will modify the version in the required files but not commit the changes.
2. Create and merge a PR with the new version.  
   Call it, for example, _"Release 1.2.3"_.
3. Build and publish to Pypi.
   This command builds the package locally (in the `dist` folder) and publish (upload) to Pypi.
   ```bash
   python -m admin.build publish
   ```
   To only build without uploading to Pypi, use the `--no-upload` option.
4. Create GitHub release and tag.
   ```bash
   python -m admin.build release
   ```
   This will:
     * Create a tag in GitHub with the version, ex `1.2.3`.
     * Create a release in GitHub with the version (named `v{version}`, ex `v1.2.3`).
