import getpass
import json
import netrc
import os
import warnings

import keyring
from typing import Optional, Tuple, List


class Authenticator:
    """
    Credential manager for logging into an API service.

    Supports credentials stored in .netrc, keyring, and environment 
    variables.

    Parameters
    ----------
    service : str
        The name of the service to log in to.
    priority : list of str, optional
        Ordered list of credential stores to check. Options: 'netrc', 
        'keyring', 'env'. Default is ['netrc', 'keyring', 'env'].
    env_prefix : str, optional
        Prefix for environment variable names. Default is uppercase of 
        service name.

    Attributes
    ----------
    service : str
        The name of the service or machine used in backends.
    priority : list of str
        The order in which credential stores are checked.
    env_prefix : str
        Prefix used to look for environment variable credentials.
    """

    def __init__(
        self,
        service: str,
        priority: Optional[List[str]] = None,
        env_prefix: Optional[str] = None
    ):
        self.service = service
        self.priority = priority or ['netrc', 'keyring', 'env']
        self.env_prefix = env_prefix or service.replace(".", "_").upper()

    # ==== .netrc ====

    def get_netrc_credentials(self) -> Optional[Tuple[str, str]]:
        """Get credentials from ~/.netrc file."""
        try:
            auths = netrc.netrc()
            login, _, password = auths.authenticators(self.service)
            if login and password:
                return login, password
        except (FileNotFoundError, TypeError):
            return None
        return None
    
    def set_netrc_credentials(self, username: str, password: str):
        """Editing .netrc is not yet supported."""
        raise NotImplementedError(
            "Setting .netrc credentials is not currently supported.")


    # ==== Keyring ====

    def get_keyring_credentials(self) -> Optional[Tuple[str, str]]:
        """Get credentials stored in keyring as a JSON blob."""
        try:
            creds_json = keyring.get_password(self.service, "default")
            if creds_json:
                creds = json.loads(creds_json)
                return creds['username'], creds['password']
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def set_keyring_credentials(self, username: str, password: str):
        """Store username and password in keyring"""
        creds = json.dumps({'username': username, 'password': password})
        keyring.set_password(self.service, "default", creds)

    # ==== Environment Variables ====

    def get_env_credentials(self) -> Optional[Tuple[str, str]]:
        """Get credentials from environment variables."""
        user = os.getenv(f"{self.env_prefix}_USERNAME")
        password = os.getenv(f"{self.env_prefix}_PASSWORD")
        if user and password:
            return user, password
        return None

    def set_env_credentials(self, username: str, password: str):
        """
        Set credentials in the current environment. 
        
        Credentials do not persist between sessions. Useful for runtime 
        configuration and continuous integration.
        """
        os.environ[f"{self.env_prefix}_USERNAME"] = username
        os.environ[f"{self.env_prefix}_PASSWORD"] = password

    # ==== Login ====

    def get_credentials(
            self, 
            interactive: bool = True, 
            override: bool = False
        ) -> Tuple[str, str]:
        """
        Attempt to retrieve credentials using the specified priority.

        If credentials are found and override is True, prompt to 
        override them. If credentials are not found and interactive is 
        True, prompt to enter and store them.

        Parameters
        ----------
        interactive : bool, optional
            If True, allows prompting the user for credentials. 
            Default is True.
        override : bool, optional
            If True, and credentials are found, ask whether to override 
            them. Default is False.

        Returns
        -------
        username : str
            The authenticated username.
        password : str
            The associated password.

        Raises
        ------
        RuntimeError
            If credentials are not found and interactive is False.
        """
        for method in self.priority:
            getter = getattr(self, f"get_{method}_credentials", None)
            if getter:
                creds = getter()
                if creds:
                    username, password = creds
                    print(f"Credentials found using '{method}' backend.")

                    if interactive and override:
                        user_input = input(
                            "Do you want to override these credentials?"
                            " [y/N]: "
                            ).strip().lower()
                        if user_input == "y":
                            username, password = self._prompt_for_credentials()
                            self._store_credentials(username, password)
                    return username, password

        if not interactive:
            raise RuntimeError(
                f"No credentials found for {self.service} and interactive mode"
                " is off.")

        print(
            f"No stored credentials found for {self.service}. Please log in.")
        username, password = self._prompt_for_credentials()
        self._store_credentials(username, password)
        return username, password


    def _prompt_for_credentials(self) -> Tuple[str, str]:
        """Securely prompt the user for credentials."""
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        return username, password


    def _store_credentials(self, username: str, password: str):
        """
        Try to store credentials
        
        Use the first backend in the priority list
        that supports setting credentials. Log if unable to store.
        """
        for method in self.priority:
            setter = getattr(self, f"set_{method}_credentials", None)
            if setter:
                try:
                    setter(username, password)
                    print(f"Credentials stored using '{method}' backend.")
                    return
                except NotImplementedError:
                    warnings.warn(
                        f"Setting credentials not supported for '{method}'"
                        " backend.")
                except Exception as e:
                    warnings.warn(
                        f"Failed to store credentials with '{method}': {e}")
        warnings.warn(
            "Credentials could not be saved with any available method.")
