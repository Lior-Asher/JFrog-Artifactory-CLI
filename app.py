#! /usr/bin/python3

import requests
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
        self.user = USER
        self.password = PASSWORD
        self.server = SERVER
        self.group = 'administrators'
        self.url = f'https://{self.server}.jfrog.io/artifactory/api/'
        self.token = self._get_token_for_group(self.group)
        self.session = requests.Session()
        self._set_session(self.token)
        # self.menu()

    def _set_session(self, token) -> None:
        self.headers = {'Authorization': f'Bearer {token}'}
        self.session.headers.update(self.headers)

    def _set_url(self, endpoint) -> str:
        url = ''.join([self.url, endpoint])
        return url

    def _change_group(self, group: str) -> str:
        self.group = group

    def _get_token_for_group(self, group: str) -> str:
        # curl -u $user:$password -XPOST "https://artitestserver.jfrog.io/artifactory/api/security/token" -d "username=$user" -d "scope=member-of-groups:readers" > .tok3
        
        endpoint = 'security/token'
        # url = ''.join([self.url, endpoint])
        url = self._set_url(endpoint)
        data = {'username':self.user, 'password':self.password, 'scope=member-of-groups':group}
        r = requests.post(url, auth=(self.user, self.password), data=data)
        # r = self.session.post(url, auth=(self.user, self.password), data=self.data)
        return r.json()['access_token']

    def system_ping(self) -> requests.Response:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/ping'
        url = self._set_url(endpoint)        
        r = self.session.get(url, headers=self.session.headers)
        return r

    def system_version(self) -> str:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/version'
        url = self._set_url(endpoint)    
        r = self.session.get(url, headers=self.session.headers)
        return r.json()['version']

    def display_menu(self) -> None:
        menu_options = {
            1: "Ping",
            2: "Artifactory version",
            3: "Create User",
            4: "Delete User",
            5: "Get Storage Info",
            6: "Create Repository",
            7: "Update Repository",
            8: "List Repositories",
            9: f"Change user's group (current group: '{self.group}')",
            10: "Exit",
            11: "Print token"
            }

        for option in menu_options.keys():
            print(option, "--", menu_options[option])

    def menu(self) -> None:
        while True:
            print()
            self.display_menu()

            option = ''
            try:
                option = int(input("Enter your choice: "))
            except:
                print("Wrong input. Please enter a number ...\n")
    
            if option == 1:
                # Ping
                r = self.system_ping()
                print(f"ping {(self.url).split('artifactory', 1)[0]} - {r.text}")
            elif option == 2:
                # Artifactory version
                version = self.system_version()
                print(f"Artifactory version {version}")
            elif option == 3:
                # Create User
                break
            elif option == 4:
                # Delete User
                break
            elif option == 5:
                # Get Storage Info
                break
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
                # Exit 
                break
            elif option == 11:
                # Print token
                print(self.token) 
                # break
            else:
                print("Invalid option, try again")

            # print(selection)

if __name__ == '__main__':
    cli = CLI()
    # token = cli._get_token_for_group("readers")
    # print(token)
    cli.menu()
    