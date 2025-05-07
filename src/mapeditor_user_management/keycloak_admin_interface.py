from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection

from mapeditor_user_management.user import User

KEYCLOAK_REALM = "esdl-mapeditor"
ADMIN_REALM = "master"


class KeycloakAdminInterface:
    connection: KeycloakOpenIDConnection
    admin: KeycloakAdmin

    def __init__(self, server_url: str, admin_username: str, admin_password: str):
        self.connection = KeycloakOpenIDConnection(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=KEYCLOAK_REALM,
            user_realm_name=ADMIN_REALM,
        )

        self.admin = KeycloakAdmin(connection=self.connection)

    def add_user_to_keycloak(self, user: User) -> None:
        """Ensures the user is added to keycloak.

        This function may also be called on a user which already exists.

        :param user: User to add
        """
        print(f"Adding user {user} to keycloak")
        self.admin.create_user(
            {
                "email": user.email,
                "username": user.username,
                "enabled": True,
                "emailVerified": False,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "requiredActions": ["VERIFY_EMAIL", "UPDATE_PASSWORD"],
            },
            exist_ok=True,
        )

    def edit_users_keycloak(
        self,
        mode: str,
        usernames: list[str] = None,
        roles: dict[str, str] = None,
        group_paths: list[str] = None,
    ) -> None:
        """Edit roles and groups for keycloak users.

        :param mode: "add" or "delete"
        :param usernames: list of usernames to be edited, if empty all users will be edited
        :param roles: dictionary with 'client_name': 'role_name' key value pairs to be added to the user
                      (use 'realm' as client name to set realm role instead of client role)
        :param group_paths: list of group paths to be added to the user
        """
        if not usernames:
            usernames = [user["username"] for user in self.admin.get_users()]
        for username in usernames:
            user_id = self.admin.get_user_id(username)
            print(
                f"  Editing '{mode}' user '{username}' to roles '{roles}' and groups '{group_paths}'"
            )
            if roles:
                for client_name, role_name in roles.items():
                    if client_name.lower() == "realm":
                        role = self.admin.get_realm_role(role_name)
                        if mode == "add":
                            self.admin.assign_realm_roles(user_id=user_id, roles=[role])
                        elif mode == "delete":
                            self.admin.delete_realm_roles_of_user(
                                user_id=user_id, roles=[role]
                            )
                    else:
                        client_id = self.admin.get_client_id(client_name)
                        role = self.admin.get_client_role(
                            client_id=client_id, role_name=role_name
                        )

                        if mode == "add":
                            self.admin.assign_client_role(
                                client_id=client_id, user_id=user_id, roles=[role]
                            )
                        elif mode == "delete":
                            self.admin.delete_client_roles_of_user(
                                client_id=client_id, user_id=user_id, roles=[role]
                            )
            if group_paths:
                for group_path in group_paths:
                    group_id = self.admin.get_group_by_path(group_path)["id"]

                    if mode == "add":
                        self.admin.group_user_add(user_id, group_id)
                    elif mode == "delete":
                        self.admin.group_user_remove(user_id, group_id)