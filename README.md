# MapEditor User Management

For adding new users to the ESDL MapEditor or updating settings for existing users.

## Usage

1. Create venv with required dependencies by

   ```
   ./setup.sh
   ```

   or for windows create and activate venv (Python 3.12) followed by:

   ```
   pip install setuptools
   pip install -r ./requirements.txt
   ```

2. The parameters can be supplied via arguments or as environment variables, or a combination of
   both.  
   Via environment variables copy `.env.template` to `.env`.  
   Or via args see help:
   ```bash
   python -m mapeditor_user_management.main --help
   python -m mapeditor_user_management.main add-users --help
   python -m mapeditor_user_management.main edit-users-settings --help
   ```

3. Run (optionally with arguments) `main.py` or `run.sh` with the repo root as working directory (PyCharm mark the
   `src` folder as `Sources Root`).

### Not committed users/config

The folder `settings_not_committed` can be used to store confidential user list/settings.

## Description

Below a description of the two modes: `add-users` and `edit-users-config`. See `.env.template` for more info on the
config parameters.

### add-users

Add a specified list of users: create keycloak users, add optional keycloak roles and groups and set mapeditor settings
in mongodb.

### edit-users-config

Edit settings (keycloak and/or mapeditor) for a list of users, or all users.
There are three ways (EDIT_MODE) in which the config of the users can be edited:

1. `update`  
   Keycloak groups and roles will be added.
   For mapeditor settings the data in the json will be added, if not already present, to the current config of each
   user.   
   Caveat for lists: the whole list will be replaced (is it not possible to distinguish between adding a new item or
   updating an existing one).
2. `overwrite`  
   Keycloak groups and roles will be added.
   The mapeditor config for all users will be overwritten by the supplied json
3. `delete`  
   Keycloak groups and roles will be deleted.
   For mapeditor settings: the json items whose value is not a dictionary will be deleted (only the deepest item will be
   deleted).  
   To delete a higher level item change the value of the item to a string.
   Caveat for lists: it is not possible to remove specific list items.

## Connect to remote database

Use ssh tunnel, for instance:

```bash
ssh -L 27019:localhost:27017 root@omotes-mapeditor-test.hesi.energy
```