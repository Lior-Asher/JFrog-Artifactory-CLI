#! /usr/bin/python3
import sys
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
        # self.menu()

    def _set_group_name(self, group: str) -> str:
        self.group = group

    def _get_token_for_group(self, group: str) -> str:
        # curl -u $user:$password -XPOST "https://artitestserver.jfrog.io/artifactory/api/security/token" -d "username=$user" -d "scope=member-of-groups:readers" > .tok3
        
        endpoint = 'security/token'
        url = ''.join([self.url, endpoint])
        data = {'username':self.user, 'password':self.password, 'scope=member-of-groups':group}
        r = requests.post(url, auth=(self.user, self.password), data=data)
        return r.json()['access_token']

    def system_ping(self) -> None:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping

        pass

    def display_menu(self) -> None:
        print("Default group is: administrators")
        menu_options = {
            1: "Change user's group name",
            2: "Ping",
            3: "Option 3",
            4: "Exit",
            5: "Print token"
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
                # Change user's group name
                group = input("Enter user's group name:")
                self._set_group_name(group)
                self.token = self._get_token_for_group(self.group) # set token for new group
                
            elif option == 2:
                # Ping
                break
            elif option == 3:
                # Option 3
                break
            elif option == 4:
                # Exit 
                break
            elif option == 5:
                # Print token
                print(self.token) 
                # break
            else:
                print("Invalid option, try again")

            # print(selection)

if __name__ == '__main__':
    cli = CLI()
    # token = cli.get_token_for_group("readers")
    # print(token)
    cli.menu()
    