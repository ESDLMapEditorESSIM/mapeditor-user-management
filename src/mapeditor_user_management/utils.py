import argparse
import csv
import os
import sys
from typing import Dict, Any, TypeVar
from mapeditor_user_management.user import User

KeyType = TypeVar('KeyType')


# Code copy from pydantic:
#   - avoid importing big library
#   - deep_update is in v1, not part of v2 and v3, might be deprecated
# https://github.com/pydantic/pydantic/blob/fd2991fe6a73819b48c906e3c3274e8e47d0f761/pydantic/utils.py#L200
def deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[
    KeyType, Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v,
                                                                                            dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def delete_from_dict(dictionary: dict, to_delete_dict: dict):
    for k, v in to_delete_dict.items():
        if k in dictionary:
            if isinstance(v, dict):
                delete_from_dict(dictionary[k], v)
            else:
                del dictionary[k]


def setup_arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="MapEditor User Management",
        description="Add/update users and settings in keycloak and mongodb.",
    )

    parser.add_argument("-mh", "--mongo-host", default=os.environ.get("MONGO_HOST"))
    parser.add_argument("-mp", "--mongo-port", default=os.environ.get("MONGO_PORT"))

    subparsers = parser.add_subparsers(dest="mode")
    # subparsers.required = True

    parser_add = subparsers.add_parser("add-users")
    parser_add.add_argument(
        "-ksu", "--keycloak-server-url", default=os.environ.get("KEYCLOAK_SERVER_URL")
    )
    parser_add.add_argument(
        "-ku",
        "--keycloak-admin-username",
        default=os.environ.get("KEYCLOAK_ADMIN_USERNAME"),
    )
    parser_add.add_argument(
        "-kp",
        "--keycloak-admin-password",
        default=os.environ.get("KEYCLOAK_ADMIN_PASSWORD"),
    )
    parser_add.add_argument(
        "-kg",
        "--keycloak-group-path",
        default=os.environ.get("KEYCLOAK_GROUP_PATH"),
    )
    parser_add.add_argument(
        "-u", "--users-from-csv", default=os.environ.get("USERS_FROM_CSV")
    )
    parser_add.add_argument(
        "-mccn",
        "--model-contexts-config-name",
        default=os.environ.get("MAPEDITOR_MODEL_CONTEXTS_CONFIG_NAME"),
    )
    parser_add.add_argument(
        "-mccf",
        "--model-contexts-config-file",
        default=os.environ.get("MAPEDITOR_MODEL_CONTEXTS_DEFAULT_FILE"),
    )
    parser_add.add_argument(
        "-escn",
        "--esdl-services-config-name",
        default=os.environ.get("ESDL_SERVICES_CONFIG_NAME"),
    )
    parser_add.add_argument(
        "-escf",
        "--esdl-services-config-file",
        default=os.environ.get("ESDL_SERVICES_CONFIG_DEFAULT_FILE"),
    )
    parser_add.add_argument(
        "-mucn",
        "--mapeditor-user-config-name",
        default=os.environ.get("MAPEDITOR_USER_CONFIG_NAME"),
    )
    parser_add.add_argument(
        "-mucf",
        "--mapeditor-user-config-file",
        default=os.environ.get("MAPEDITOR_USER_CONFIG_DEFAULT_FILE"),
    )

    parser_update_users_settings = subparsers.add_parser("edit-users-settings")
    parser_update_users_settings.add_argument(
        "-em",
        "--edit-mode",
        choices=["update", "overwrite", "delete"],
        default=os.environ.get("EDIT_MODE"),
    )
    parser_update_users_settings.add_argument(
        "-snn", "--setting-name", default=os.environ.get("SETTING_NAME")
    )
    parser_update_users_settings.add_argument(
        "-svf", "--setting-value-file", default=os.environ.get("SETTING_VALUE_FILE")
    )

    args = parser.parse_args()
    if not args.mode and os.environ.get("MODE"):
        # reparse the arguments:
        args = parser.parse_args([os.environ.get("MODE")] + sys.argv[1:])
    else:
        raise IOError("A 'MODE' must be supplied as the first argument or as ENV VAR.")
    return args


def parse_users(path: str) -> list[User]:
    print(f"Reading users from {path}")
    users = []
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            users.append(
                User(
                    email=row["email"].lower(),
                    username=row["username"].lower(),
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                )
            )
    return users
