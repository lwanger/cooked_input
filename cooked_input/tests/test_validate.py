
"""
pytest tests for cooked_input: test the validate method

Len Wanger, 2017
"""

from cooked_input import validate, InRangeValidator, NotInValidator

class TestValidate(object):

    def test_validate(self):
        validators = [InRangeValidator(min_val=1, max_val=10), NotInValidator(5)]

        for v in [(-1, False), (1, True), (5, False), (6, True), (11, False)]:
            result = validate(v[0], validators)
            assert(result==v[1])
