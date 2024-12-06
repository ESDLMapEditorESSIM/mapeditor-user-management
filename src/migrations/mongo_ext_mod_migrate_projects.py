from dotenv import load_dotenv

from mapeditor_user_management.main import setup_arg_parser
from mapeditor_user_management.mongo_interface import MongoInterface

def main():
    args = setup_arg_parser()
    mongo_interface = MongoInterface(args.mongo_host, args.mongo_port)

    for ext_mod in mongo_interface.get_external_model_runs():
        ext_mod.pop("projects", None)
        ext_mod["user_group_paths"] = []
        mongo_interface.set_external_model_run(ext_mod)


if __name__ == "__main__":
    load_dotenv()
    main()
