#! /usr/bin/python3

import json
import requests
import argparse
from secrets import USER, PASSWORD, SERVER

# -------------------------------------------
# Using my JFrog url,
# not Artifactory server hostname and port
# https://<Server Name>.jfrog.io/artifactory/
# Example: 
# 1) curl -H "X-JFrog-Art-Api:ABcdEF" -X PUT "https://<Server Name>.jfrog.io/artifactory//my/new/artifact/        directory/# file.txt" -T Desktop/myNewFile.txt
#  2) curl -H "Authorization: Bearer <Token>" -X PUT "https://<Server Name>.jfrog.io/artifactory//my/new/artifact/directory/file.txt" -T Desktop/myNewFile.txt
#
# -------------------------------------------

class CLI:
    def __init__(self) -> None:        
        self.username = USER # TODO: replace 'USER' with '' after testing
        self.password = PASSWORD # TODO: replace 'PASSWORD' with '' after testing
        self.server = SERVER
        self.group = 'administrators'
        self.url = f'https://{self.server}.jfrog.io/artifactory/api/'
        # self._user_credentials() # TODO: activate this method after testing
        self.token = self._get_token_for_group(self.group)
        self.session = requests.Session()
        self._set_session(self.token)
        # self.menu()

    def _user_credentials(self):
        # Get user credentials from the command line on script run
        parser = argparse.ArgumentParser(description='CLI for the JFrog REST API')
        parser.add_argument('-u', '--username', help="personal username to login to JFrog's REST API", required=True)
        parser.add_argument('-p', '--password', help="personal password to login to JFrog's REST API", required=True)
        args = parser.parse_args()
        # args, unknown = parser.parse_known_args()
        self.username = args.username
        self.password = args.password

    #----- Utility methods -----
    def _set_session(self, token: str) -> None:
        self.headers = {'Authorization': f'Bearer {token}'}
        self.session.headers.update(self.headers)

    def _set_url(self, endpoint: str) -> str:
        url = ''.join([self.url, endpoint])
        return url

    def _get_token_for_group(self, group: str) -> str:
        # curl -u $user:$password -XPOST "https://artitestserver.jfrog.io/artifactory/api/security/token" -d "username=$user" -d "scope=member-of-groups:readers" > .tok3
        
        endpoint = 'security/token'
        # url = ''.join([self.url, endpoint])
        url = self._set_url(endpoint)
        data = {'username':self.username, 'password':self.password, 'scope=member-of-groups':group}
        r = requests.post(url, auth=(self.username, self.password), data=data)
        # r = self.session.post(url, auth=(self.username, self.password), data=self.data)
        return r.json()['access_token']

    #----- Menu options implementation -----
    # 1
    def _system_ping(self) -> requests.Response:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/ping'
        url = self._set_url(endpoint)        
        r = self.session.get(url, headers=self.session.headers)
        return r

    # 2
    def _system_version(self) -> str:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/version'
        url = self._set_url(endpoint)    
        r = self.session.get(url, headers=self.session.headers)
        return r.json()['version']

    # 3
    def _create_user(self) -> requests.status_codes:
        # Notes: Requires Artifactory Pro
        # Usage: PUT /api/security/users/{userName}
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        endpoint = f'security/users/{username}'
        url = self._set_url(endpoint)
        # email and password are mandatory, name is optional
        json = {'name': f'{username}',
                'email' : f'{email}',
                'password': f'{password}'
                }

        r = self.session.put(url, headers=self.session.headers, json=json)
        return r.status_code

    # 4 
    def _delete_user(self) -> str:
        # Notes: Requires Artifactory Pro
        # Usage: DELETE /api/security/users/{userName}
        username = input("Enter username to delete: ")
        endpoint = f'security/users/{username}'
        url = self._set_url(endpoint)
        msg = self.session.delete(url, headers=self.session.headers)
        return msg

    # 5
    def _get_storage_info(self) -> json:
        # Returns storage summary information regarding binaries, file store and repositories.
        # Usage: GET /api/storageinfo
        endpoint = f'/storageinfo'
        url = self._set_url(endpoint)
        r = self.session.get(url, headers=self.session.headers)
        return r.json()

    # 6
    def _create_repository(self):
        # Creates a new repository in Artifactory with the provided configuration. Supported by local, remote, virtual and federated repositories. 
        # Usage: PUT /api/repositories/{repoKey}
        endpoint = f'/repositories/{repoKey}'
        url = self._set_url(endpoint)
        r = self.session.put(url, headers=self.session.headers)
        pass

    # 9
    def _change_group(self, group: str) -> str:
        self.group = group

    def _display_menu(self) -> None:
        menu_options = {
            1: "Ping",
            2: "Artifactory Version",
            3: "Create User",
            4: "Delete User",
            5: "Get Storage Info",
            6: "Create Repository",
            7: "Update Repository",
            8: "List Repositories",
            9: f"Change Group (current group: '{self.group}')",
            10: "Create Group",
            11: "Exit",
            12: "Print Token"
            }

        for option in menu_options.keys():
            if option < 10:     
                print(option, " --", menu_options[option])
            else:
                print(option, "--", menu_options[option])

    def menu(self) -> None:
        while True:
            print()
            self._display_menu()

            option = ''
            try:
                option = int(input("Enter your choice: "))
            except:
                print("Wrong input. Please enter a number ...\n")
    
            if option == 1:
                # Ping
                r = self._system_ping()
                print(f"ping {(self.url).split('artifactory', 1)[0]} - Status: {r.text}")
            elif option == 2:
                # Artifactory version
                version = self._system_version()
                print(f"Artifactory version {version}")
            elif option == 3:
                # Create User
                status = self._create_user()
                if status == 200:
                    print("User created successfully")
                else:
                    print("User was not created, try again")
            elif option == 4:
                # Delete User
                msg = self._delete_user()
                print(msg)
            elif option == 5:
                # Get Storage Info
                info = self._get_storage_info()
                print(info)
            elif option == 6:
                # Create Repository
                break
            elif option == 7:
                # Update Repository
                break
            elif option == 8:
                # List Repositories
                break
            elif option == 9:
                # Change user's group name
                group = input("Enter user's group name:")
                self._change_group(group)
                self.token = self._get_token_for_group(self.group) # set token for new group
            elif option == 10:
                # Create Group
                break
            elif option == 11:
                # Exit 
                break
            elif option == 12:
                # Print token
                print(self.token) 
                # break
            else:
                print("Invalid option, try again")

            # print(selection)

if __name__ == '__main__':
    # token = cli._get_token_for_group("readers")
    # print(token)
    cli = CLI()
    cli.menu()
    

    