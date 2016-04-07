#!/bin/bash

set -e

fatal=0

if [[ -z "$POSTGRES_PORT_5432_TCP_ADDR" ]]; then
  echo '$POSTGRES_PORT_5432_TCP_ADDR not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$POSTGRES_PORT_5432_TCP_PORT" ]]; then
  echo '$POSTGRES_PORT_5432_TCP_PORT not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$POSTGRES_ENV_POSTGRES_USER" ]]; then
  echo '$POSTGRES_ENV_POSTGRES_USER not defined. Aborting...' >&2
  fatal=1
fi

if [[ -z "$POSTGRES_ENV_POSTGRES_PASSWORD" ]]; then
  echo '$POSTGRES_ENV_POSTGRES_PASSWORD not defined. Aborting...' >&2
  fatal=1
fi

if [[ "$fatal" -eq 1 ]]; then
  exit 1
fi

function _get_value {
  if [[ -z "$1" ]]; then
    echo '$1 not provided.' >&2
    return
  fi

  if [[ -n "$2" ]]; then
    echo "$2"
  else
    echo "$1"
  fi
}


# set odoo database host, port, user and password
: ${PGHOST:=$DB_PORT_5432_TCP_ADDR}
: ${PGPORT:=$DB_PORT_5432_TCP_PORT}
: ${PGUSER:=${DB_ENV_POSTGRES_USER:='postgres'}}
: ${PGPASSWORD:=$DB_ENV_POSTGRES_PASSWORD}
export PGHOST PGPORT PGUSER PGPASSWORD

database="$(_get_value "$POSTGRES_ENV_POSTGRES_USER" "$POSTGRES_ENV_POSTGRES_DB")"

case "$1" in
	--)
		shift
		exec openerp-server \
		  --db_host="$POSTGRES_PORT_5432_TCP_ADDR" \
		  --db_port="$POSTGRES_PORT_5432_TCP_PORT" \
		  --database="$database" \
		  --db-filter="$database" \
		  --db_user="$POSTGRES_ENV_POSTGRES_USER" \
		  --db_password="$POSTGRES_ENV_POSTGRES_PASSWORD" \
			"$@"
		;;
	-*)
		exec openerp-server \
		  --db_host="$POSTGRES_PORT_5432_TCP_ADDR" \
		  --db_port="$POSTGRES_PORT_5432_TCP_PORT" \
		  --database="$database" \
		  --db-filter="$database" \
		  --db_user="$POSTGRES_ENV_POSTGRES_USER" \
		  --db_password="$POSTGRES_ENV_POSTGRES_PASSWORD" \
			"$@"
		;;
	*)
		exec --db_host="$POSTGRES_PORT_5432_TCP_ADDR" \
		  --db_port="$POSTGRES_PORT_5432_TCP_PORT" \
		  --database="$database" \
		  --db-filter="$database" \
		  --db_user="$POSTGRES_ENV_POSTGRES_USER" \
		  --db_password="$POSTGRES_ENV_POSTGRES_PASSWORD" \
			"$@"
esac

exit 1
