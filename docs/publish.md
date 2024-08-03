# Publishing package
For the publishing process, [flit](https://flit.pypa.io/en/stable/) is used to make it simpler.

To publish to Pypi, an account is needed and an API token generated.

Then create the file `.pypirc` in the home folder with the token:
```
[pypi]
  username = __token__
  password = pypi-AhEIc...ktllA
```
Note that using username/password in Pypi has been disabled. Need to use token.

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
   Call it, for example, _"Preparing for v1.2.3 release"_.
3. Build and publish
   ```
   inv build.publish
   ```
   This will:
     * Create a tag in GitHub with the version, ex `1.2.3`.
     * Create a release in GitHub with the version (named `v{version}`, ex `v1.2.3`).
     * Publish (upload) to Pypi.
