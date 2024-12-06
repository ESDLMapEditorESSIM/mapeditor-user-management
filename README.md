# MapEditor User Management

For adding new users to the ESDL MapEditor or updating settings for existing users.

## Usage

1. Create venv with required dependencies by

   ```
   ./setup.sh
   ```

   or for windows create and activate venv (Python 3.12) followed by:

   ```
   pip install piptools
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

3. Run by (optionally with arguments):
    ```bash
    ./run.sh
    ```
   or `main.py` directly.

### Not committed users/config

The folder `settings_not_committed` can be used to store confidential user list/settings.

## Description

### add-users

The tool will add the necessary account to keycloak and set the necessary settings to mongodb for a
specified list of
users.

### edit-users-config

A settings name (SETTING_NAME) and settings value json (SETTINGS_VALUE_FILE) are needed. There are
three ways
(EDIT_MODE) in which the config of the users can be edited:

1. 'update'  
   The data in the json will be added, if not already present, to the current config of each
   user.   
   Caveat for lists: the whole list will be replaced (is it not possible to distinguish between
   adding a new item or
   updating an existing one).
2. 'overwrite'  
   The config for all users will be overwritten by the json
3. 'delete'
   The json items whose value is not a dictionary will be deleted (only the deepest item will be
   deleted).  
   To delete a higher level item change the value of the item to a string.
   Caveat for lists: it is not possible to remove specific list items.

## Connect to remote database

Use ssh tunnel, for instance:

```bash
ssh -L 27019:localhost:27017 root@omotes-mapeditor-test.hesi.energy
```