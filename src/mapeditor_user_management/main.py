import json
from dotenv import load_dotenv

from mapeditor_user_management.keycloak_admin_interface import KeycloakAdminInterface
from mapeditor_user_management.mongo_interface import MongoInterface, SettingType
from mapeditor_user_management.utils import deep_update, delete_from_dict, setup_arg_parser, \
    parse_users


def main():
    args = setup_arg_parser()

    mongo_interface = MongoInterface(args.mongo_host, args.mongo_port)
    existing_users = mongo_interface.get_all_users()

    if args.mode == "add-users":
        users = parse_users(args.users_from_csv)
        keycloak_admin = KeycloakAdminInterface(
            args.keycloak_server_url,
            args.keycloak_admin_username,
            args.keycloak_admin_password,
            args.keycloak_group_path,
        )

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
        print(
            f"Added users with config: '{args.model_contexts_config_file}', '{args.esdl_services_config_file}'"
            f", '{args.mapeditor_user_config_file}'"
        )
    elif args.mode == "edit-users-settings":
        with open(args.setting_value_file, "r") as open_file:
            value_update_string = open_file.read()
        new_value = json.loads(value_update_string)
        for user in existing_users:
            print(f"Editing user: {user['name']}")
            if args.edit_mode == "update":
                setting_value = mongo_interface.get_setting(
                    SettingType.USER, user["name"], args.setting_name
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
            elif args.edit_mode == "overwrite":
                setting_value = new_value
            elif args.edit_mode == "delete":
                delete_from_dict(setting_value, new_value)

            mongo_interface.set_user_setting(
                user["name"], args.setting_name, setting_value
            )
        print(f"Edited users settings with config: '{args.setting_value_file}'")

    print("User management finished")


if __name__ == "__main__":
    load_dotenv()
    main()
