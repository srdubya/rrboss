# rrboss
Manage the Creation of Round Robin Invitations on MacOS.

## MacOS Shortcuts
For this application to work a MacOS Shortcut named __SendBatchSMS__ must exist.  The definition of __SendBatchSMS__ is as follows:

1. Receive `text` from `Share Sheet`  
If there's no input:  `Stop and Respond`
2. Get dictionary from `Shortcut Input`
3. Get `Value` for `message` in `Dictionary`
4. Get `Value` for `numbers` in `Dictionary`
5. Send `message` to `numbers`

## Modules Used

|Module|Use|
|---|---|
|py2app | Generates a MacOS runnable.  Optional |
|pydantic | Stores/retrieves `json` content. |
|pyobjc | Provides access to MacOS Contacts. |
|PySide6 | Provides UI capabilities. |

## Building
RRBoss was written using 
[PyCharm](https://www.jetbrains.com/pycharm/download/#section=windows) and  [Qt-Designer](https://www.qt.io/downloadhttps://www.qt.io/download). The icon was developed using [InkScape](https://inkscape.org/releases/).

### Icons
Run `makeall.sh` in the `icon` directory.

### RRBoss.app
Run `buildapp.sh`.

## Running
Once all of the necessary modules have been installed, running the program should be as simple as:
> `python main.py`

Wrapping that into a script something like this may be helpful:
```
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$HOME/src/github/rrboss"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found" >&2
    exit 2
fi

cd "$SCRIPT_DIR"
source .venv/bin/activate
exec python3 "$PYTHON_SCRIPT" "$@"
deactivate
cd -
```

When run `RRBoss` will create a settings file called `.rrboss.json`.