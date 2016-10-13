#!/usr/bin/python2

from __future__ import print_function


class Cmd(object):
    def __init__(self, parsed_args, raw_args):
        self.parsed_args = parsed_args
        self.raw_args = raw_args
        self.cmd = None
        self.extra_args = None
        self.ret = 0


    def callps(self, *args, **kwargs):
        from subprocess import Popen

        print('subprocess: {0}'.format(args[0]))
        ps = Popen(*args, **kwargs)
        self.ret = ps.wait()
        return self.ret


    def execvp(self, args):
        from os import execvp

        print('execvp: {0}'.format(args))
        # Point of no return.
        execvp(args[0], args)


    def get_odoo_addons_paths(self):
        from os import environ

        from ConfigParser import SafeConfigParser

        if self.parsed_args.addons_path:
            return self.parsed_args.addons_path.split(',')

        config = SafeConfigParser()
        config.read(environ['OPENERP_SERVER'])
        return config.get('options', 'addons_path').split(',')


    def psql_query(self, query):
        self.callps(['psql', '-c', query])


    def prerun(self):
        from os import environ as env

        if 'POSTGRES_PORT_5432_TCP_ADDR' in env:
            env['PGHOST'] = env['POSTGRES_PORT_5432_TCP_ADDR']
        else:
            env['PGHOST'] = 'postgres'

        if 'POSTGRES_PORT_5432_TCP_PORT' in env:
            env['PGPORT'] = env['POSTGRES_PORT_5432_TCP_PORT']
        else:
            env['PGPORT'] = '5432'


        if 'POSTGRES_ENV_POSTGRES_USER' in env:
            env['PGUSER'] = env['POSTGRES_ENV_POSTGRES_USER']

        if 'POSTGRES_ENV_POSTGRES_PASSWORD' in env:
            env['PGPASSWORD'] = env['POSTGRES_ENV_POSTGRES_PASSWORD']

        if 'POSTGRES_ENV_POSTGRES_DB' not in env and 'PGDATABASE' not in env:
            env['PGDATABASE'] = env['PGUSER']

        self.cmd = [
            'openerp-server',
            '--db_host', env['PGHOST'],
            '--db_port', env['PGPORT'],
            '--db_user', env['PGUSER'],
            '--db_password', env['PGPASSWORD'],
        ]

        if self.parsed_args.addons_path:
            self.cmd.extend(['--addons-path', self.parsed_args.addons_path])

        self.extra_args = self.parsed_args.odoo_args[1:]


    def postrun(self):
        # Append args after '--'
        self.cmd.extend(self.extra_args)

        self.execvp(self.cmd)



class TestCmd(Cmd):
    def __init__(self, parsed_args, raw_args):
        super(self.__class__, self).__init__(parsed_args, raw_args)


    def extend_test_type_args(self):
        from glob import glob
        from os import path

        if self.parsed_args.test_base:
            self.cmd.extend([
                '--database', 'test_base',
                '--init', 'base',
            ])
        elif self.parsed_args.test_all:
            modules = []
            for p in self.get_odoo_addons_paths():
                module_paths = (
                    glob(path.join(p.strip(), '*/__openerp__.py')) +
                    glob(path.join(p.strip(), '*/__manifest__.py'))
                )

                for module_path in module_paths:
                    module = path.basename(path.dirname(module_path))
                    modules.append(module)

            modules = set(modules)

            if self.parsed_args.test_except:
                for m in self.parsed_args.test_except.split(','):
                    modules.remove(m.strip())

            self.cmd.extend([
                '--database', 'test_all',
                '--init', ','.join(modules),
            ])


    def run(self):
        self.prerun()

        self.cmd.extend([
            '--stop-after-init',
            '--test-enable',
            '--log-level', 'test',
            '--max-cron-threads', '0',
        ])

        self.extend_test_type_args()
        self.postrun()



class ServeCmd(Cmd):
    def __init__(self, parsed_args, raw_args):
        super(self.__class__, self).__init__(parsed_args, raw_args)


    def run(self):
        from os import environ as env

        self.prerun()

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

        if not self.parsed_args.demo:
            self.cmd.extend([
                '--without-demo', 'all'
            ])

        if self.parsed_args.autoset or self.parsed_args.single:
            self.cmd.extend([
                '--database', env['PGDATABASE'],
                '--db-filter', env['PGDATABASE'],
            ])

        self.postrun()


def serve(parsed_args, raw_args):
    serve_cmd = ServeCmd(parsed_args, raw_args)
    return serve_cmd.run()


def test(parsed_args, raw_args):
    test_cmd = TestCmd(parsed_args, raw_args)
    return test_cmd.run()


def main(args=None):
    from argparse import REMAINDER, ArgumentParser
    import sys

    if args is None:
        args = sys.argv[1:]

    p = ArgumentParser(description='odoo docker image')
    p.add_argument(
        '--addons-path',
        help='Sets addons_path for odoo.',
        required=False,
    )
    sp = p.add_subparsers(help='sub-command help', dest='command')
    sp_serve = sp.add_parser('serve', help='start the server')
    sp_serve.add_argument(
        '--autoset',
        help='Automatically set the arguments of odoo.py',
        action='store_true',
    )
    sp_serve.add_argument(
        '--demo',
        help='Install demo data when initializing',
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

    sp_test = sp.add_parser('test', help='run tests')
    sp_test.add_argument(
        '--except',
        help='Test all except the following modules',
        type=str,
        dest='test_except',
    )
    sp_test.add_argument(
        'odoo_args',
        nargs=REMAINDER,
        help='Odoo arguments can be specified after a double dash (--)',
    )
    sp_test_mutex = sp_test.add_mutually_exclusive_group(required=True)
    sp_test_mutex.add_argument(
        '--base',
        help='Run the test suite for module "base".',
        action='store_true',
        dest='test_base',
    )
    sp_test_mutex.add_argument(
        '--all',
        help='Run the test suite for all modules that is available.',
        action='store_true',
        dest='test_all',
    )

    sp_test.set_defaults(func=test)
    parsed_args = p.parse_args()

    if parsed_args.command == 'test' and parsed_args.test_except and not parsed_args.test_all:
        sp_test.error('--except can only be used with --all')

    return parsed_args.func(parsed_args, args)


def run_main(args=None):
    try:
        main(args)
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    import sys
    sys.exit(run_main())
