"""
Convenient helper library
"""

class DaggerWrapper():
    """A wrapper for the Dagger SDK"""

    def __init__(self, client):
        """Instantiate a new DaggerWrapper object.

        :param client: An instance of the Dagger client
        """
        self.client = client


    async def get_mariadb_service(self, version=None):
        """
        return mariadb sidecar container

        :param version: Version of MariaDB to use, defaults to "latest"
        """
        if not version:
            version = "latest"
        mariadb = (
            self.client.container()
            .from_(f"mariadb:{version}")
            .with_env_variable("MARIADB_USER", "user")
            .with_env_variable("MARIADB_PASSWORD", "password")
            .with_env_variable("MARIADB_DATABASE", "drupal")
            .with_env_variable("MARIADB_ROOT_PASSWORD", "root")
            .with_exposed_port(3306)
        )

        return await mariadb

    async def get_drupal_service(self):
        """
        return drupal sidecar container
        """
        drupal = (
            self.client.container()
            .from_("drupal:10.0.7-php8.2-fpm")
            .with_exec(
                [
                    "composer",
                    "require",
                    "drupal/core-dev",
                    "--dev",
                    "--update-with-all-dependencies",
                ]
            )
        )

        return await drupal






