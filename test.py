from daggerwrapper.wrapper import DaggerWrapper
import dagger 
import anyio

async def test():
    async with dagger.Connection() as client:
        wrapper = DaggerWrapper(client)

        versions = ["latest", "11", "10"]
        # version = await wrapper.get_python_version()
        
        drupal = await wrapper.get_drupal_service()

        for version in versions:
            mariadb = await wrapper.get_mariadb_service(version)
            test = await (
                drupal.with_service_binding("db", mariadb)
                .with_env_variable("SIMPLETEST_DB", "mysql://user:password@db/drupal")
                .with_env_variable("SYMFONY_DEPRECATIONS_HELPER", "disabled")
                .with_workdir("/opt/drupal/web/core")
                .with_exec(["../../vendor/bin/phpunit", "-v", "--group", "KernelTests"])
                .stdout()
            )
            print(f"Starting tests for MariaDB {version}")
            print(test)

anyio.run(test)