# Publishing package
## Requirements
* `flit`  
  For the publishing process, [flit](https://flit.pypa.io/en/stable/) is used to make it simpler.  
  Included in `requirements-dev.txt`.
* Pypi account and API token  
  To publish to Pypi, an account is needed and an API token generated.  
  Go to [https://pypi.org](https://pypi.org/) and follow instructions.
* `.pypirc` file  
  Create the file `.pypirc` in the home folder with the token:
  ```
  [pypi]
    username = __token__
    password = pypi-AhEIc...ktllA
  ```
  Note that using username/password has been disabled in Pypi. Need to use token.
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
To further simplify, [invoke](https://www.pyinvoke.org/) tasks were added.  
For a full list of build related tasks:
```
inv --list build
```

1. Set/bump the version
   ```
   inv build.version
   ```
   This will modify the version in the required files but not commit the changes.
2. Create and merge a PR with the new version.  
   Call it, for example, _"Release 1.2.3"_.
3. Build and publish to Pypi.
   This command builds the package locally (in the `dist` folder) and publish (upload) to Pypi.
   ```
   inv build.publish
   ```
   To only build the package without uploading to Pypi, use the `--no-upload` option.
4. Create GitHub release and tag.
   ```
   inv build.release
   ```
   This will:
     * Create a tag in GitHub with the version, ex `1.2.3`.
     * Create a release in GitHub with the version (named `v{version}`, ex `v1.2.3`).
