# Passwor dWallet

A password wallet application written in Python 3.6.

**IMPORTANT: this is still under development -- do NOT trust it with all your
passwords, and DO backup them.**

## Install prerequisites

1. Install Python 3:
   ```bash
   sudo apt install -y python3 python3-pip
   sudo pip3 install virtualenv                 # Optional
   ```

2. Install necessary packages
   ```bash
   virtualenv -p python3 .venv
   source .venv/bin/activate                    # Optional
   pip install -r requirements.txt
   ```

## Usage

- `add` to add new password record, including `name`, `pwd`, `site` and `desc`:
  ```bash
  python3 shell.py add
  ```

  - `name`: username - required with default to be `Guest` if not provided;
  - `pwd`: password - required without default value;
  - `site`: site of password - required with default to be `Default` if not
    provided;
  - `desc`: description - optional.

- `del` to remove a password record by `name` and `site`:
  ```bash
  python3 shell.py del
  ```

- `update` to change password/descrption of a record by `name` and `site`:
  ```bash
  python3 shell.py update
  ```

- `find` to list matched records
  ```bash
  python3 shell.py find [name=R1 [site=R2 [desc-R3]] [True|False]]
  ```

  - trailing args are optional, and will find all if not provided;
  - `R1`, `R2`, `R3`: regular expressions for the three fields;
  - final argument (`True` or `False`) specifies whether to show encrypted or
    decrypted password.

## Licence

MIT
