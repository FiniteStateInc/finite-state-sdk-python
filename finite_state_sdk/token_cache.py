import finite_state_sdk
import os
import time


"""
A class for caching Finite State API tokens so that a new token is not required for every run of the script
Use this in place of finite_state_sdk.get_auth_token
Example Usage
---
token_cache = TokenCache(ORGANIZATION_CONTEXT)
token = token_cache.get_token(CLIENT_ID, CLIENT_SECRET)
"""


class TokenCache():
    def __init__(self, organization_context, client_id=None):
        self.token = None

        self.client_id = client_id
        self.organization_context = organization_context
        self.token_path = f'.tokencache/{self.organization_context}'
        if self.client_id:
            self.token_path = f'.tokencache/{self.organization_context}-{self.client_id}'
        else:
            self.token_file = f'.tokencache/{self.organization_context}/token.txt'
        self.token_file = f'{self.token_path}/token.txt'

        # create the token cache directory if it doesn't exist
        if not os.path.exists('.tokencache'):
            os.mkdir('.tokencache')

        # create the client directory if it doesn't exist
        if not os.path.exists(self.token_path):
            os.mkdir(self.token_path)

    def _get_token_from_api(self, client_id, client_secret):
        # get a new token
        self.token = finite_state_sdk.get_auth_token(client_id, client_secret)

        # write it to disk
        with open(self.token_file, 'w') as f:
            f.write(self.token)

    def get_token(self, client_id, client_secret):
        # try to read from disk
        if self.token is None:
            if os.path.exists(self.token_file):
                # check how old the file is, if it is more than 24 hours old, delete it
                if os.path.getmtime(self.token_file) < time.time() - 24 * 60 * 60:
                    print("Token is more than 24 hours old, deleting it...")
                    self.invalidate_token()

                    self._get_token_from_api(client_id, client_secret)
                    return self.token
                else:
                    print("Getting saved token from disk...")
                    with open(self.token_file, 'r') as f:
                        self.token = f.read()

                    return self.token
            else:
                print("Querying the API for a new token...")
                self._get_token_from_api(client_id, client_secret)
                return self.token

        else:
            return self.token

    def invalidate_token(self):
        self.token = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            self.token = None
