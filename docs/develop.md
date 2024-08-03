# Development
## Requirements
Start by installing all required packages:
```
pip install -r requirements-dev.txt
```

## Tasks
This project uses **pyinvoke** ([main page](https://www.pyinvoke.org/) | [docs](https://docs.pyinvoke.org/en/stable/) |
[GitHub](https://github.com/pyinvoke/invoke)) to facilitate executing miscellaneous tasks that help
with development (similar to `make`, but in Python).

### Using invoke
After the installing the dev requirements (which include `invoke`), try the commands below.

* List all available tasks  
  ```
  inv --list
  ```

  Tasks are grouped (those that have a `.`). To see all the _lint_ tasks:
  ```
  inv --list lint
  ```
* Help with a certain task  
  ```
  inv --help pip.package
  ```
* Use `--dry` to see what the task does without executing it.

### Debugging tasks
To debug `tasks.py` (the file used by `invoke`), either add a `breakpoint()` statement or, if using
an IDE (in this example PyCharm), use the configuration below to allow setting breakpoints in the
code and debug `tasks.py` as any other Python file.

![PyCharm tasks run config](images/pycharm_tasks_run_config.png)

Replace script path to have the project's virtual environment.