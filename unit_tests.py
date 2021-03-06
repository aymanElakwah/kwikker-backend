import pytest
import app
from database_manager import db_manager
import click

all_modules = ['timelines_and_trends', 'authentication_and_registration', 'notifications',
               'direct_messages', 'users_profiles', 'kweeks', 'users_interactions', 'media']


@click.command()
@click.option('--module', default='')
@click.option('--production', is_flag=True)
def cli(module, production):
    if module == '':
        modules = all_modules
    elif module in all_modules:
        modules = [module]
    else:
        print('Module does not exist.')
        raise SystemExit(12)

    if production:
        env = 'production test'
    else:
        env = 'development test'

    if not app.initialize(env=env):
        raise SystemExit(11)

    failed = False
    final_exit_code = 0

    for module in modules:
        db_manager.execute_query_no_return('DELETE FROM USER_CREDENTIALS; DELETE FROM HASHTAG;')
        response = db_manager.execute_query_no_return(open(module + '/seed.sql', 'r').read())
        if response is not None:
            print('Seed error:')
            print(response)
            raise SystemExit(10)
        exit_code = pytest.main(['--cov-report', 'term-missing', '--cov=' + module,
                                 module + '/test_actions.py'])
        if exit_code != 0 and not failed:
            failed = True
            final_exit_code = exit_code

    db_manager.execute_query_no_return('DELETE FROM USER_CREDENTIALS; DELETE FROM HASHTAG;')
    if final_exit_code == 0:
        print('All tests passed.')
    else:
        print('Some tests failed!')
    raise SystemExit(final_exit_code)


if __name__ == '__main__':
    cli()
