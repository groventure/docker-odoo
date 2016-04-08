#!/bin/bash

set -e

fatal=0

if [[ -z "$DB_PORT_5432_TCP_ADDR" ]]; then
  echo '$DB_PORT_5432_TCP_ADDR not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$DB_PORT_5432_TCP_PORT" ]]; then
  echo '$DB_PORT_5432_TCP_PORT not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$DB_ENV_POSTGRES_USER" ]]; then
  echo '$DB_ENV_POSTGRES_USER not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$DB_ENV_POSTGRES_PASSWORD" ]]; then
  echo '$DB_ENV_POSTGRES_PASSWORD not defined. Aborting...' >&2
  fatal=1
fi

if [[ "$fatal" -eq 1 ]]; then
  exit 1
fi

# set odoo database host, port, user and password
: ${PGHOST:=$DB_PORT_5432_TCP_ADDR}
: ${PGPORT:=$DB_PORT_5432_TCP_PORT}
: ${PGUSER:=${DB_ENV_POSTGRES_USER:='postgres'}}
: ${PGPASSWORD:=$DB_ENV_POSTGRES_PASSWORD}
: ${PGDATABASE:=${DB_ENV_POSTGRES_DB:=$DB_ENV_POSTGRES_USER}}
export PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE

if [[ "$PGUSER" != 'postgres' ]]; then
  psql -c 'ALTER DATABASE "'"$PGDATABASE"'" OWNER TO "'"$PGUSER"'"'
  psql -c 'ALTER USER "'"$PGUSER"'" WITH NOCREATEDB'
  psql -c 'ALTER USER "'"$PGUSER"'" WITH NOSUPERUSER'
fi

case "$1" in
  --)
    shift
    exec openerp-server \
      --config='/etc/odoo/openerp-server.conf' \
      --db_host="$PGHOST" \
      --db_port="$PGPORT" \
      --db_user="$PGUSER" \
      --db_password="$PGPASSWORD" \
      --database="$PGDATABASE" \
      --db-filter="$PGDATABASE" \
      --workers=0 \
      "$@"
    ;;
  -*)
    exec openerp-server \
      --config='/etc/odoo/openerp-server.conf' \
      --db_host="$PGHOST" \
      --db_port="$PGPORT" \
      --db_user="$PGUSER" \
      --db_password="$PGPASSWORD" \
      --database="$PGDATABASE" \
      --db-filter="$PGDATABASE" \
      --workers=0 \
      "$@"
    ;;
  *)
    exec \
      --config='/etc/odoo/openerp-server.conf' \
      --db_host="$PGHOST" \
      --db_port="$PGPORT" \
      --db_user="$PGUSER" \
      --db_password="$PGPASSWORD" \
      --database="$PGDATABASE" \
      --db-filter="$PGDATABASE" \
      --workers=0 \
      "$@"
esac

exit 1
