# Dagger Wrapper

This is a sample project that shows you how to extend the Dagger SDK to make it reusable accross other projects. It ties together a few themes that have been explored in other Dagger guides. [This Guide](https://docs.dagger.io/757394/use-service-containers#example-mariadb-database-service-for-application-tests) shows a great example of how to to run service containers using MariaDB and Drupal and [this guide](https://docs.dagger.io/sdk/python/628797/get-started/#step-4-test-against-multiple-python-versions) shows how to run matrix builds over multiple versions of Python. 

Imagine that you are working on a Drupal application that supports mulitple version of MariaDB. As a part of your CI process you need to run your test suite against each supported database version. The [Dagger Python SDK](https://docs.dagger.io/sdk/python/) provides us with the building blocks we need to create sidecar containers. We can use these building blocks to create an SDK wrapper that allows us to simplify our project-specific Dagger configuration and create utility functions for all other projects in your organization. 

## Code Walkthrough 

We start by creating a simple Python Class that is instantiated with an instance of a Dagger client. 

```python
def __init__(self, client):
    """Instantiate a new DaggerWrapper object.

    :param client: An instance of the Dagger client
    """
    self.client = client
```

Next, we create a utility function that returns a MariaDB container. This function allows us to specify a specific `version` of MariaDB or defaults to the latest Docker tag.

```python
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
```

Last, we return a drupal sidecar container using the same appraoch as the previously referenced guide. 

```python
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
```

With these things in place we can now publish this simple wrapper library and reuse it accross any other project that needs drupal or MariaDB. 

## Wrapper in Action 

To really appreciate what is happening here, lets start a new project from scratch and use this library. 


Open up a new terminal and run the following commands:

```bash
# create new folder for our project 
mkdir dagger_wrapper_demo

# go into the folder 
cd dagger_wrapper_demo 

# create a python virutalenv
python3 -m venv venv 

# activate the virtualenv
source venv/bin/activate 
```

You can install the wrapper we have been discussing using pip. 

```bash
pip install git+https://github.com/levlaz/dagger-wrapper
```

Create a new file for our Dagger configuration called `main.py` and add the following code to it:

```python
from daggerwrapper.wrapper import DaggerWrapper
import dagger 
import anyio

async def test():
    async with dagger.Connection() as client:
        # create new wrapper and pass in the Dagger client
        wrapper = DaggerWrapper(client)

        # specify MariaDB versions that we are going to test 
        versions = ["latest", "11", "10"]

        # create drupal sidecar
        drupal = await wrapper.get_drupal_service()

        # run test suite for every version of MariaDB
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
```

In this code we are creating a new `wrapper` object which give us the two utility functions that we discussed in the previous section. `get_drupal_service()` creates a Drupal sidecar and `get_mariadb_service()` creates a MariaDB sidecar with a specified version of MariaDB. For each version of MariaDB we will run our full test suite and view the results in the console. 

You can see this in action by running `python main.py`. 

## Running in CI 

With everything working as expected locally, we can complete our journey by getting this working on CI. With the following minimal configuration you can see the same output on CircleCI that you see locally.  

```yaml
version: 2.1

jobs:
  build:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install DaggerWrapper
          command: pip install git+https://github.com/levlaz/dagger-wrapper

      - setup_remote_docker:
          version: 20.10.23
          docker_layer_caching: true

      # Run Dagger
      - run: python main.py
```

# Conclusion 

With this simple example, we have illustrated how you can use the powerful Dagger SDK building blocks to create reusable abstractions. Like any good library, as your needs evolve and organizational complexity increases, you can benefit from having a single source of truth for how to connfigure and run your builds. Most importantly, as the needs of your project grow you can handle the complexity with clean, reusable code, rather than wrangling a thousand line YAML file. 
