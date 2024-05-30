import http.client
import requests
from keycloak import KeycloakOpenID, KeycloakAuthenticationError
from typing import Sequence, NamedTuple

from aiod.config import config

keycloak_openid = KeycloakOpenID(
    server_url=config.auth_server_url,
    client_id=config.client_id,
    realm_name=config.realm,
)


class User(NamedTuple):
    name: str
    roles: Sequence[str]


def login(username: str, password: str) -> None:
    """
    Logs in the user with the provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Raises:
        MissingCredentialsError: If the username or password is missing.
        MissingTokenError: If Keycloak returns an invalid token.
    """
    if username is None or password is None:
        raise FailedAuthenticationError(
            "Username and/or password missing! Please provide your credentials and try again."
        )
    try:
        token = keycloak_openid.token(username, password)
    except KeycloakAuthenticationError as e:
        raise FailedAuthenticationError(
            "Incorrect username or password! Please try again."
        ) from e
    config.access_token = token["access_token"]
    config.refresh_token = token["refresh_token"]


def logout() -> None:
    """
    Logs out the current user.

    Raises:
        MissingTokenError: If the stored refresh token is empty.
    """
    refresh_token = get_refresh_token()

    keycloak_openid.logout(refresh_token)
    config.access_token = None
    config.refresh_token = None


def get_access_token() -> str | None:
    """
    Retrieves the access token.

    Returns:
        str | None: The access token if available, else None.
    """
    return config.access_token


def get_refresh_token() -> str | None:
    """
    Retrieves the refresh token.

    Returns:
        str | None: The refresh token if available, else None.
    """
    return config.refresh_token


def get_current_user() -> User:
    """Return name and roles of the user that is currently authenticated.

    Raises:
        NotAuthenticatedError: When the user is not authenticated.

    Returns:
        User: The user information for the currently authenticated user.
    """
    token = get_access_token()
    response = requests.get(
        f"{config.api_base_url}authorization_test",
        headers={"Authorization": f"Bearer {token}"},
    )

    content = response.json()
    if response.status_code == http.client.UNAUTHORIZED:
        raise NotAuthenticatedError(content)
    return User(
        name=content["name"],
        roles=tuple(content["roles"]),
    )


class FailedAuthenticationError(Exception):
    """Raised when an authentication error occurred."""


class NotAuthenticatedError(Exception):
    """Raised when an endpoint that requires authentication is called without authentication."""
