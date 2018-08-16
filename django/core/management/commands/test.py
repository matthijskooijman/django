import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.utils import get_runner


class Command(BaseCommand):
    help = 'Discover and run tests in the specified modules or the current directory.'

    # DiscoverRunner runs the checks after databases are set up.
    requires_system_checks = False
    test_runner = None

    def prescan_testrunner_option(self, argv):
        option = '--testrunner'
        args = argv[2:]
        for i, arg in enumerate(args):
            if arg == option and i + 1 < len(args):
                return args[i + 1]

            parts = arg.split('=', 2)
            if len(parts) == 2 and parts[0] == option:
                return parts[1]
        return None

    def run_from_argv(self, argv):
        """
        Pre-parse the command line to extract the value of the --testrunner
        option. This allows a test runner to define additional command line
        arguments.
        """
        self.test_runner = self.prescan_testrunner_option(argv)
        super().run_from_argv(argv)

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='test_label', nargs='*',
            help='Module paths to test; can be modulename, modulename.TestCase or modulename.TestCase.test_method'
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--failfast', action='store_true',
            help='Tells Django to stop running the test suite after first failed test.',
        )
        parser.add_argument(
            '--testrunner',
            help='Tells Django to use specified test runner class instead of '
                 'the one specified by the TEST_RUNNER setting.',
        )

        test_runner_class = get_runner(settings, self.test_runner)

        if hasattr(test_runner_class, 'add_arguments'):
            test_runner_class.add_arguments(parser)

    def handle(self, *test_labels, **options):
        TestRunner = get_runner(settings, options['testrunner'])

        test_runner = TestRunner(**options)
        failures = test_runner.run_tests(test_labels)

        if failures:
            sys.exit(1)
