from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection

from mapeditor_user_management.user import User

USER_ROLE_NAME = 'Editor'
KEYCLOAK_REALM = 'esdl-mapeditor'
ADMIN_REALM = "master"


class KeycloakAdminInterface:
    connection: KeycloakOpenIDConnection
    admin: KeycloakAdmin

    def __init__(self, server_url: str, admin_username: str, admin_password: str, group_path: str):
        self.connection = KeycloakOpenIDConnection(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=KEYCLOAK_REALM,
            user_realm_name=ADMIN_REALM)

        self.admin = KeycloakAdmin(connection=self.connection)
        self.group_path = group_path
        if self.group_path != "":
            self.group_id = self.admin.get_group_by_path(group_path)['id']

    def add_user_to_keycloak(self, user: User) -> None:
        """Ensures the user is added to keycloak.

        This function may also be called on a user which already exists. Then it will ensure that
        the user is assigned the correct (client) role and added to the necessary group.

        :param user: User to add
        """
        client_id = self.admin.get_client_id("essim-dashboard")
        role = self.admin.get_client_role(client_id=client_id, role_name=USER_ROLE_NAME)

        print(f'Adding/Updating user {user} to/in keycloak')
        self.admin.create_user({
            "email": user.email,
            "username": user.username,
            "enabled": True,
            'emailVerified': False,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "requiredActions": ['VERIFY_EMAIL', 'UPDATE_PASSWORD']
        }, exist_ok=True)
        user_id = self.admin.get_user_id(user.username)

        print(f'  Assigning user {user} to role {USER_ROLE_NAME}')
        self.admin.assign_client_role(client_id=client_id, user_id=user_id, roles=[role])

        if self.group_path != "":
            print(f'  Add user {user} to group {self.group_id}')
            self.admin.group_user_add(user_id, self.group_id)
