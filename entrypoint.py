#!/usr/bin/python2

from __future__ import print_function


class Cmd(object):
    def __init__(self, parsed_args, raw_args):
        self.parsed_args = parsed_args
        self.raw_args = raw_args


class ServeCmd(Cmd):
    def __init__(self, parsed_args, raw_args):
        super(self.__class__, self).__init__(parsed_args, raw_args)
        self.ret = 0


    def callps(self, *args, **kwargs):
        from subprocess import Popen

        print('subprocess: {0}'.format(args[0]))
        ps = Popen(*args, **kwargs)
        self.ret = ps.wait()
        return self.ret


    def chkenv(self, envkey):
        import os, sys

        if envkey not in os.environ:
            self.ret = 1
            print('${0} not defined. Aborting.'.format(envkey),
                    file=sys.stderr)


    def psql_query(self, query):
        self.callps(['psql', '-c', query])


    def run(self):
        from os import environ as env

        self.chkenv('POSTGRES_PORT_5432_TCP_ADDR')
        self.chkenv('POSTGRES_PORT_5432_TCP_PORT')
        self.chkenv('POSTGRES_ENV_POSTGRES_USER')
        self.chkenv('POSTGRES_ENV_POSTGRES_PASSWORD')

        if self.ret != 0:
            return self.ret

        env['PGHOST'] = env['POSTGRES_PORT_5432_TCP_ADDR']
        env['PGPORT'] = env['POSTGRES_PORT_5432_TCP_PORT']
        env['PGUSER'] = env['POSTGRES_ENV_POSTGRES_USER']
        env['PGPASSWORD'] = env['POSTGRES_ENV_POSTGRES_PASSWORD']

        if 'POSTGRES_ENV_POSTGRES_DB' not in env:
            env['PGDATABASE'] = env['PGUSER']

        if env['PGUSER'] != 'postgres':
            if self.parsed_args.pg_chown or self.parsed_args.single:
                self.psql_query(
                    'ALTER DATABASE "{0}" OWNER TO "{1}"'
                    .format(env['PGDATABASE'], env['PGUSER'])
                )

            if self.parsed_args.pg_nosuperuser or self.parsed_args.single:
                self.psql_query(
                    'ALTER USER "{0}" WITH NOSUPERUSER'
                    .format(env['PGUSER'])
                )

        odoo_args = self.parsed_args.odoo_args[1:]

        if self.parsed_args.autoset or self.parsed_args.single:
            openerp_server_args = [
                'openerp-server',
                '--db_host', env['PGHOST'],
                '--db_port', env['PGPORT'],
                '--db_user', env['PGUSER'],
                '--db_password', env['PGPASSWORD'],
                '--database', env['PGDATABASE'],
                '--db-filter', env['PGDATABASE'],
            ]
            openerp_server_args.extend(odoo_args)

            self.callps(openerp_server_args)
            return self.ret

        openerp_server_args = ['openerp-server']
        openerp_server_args.extend(odoo_args)

        self.callps(openerp_server_args)
        return self.ret


def serve(parsed_args, raw_args):
    serve_cmd = ServeCmd(parsed_args, raw_args)
    return serve_cmd.run()


def main(args=None):
    from argparse import REMAINDER, ArgumentParser
    import sys

    if args is None:
        args = sys.argv[1:]

    p = ArgumentParser(description='odoo docker image')
    sp = p.add_subparsers(help='sub-command help', dest='command')
    sp_serve = sp.add_parser('serve', help='start the server')
    sp_serve.add_argument(
        '--autoset',
        help='Automatically set the arguments of odoo.py',
        action='store_true',
    )
    sp_serve.add_argument(
        '--pg-chown',
        help='Change owner of linked database to user if defined',
        action='store_true',
    )
    sp_serve.add_argument(
        '--pg-nosuperuser',
        help='Change linked database user with nosuperuser if defined',
        action='store_true',
    )
    sp_serve.add_argument(
        '--single',
        help='Optimise for single db usage. Implies --autoset, --pg-chown and --pg-nosuperuser',
        action='store_true',
    )
    sp_serve.add_argument(
        'odoo_args',
        nargs=REMAINDER,
        help='Odoo arguments can be specified after a double dash (--)',
    )
    sp_serve.set_defaults(func=serve)

    parsed_args = p.parse_args()
    return parsed_args.func(parsed_args, args)


def run_main(args=None):
    try:
        main(args)
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    import sys
    sys.exit(run_main())
