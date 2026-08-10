import cooked_input as ci


class TestErrFmt(object):

    def test_err_fmt(self, fake_input):
        input_str = 'foo\nbar\nblat\nfoo\nbar\nblat'

        err_fmt_str = 'You entered: "{value}", I said not "foo" or "bar" ({error_content})'
        not_foo_validator = ci.NoneOfValidator(ci.ChoiceValidator(['foo', 'bar']))

        # Both prompts read from the one script, so the second consumes the second
        # foo/bar/blat run -- same as sharing a single StringIO used to.
        feeder = fake_input(input_str)

        result = ci.get_string(prompt='Enter a value (not "foo" or "bar")', validators=not_foo_validator)
        assert (result == 'blat')

        result = ci.get_string(prompt='Enter a value (not "foo" or "bar") - w error fmt str', validators=not_foo_validator, validator_error_fmt=err_fmt_str)
        assert (result == 'blat')

        assert feeder.remaining == 0
