import json
from dotenv import load_dotenv

from mapeditor_user_management.constants import Mode, KeycloakEditMode, EditMode, MapEditorSettingType
from mapeditor_user_management.keycloak_admin_interface import KeycloakAdminInterface
from mapeditor_user_management.mongo_interface import MongoInterface
from mapeditor_user_management.utils import (
    deep_update,
    delete_from_dict,
    setup_arg_parser,
    parse_users,
)


def main():
    args = setup_arg_parser()

    if args.mode in [Mode.ADD_USERS, Mode.EDIT_USERS_SETTINGS]:
        keycloak_admin = KeycloakAdminInterface(
            args.keycloak_server_url,
            args.keycloak_admin_username,
            args.keycloak_admin_password,
        )

    mongo_interface = MongoInterface(args.mongo_host, args.mongo_port)
    existing_users = mongo_interface.get_all_users()

    if args.mode == Mode.ADD_USERS:
        users = parse_users(args.users_from_csv)

        existing_users_email = [user["name"] for user in existing_users]

        for user in users:
            if user.email in existing_users_email:
                print(
                    f"Email '{user.email}' already present in database: skipping user '{user}'"
                )
            else:
                print(f"Adding user: {user.email}")
                keycloak_admin.add_user_to_keycloak(user)

                default_config_dict = {
                    args.model_contexts_config_name: args.model_contexts_config_file,
                    args.esdl_services_config_name: args.esdl_services_config_file,
                    args.mapeditor_user_config_name: args.mapeditor_user_config_file,
                }
                for settings_name, settings_file in default_config_dict.items():
                    with open(settings_file, "r") as open_file:
                        settings_value_string = open_file.read()
                    mongo_interface.set_user_setting(
                        user.email, settings_name, json.loads(settings_value_string)
                    )

        keycloak_admin.edit_users_keycloak(
            KeycloakEditMode.ADD,
            [user.username for user in users],
            json.loads(args.keycloak_roles),
            json.loads(args.keycloak_group_paths),
        )
        print(
            f"Added users with config: '{args.model_contexts_config_file}', '{args.esdl_services_config_file}'"
            f", '{args.mapeditor_user_config_file}'"
        )
    elif args.mode == Mode.EDIT_USERS_SETTINGS:
        edit_usernames = None
        mongo_usernames = [user["name"] for user in existing_users]
        if args.edit_users_from_csv:
            edit_usernames = [
                user.username for user in parse_users(args.edit_users_from_csv)
            ]
            mongo_usernames = [
                user for user in edit_usernames if user in existing_users
            ]

        # edit keycloak user settings
        if args.edit_mode in [EditMode.UPDATE, EditMode.OVERWRITE]:
            keycloak_edit_mode = KeycloakEditMode.ADD
        else:
            keycloak_edit_mode = KeycloakEditMode.DELETE
        keycloak_admin.edit_users_keycloak(
            keycloak_edit_mode,
            edit_usernames,
            json.loads(args.edit_keycloak_roles),
            json.loads(args.edit_keycloak_group_paths),
        )

        if args.setting_name:
            # edit mapeditor mongodb user settings
            with open(args.setting_value_file, "r") as open_file:
                value_update_string = open_file.read()
            new_value = json.loads(value_update_string)
            for username in mongo_usernames:
                print(
                    f"Setting user '{username}' config '{args.setting_name}' to file '{args.setting_value_file}'"
                )
                if args.edit_mode == EditMode.UPDATE:
                    setting_value = mongo_interface.get_setting(
                        MapEditorSettingType.USER, username, args.setting_name
                    )
                    if isinstance(setting_value, list):
                        value_updated = False
                        for i_value_item, value_item in enumerate(setting_value):
                            for update_item in new_value:
                                if "id" not in update_item:
                                    raise IOError(
                                        f"List entry must contain 'id', missing for: {update_item}"
                                    )
                                if value_item["id"] == update_item["id"]:
                                    setting_value[i_value_item] = deep_update(
                                        value_item, update_item
                                    )
                                    value_updated = True
                        if not value_updated:
                            setting_value.append(new_value)
                    elif isinstance(setting_value, dict):
                        setting_value = deep_update(setting_value, new_value)
                    else:
                        setting_value = new_value
                elif args.edit_mode == EditMode.OVERWRITE:
                    setting_value = new_value
                elif args.edit_mode == EditMode.DELETE:
                    delete_from_dict(setting_value, new_value)

                mongo_interface.set_user_setting(
                    username, args.setting_name, setting_value
                )
        print(f"Edited users settings with config: '{args.setting_value_file}'")

    elif args.mode == Mode.UPDATE_MONGO_USER_CONFIG:
        mongo_usernames = [user["name"] for user in existing_users]
        if args.edit_users_from_csv:
            edit_usernames = [
                user.email for user in parse_users(args.edit_users_from_csv)
            ]
            mongo_usernames = [
                user for user in edit_usernames if user in mongo_usernames
            ]

        if args.setting_name:
            # edit mapeditor mongodb user settings
            with open(args.setting_value_file, "r") as open_file:
                value_update_string = open_file.read()
            new_value = json.loads(value_update_string)
            for username in mongo_usernames:
                print(
                    f"Setting user '{username}' config '{args.setting_name}' to file '{args.setting_value_file}'"
                )
                if args.edit_mode == EditMode.UPDATE:
                    setting_value = mongo_interface.get_setting(
                        MapEditorSettingType.USER, username, args.setting_name
                    )
                    if isinstance(setting_value, list):
                        value_updated = False
                        for i_value_item, value_item in enumerate(setting_value):
                            for update_item in new_value:
                                if "id" not in update_item:
                                    raise IOError(
                                        f"List entry must contain 'id', missing for: {update_item}"
                                    )
                                if value_item["id"] == update_item["id"]:
                                    setting_value[i_value_item] = deep_update(
                                        value_item, update_item
                                    )
                                    value_updated = True
                        if not value_updated:
                            setting_value.append(new_value)
                    elif isinstance(setting_value, dict):
                        setting_value = deep_update(setting_value, new_value)
                    else:
                        setting_value = new_value
                elif args.edit_mode == EditMode.OVERWRITE:
                    setting_value = new_value
                elif args.edit_mode == EditMode.DELETE:
                    delete_from_dict(setting_value, new_value)

                mongo_interface.set_user_setting(
                    username, args.setting_name, setting_value
                )
        print(f"Edited users settings with config: '{args.setting_value_file}'")



    print("User management finished")


if __name__ == "__main__":
    load_dotenv()
    main()
