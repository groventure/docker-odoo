About this Repo
======

This is the Git repo of the official Docker image for [Odoo](https://registry.hub.docker.com/_/odoo/). See the Hub page for the full readme on how to use the Docker image and for information regarding contributing and issues.

The full readme is generated over in [docker-library/docs](https://github.com/docker-library/docs), specifically in [docker-library/docs/odoo](https://github.com/docker-library/docs/tree/master/odoo).

# Differences and Improvements

This repository is updated with an improved entrypoint, which is written in python.

## Differences from the official [Odoo Docker Repository](https://github.com/odoo/docker)

+ Linked `postgres` containers now use the token `postgres` instead of `db`. Example: `--link <postgres-container>:postgres`.
+ `PGDATABASE` is set if `POSTGRES_DB` is defined in the linked `postgres` container.
+ Container will not start if **any** of the 4 linked `postgres` variables are not defined. They are:
  + `POSTGRES_PORT_5432_TCP_ADDR`
  + `POSTGRES_PORT_5432_TCP_PORT`
  + `POSTGRES_ENV_POSTGRES_USER`
  + `POSTGRES_ENV_POTGRES_PASSWORD`

## Improvements

Multiple command-line options would now determine how the odoo service is started.

### Command `serve`
`serve` will start the server instead of the default, which was no arguments.

+ `--autoset` will automatically attempt to set the arguments of the `odoo.py` process from the `postgres` environment variables defined from the linked container. These arguments will be set:
  + `--db_host`
  + `--db_port`
  + `--db_user`
  + `--db_password`
  + `--database`
  + `--db-filter`
+ `--pg-chown` will automatically change the owner of the linked database `PGDATABASE` to `PGUSER`.
+ `--pg-nosuperuser` will automatically drop superuser status of `PGUSER`.
+ `--single` will attempt to start the service in single db mode. That is, it implies `--autoset`, `--pg-chown` and `--pg-nosuperuser`.
+ Any arguments after `--` will be passed to `odoo.py` instead.
