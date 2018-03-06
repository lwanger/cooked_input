import cooked_input as ci

err_fmt_str = 'You entered: "{value}", I said not "foo" or "bar" ({error_content})'
not_foo_validator = ci.NoneOfValidator(ci.ChoiceValidator(['foo', 'bar']))
bind_name = ci.get_string(prompt='Enter a value (not "foo" or "bar")', validators=not_foo_validator)
bind_name = ci.get_string(prompt='Enter a value (not "foo" or "bar") - w error fmt str', validators=not_foo_validator, validator_error_fmt=err_fmt_str)
