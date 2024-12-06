from enum import Enum

from pymongo import MongoClient
from pymongo.database import Database, Collection

SYSTEM_NAME_IDENTIFIER = (
    "mapeditor"  # only one identifier of system settings for mapeditor
)
MAPEDITOR_DATABASE = "esdl_mapeditor_settings"


# different types of settings
class SettingType(Enum):
    USER = "user"
    PROJECT = "project"
    SYSTEM = "system"


class MongoInterface:
    host: str
    port: str
    client: MongoClient
    db: Database
    settings: Collection

    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        database_uri = f"mongodb://{self.host}:{self.port}"

        print(f"Setting up UserSettings with mongoDB at {database_uri}")
        self.client = MongoClient(database_uri)
        self.db: Database = self.client[MAPEDITOR_DATABASE]
        self.settings: Collection = self.db.settings
        self.external_model_runs = self.db.external_model_runs

    def get_setting(self, setting_type: SettingType, identifier: str, setting_name: str):
        if self.settings is None:
            return None
        mapeditor_settings_obj = self.settings.find_one(
            {"type": setting_type.value, "name": identifier},
            {"type": 1, "name": 1, setting_name: 1},
        )
        if mapeditor_settings_obj is None:
            raise KeyError(
                "No such setting '{}' for {} {}".format(
                    setting_name, setting_type.value, identifier
                )
            )
        if setting_name in mapeditor_settings_obj:
            return mapeditor_settings_obj[setting_name]
        else:
            raise KeyError(
                "No such setting '{}' for {} {}".format(
                    setting_name, setting_type.value, identifier
                )
            )

    def get_all_users(self):
        if self.settings is None:
            return None

        return self.settings.find({"type": SettingType.USER.value})

    def set_user_setting(self, user_email: str, setting_name: str, value: dict):
        if self.settings is None:
            return None
        mapeditor_settings_obj = self.settings.find_one(
            {"type": SettingType.USER.value, "name": user_email}, {setting_name: 1}
        )
        if mapeditor_settings_obj is None:
            # unknown identifier, create first
            doc = {
                "type": SettingType.USER.value,
                "name": user_email,
                setting_name: value,
            }
            self.settings.insert_one(doc)
        else:
            return self.settings.update_one(
                {"_id": mapeditor_settings_obj["_id"]},
                {"$set": {setting_name: value}},
                upsert=False,
            )

    def get_external_model_runs(self):
        if self.external_model_runs is None:
            return None
        return self.external_model_runs.find({})

    def set_external_model_run(self, external_model_run):
        if self.external_model_runs is None:
            return None
        return self.external_model_runs.replace_one(
            {"run_id": external_model_run["run_id"]},
            external_model_run,
            upsert=False
        )
