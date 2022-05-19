#! /usr/bin/python3

import sys
import json
from tokenize import group
import requests
import argparse
import getpass
import re
# import enum
from secrets import SERVER, USER, PASSWORD

'''
 https://www.jfrog.com/confluence/display/JFROG/REST+API
 https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API
 
 Using my JFrog url,
 not Artifactory server hostname and port
 https://<Server Name>.jfrog.io/artifactory/
 Example: 
 1) curl -H "X-JFrog-Art-Api:ABcdEF" -X PUT "https://<Server Name>.jfrog.io/artifactory//my/new/artifact/        directory/# file.txt" -T Desktop/myNewFile.txt
 2) curl -H "Authorization: Bearer <Token>" -X PUT "https://<Server Name>.jfrog.io/artifactory//my/new/artifact/directory/file.txt" -T Desktop/myNewFile.txt
'''
# class Op(enum.Enum):
#     PING = "Ping"
#     ARTIFACTORY_VERSION = "Artifactory Version"
#     CREATE_USER = "Create User"
#     DELETE_USER = "Delete User"
#     GET_STORAGE_INFO = "Get Storage Info"
#     CREATE_REPOSITORY = "Create Repository"
#     UPDATE_REPOSITORY = "Update Repository"
#     LIST_REPOSITORIES = "List Repositories"
#     CHANGE_GROUP = "Change Group"
#     CREATE_GROUP = "Create Group"
#     EXIT = "Exit"
#     PRINT_TOKEN = "Print Token"

INDENTATION_THRESHOLD = 10

class CLI:
    def __init__(self) -> None:        
        self.username = USER#''
        self.password = PASSWORD#''
        self.server = SERVER
        self.group = 'administrators'
        self.url = f'https://{self.server}.jfrog.io/artifactory/api/'
        # self._user_credentials()
        self.token = self._get_token_for_group(self.group)
        self.session = requests.Session()
        self._set_session(self.token)        

    def _user_credentials(self) -> None:
        # Get user credentials from the command line on script run
        parser = argparse.ArgumentParser(description='CLI for the JFrog REST API')
        parser.add_argument('-u', '--username', help="personal username to login to JFrog's REST API", required=True)
        args = parser.parse_args()
        self.username = args.username
        self.password = getpass.getpass(prompt='Enter password: ')

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
        url = self._set_url(endpoint)
        data = {'username':self.username, 'password':self.password, 'scope=member-of-groups':group}
        try:
            r = requests.post(url, auth=(self.username, self.password), data=data)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.json()['access_token']

    #----- Menu options implementation -----
    # 1
    def _system_ping(self) -> requests.Response:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/ping'
        url = self._set_url(endpoint)        
        try:
            r = self.session.get(url, headers=self.session.headers)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r

    # 2
    def _system_version(self) -> str:
        # curl -H "Authorization: Bearer $Access_Token" https://artitestserver.jfrog.io/artifactory/api/system/ping
        endpoint = 'system/version'
        url = self._set_url(endpoint)    
        try:
            r = self.session.get(url, headers=self.session.headers)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.json()['version']

    def _is_valid_email(self, email) -> bool:
        regex = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        if re.fullmatch(regex, email):
            return True

        return False

    # 3
    def _create_user(self) -> requests.status_codes:
        '''
        Notes: Requires Artifactory Pro
        Usage: PUT /api/security/users/{userName}
        '''
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        if self._is_valid_email(email):
            raise ValueError("Invalid Email")
        if not all([username, email, password]):
            raise ValueError("Missing one or more values (username, email, password)")
            
        endpoint = f'security/users/{username}'
        url = self._set_url(endpoint)
        # email and password are mandatory, name is optional
        json = {'name': username,
                'email' : email,
                'password': password
                }

        try:
            r = self.session.put(url, headers=self.session.headers, json=json)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.status_code

    # 4 
    def _delete_user(self) -> str:
        '''
        Notes: Requires Artifactory Pro
        Usage: DELETE /api/security/users/{userName}
        '''
        username = input("Enter username to delete: ")
        if username is None or username == "":
            raise ValueError("Missing username")
        endpoint = f'security/users/{username}'
        url = self._set_url(endpoint)
        try:
            r = self.session.delete(url, headers=self.session.headers)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r

    # 5
    def _get_storage_info(self) -> json:
        '''
        Returns storage summary information regarding binaries, file store and repositories.
        Usage: GET /api/storageinfo
        '''
        endpoint = f'storageinfo'
        url = self._set_url(endpoint)
        try:
            r = self.session.get(url, headers=self.session.headers)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.json()

    # 6
    def _create_repository(self) -> requests.status_codes:
        '''
        Notes: Only for remote repositories. Requires Artifactory Pro
        Creates a new repository in Artifactory with the provided configuration. Supported by local, remote, virtual and federated repositories. 
        Usage: PUT /api/repositories/{repoKey}
        '''
        repokey = input("Enter repository name: ")
        if repokey == '' or repokey is None:
            raise ValueError("repository name cannot be empty")

        json = {
            'rclass' : 'remote',
            'url' : f'{self.url}',
            'externalDependenciesEnabled': False # False (default, Applies to Docker repositories only)
        }
        endpoint = f'repositories/{repokey}'
        url = self._set_url(endpoint)
        try:
            r = self.session.put(url, headers=self.session.headers, json=json)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.status_code

    # 7
    # TODO:
    def _update_repo(self):
        pass

    # 8
    def _list_repositories(self) -> json:
        '''
        Returns a list of minimal repository details for all repositories of the specified type.
        Usage: GET /api/repositories[?type=repositoryType (local|remote|virtual|federated|distribution)]|
        '''
        endpoint = 'repositories'
        url = self._set_url(endpoint)
        try:
            r = self.session.get(url, headers=self.session.headers)
        except Exception as e:
            print(f'Error in {r}\n{e}')

        return r.json()

    # 9
    def _change_group(self) -> None:
        print(f"(current group: '{self.group}')")
        group = input("Enter group name")
        self.group = group

    # 10
    # TODO:
    def _create_group(self):
        pass

    # 11
    def _exit(self) -> None:
        sys.exit(0)
        # raise SystemExit(0)

    # 12
    def _print_token(self) -> None:
        print(self.token)

    def _get_menu_options(self) -> dict:
        menu_options = {
            1: ("Ping", self._system_ping),
            2: ("Artifactory Version", self._system_version),
            3: ("Create User", self._create_user),
            4: ("Delete User", self._delete_user),
            5: ("Get Storage Info", self._get_storage_info),
            6: ("Create Repository", self._create_repository),
            7: ("Update Repository", self._update_repo),
            8: ("List Repositories", self._list_repositories),
            9: (f"Change Group (current group: '{self.group}')", self._change_group),
            10: ("Create Group", self._create_group),
            11: ("Exit", self._exit),
            12: ("Print Token", self._print_token)
            }

        return menu_options

    def _display_menu(self, menu_options) -> None:        
        for op_number, op_data in menu_options.items():
            indentation = " --" if op_number < INDENTATION_THRESHOLD else "--"
            print(op_number, indentation, op_data[0])

    # def menu(self) -> None:
    #     op_switch_case = {
    #         1: self._system_ping,
    #         2 : self._system_version,
    #         3 : self._create_user,
    #         4: self._delete_user,
    #         5: self._get_storage_info,
    #         6: self._create_repository,
    #         7: self._update_repo,
    #         8: self._list_repositories,
    #         9: self._change_group,
    #         10: self._create_group,
    #         11: self._exit,
    #         12: self._print_token
    #     }

    def main(self):
        menu_options = self._get_menu_options()
        while True:
            print() # for better menu readability
            self._display_menu(menu_options)

            # user_in = ''
            try:
                # /user_in = int(input("Enter your choice: "))
                # option = int(input("Enter your choice: "))
                op = int(input("Enter your choice: "))
                if op == 11:
                    break

                info, func = menu_options.get(op, (None, None))
                if func:
                    # print("OK 1") # DEBUG
                    # print(func) # DEBUG
                    func()
                    # print("OK 2") # DEBUG
                    # break
                else:
                    print(f"{op} is not defined")

            except Exception as e:
                print(e, "\n")
    
            # option = op_switch_case.get(user_in, None)()
            # print(f'{option.value}')
            # break # DEBUG
            # if option == 1:
            #     # Ping
            #     r = self._system_ping()
            #     print(f"ping {(self.url).split('artifactory', 1)[0]} - Status: {r.text}")
            # elif option == 2:
            #     # Artifactory version
            #     version = self._system_version()
            #     print(f"Artifactory version {version}")
            # elif option == 3:
            #     # Create User
            #     status_code = self._create_user()
            #     if status_code == 200:
            #         print("User created successfully")
            #     else:
            #         print("User was not created, try again")
            # elif option == 4:
            #     # Delete User
            #     r = self._delete_user()
            #     print(r)
            # elif option == 5:
            #     # Get Storage Info
            #     info = self._get_storage_info()
            #     print(info)
            # elif option == 6:
            #     # Create Repository
            #     try:
            #         status_code = self._create_repository()
            #         if status_code == 200:
            #             print("Repository created successfully!")
            #         else:
            #             print(status_code)
            #     except ValueError as e:
            #         print(e.args)
            # elif option == 7:
            #     # Update Repository
            #     # TODO:
            #     print("Not implemented yet")
            #     break
            # elif option == 8:
            #     # List Repositories
            #     repos = self._list_repositories()
            #     print(repos)
            # elif option == 9:
            #     # Change user's group name
            #     group = input("Enter user's group name:")
            #     self._change_group(group)
            #     self.token = self._get_token_for_group(self.group) # set token for new group
            # elif option == 10:
            #     # Create Group
            #     # TODO:
            #     print("Not implemented yet")
            #     break
            # elif option == 11:
            #     # Exit 
            #     break
            # elif option == 12:
            #     # Print token
            #     print(self.token) 
            # else:
            #     print("Invalid option, try again")

if __name__ == '__main__':   
    cli = CLI()
    cli.main()
    

    