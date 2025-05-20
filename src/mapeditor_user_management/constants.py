from enum import Enum
from dataclasses import dataclass


@dataclass
class User:
    email: str
    username: str
    first_name: str
    last_name: str


class Mode(str, Enum):
    ADD_USERS = "add-users"
    EDIT_USERS_SETTINGS = "edit-users-settings"


class EditMode(str, Enum):
    UPDATE = "update"
    OVERWRITE = "overwrite"
    DELETE = "delete"


class KeycloakEditMode(str, Enum):
    ADD = "add"
    DELETE = "delete"


class MapEditorSettingType(Enum):
    USER = "user"
    PROJECT = "project"
    SYSTEM = "system"
