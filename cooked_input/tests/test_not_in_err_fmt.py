import cooked_input as ci


from io import StringIO

from .utils import redirect_stdin


class TestErrFmt(object):

    def test_err_fmt(self):
        input_str = 'foo\nbar\nblat\nfoo\nbar\nblat'

        err_fmt_str = 'You entered: "{value}", I said not "foo" or "bar" ({error_content})'
        not_foo_validator = ci.NoneOfValidator(ci.ChoiceValidator(['foo', 'bar']))

        with redirect_stdin(StringIO(input_str)):
            result = ci.get_string(prompt='Enter a value (not "foo" or "bar")', validators=not_foo_validator)
            assert (result == 'blat')

            result = ci.get_string(prompt='Enter a value (not "foo" or "bar") - w error fmt str', validators=not_foo_validator, validator_error_fmt=err_fmt_str)
            assert (result == 'blat')