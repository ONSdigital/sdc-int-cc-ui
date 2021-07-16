import pytest

from app.utils import ProcessPostcode, ProcessMobileNumber
from app.errors.handlers import InvalidDataError


class TestPostcodeValidation:
    def test_validate_postcode_valid(self):
        postcode = 'PO15 5RR'
        locale = 'en'

        # When validate_postcode is called
        ProcessPostcode.validate_postcode(postcode)
        # Nothing happens

    def test_validate_postcode_valid_with_unicode(self):
        postcode = 'BS２ ０FW'
        # When validate_postcode is called
        ProcessPostcode.validate_postcode(postcode)
        # Nothing happens

    def test_validate_postcode_empty(self):
        postcode = ''
        # When validate_postcode is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessPostcode.validate_postcode(postcode)
        # Then an InvalidDataError is raised
        assert "Enter the caller's postcode" in str(cm.value)
        # With the correct message

    def test_validate_postcode_not_alphanumeric(self):
        postcode = '?<>:{}'
        # When validate_postcode is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessPostcode.validate_postcode(postcode)
        # Then an InvalidDataError is raised
        assert 'Postcode can only contain letters and numbers' in str(cm.value)
        # With the correct message

    def test_validate_postcode_short(self):
        postcode = 'PO15'
        # When validate_postcode is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessPostcode.validate_postcode(postcode)
        # Then an InvalidDataError is raised
        assert 'Postcode is too short' in str(cm.value)
        # With the correct message

    def test_validate_postcode_long(self):
        postcode = 'PO15 5RRR'
        # When validate_postcode is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessPostcode.validate_postcode(postcode)
        # Then an InvalidDataError is raised
        assert 'Postcode is too long' in str(cm.value)
        # With the correct message

    def test_validate_postcode_invalid(self):
        postcode = 'ZZ99 9ZZ'
        # When validate_postcode is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessPostcode.validate_postcode(postcode)
        # Then an InvalidDataError is raised
        assert 'Enter a valid UK postcode' in str(cm.value)
        # With the correct message


class TestMobileValidation:
    def test_validate_uk_mobile_phone_number_valid(self):
        mobile_number = '070 1234 5678'
        # When validate_uk_mobile_phone_number is called
        ProcessMobileNumber.validate_uk_mobile_phone_number(mobile_number)
        # Nothing happens

    def test_validate_uk_mobile_phone_number_short(self):
        mobile_number = '070 1234'
        # When validate_uk_mobile_phone_number is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessMobileNumber.validate_uk_mobile_phone_number(mobile_number)
        # Then an InvalidDataError is raised
        assert 'Enter a UK mobile number in a valid format, for example, 07700 900345 or +44 7700 900345' in \
               str(cm.value)
        # With the correct message

    def test_validate_uk_mobile_phone_number_long(self):
        mobile_number = '070 1234 5678 9012 3456 7890'
        # When validate_uk_mobile_phone_number is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessMobileNumber.validate_uk_mobile_phone_number(mobile_number)
        # Then an InvalidDataError is raised
        assert 'Enter a UK mobile number in a valid format, for example, 07700 900345 or +44 7700 900345' in \
               str(cm.value)
        # With the correct message

    def test_validate_uk_mobile_phone_number_not_mobile(self):
        mobile_number = '020 1234 5678'
        # When validate_uk_mobile_phone_number is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessMobileNumber.validate_uk_mobile_phone_number(mobile_number)
        # Then an InvalidDataError is raised
        assert 'Enter a UK mobile number in a valid format, for example, 07700 900345 or +44 7700 900345' in \
               str(cm.value)
        # With the correct message

    def test_validate_uk_mobile_phone_number_not_numeric(self):
        mobile_number = 'gdsjkghjdsghjsd'
        # When validate_uk_mobile_phone_number is called
        with pytest.raises(InvalidDataError) as cm:
            ProcessMobileNumber.validate_uk_mobile_phone_number(mobile_number)
        # Then an InvalidDataError is raised
        assert 'Enter a UK mobile number in a valid format, for example, 07700 900345 or +44 7700 900345' in \
               str(cm.value)
        # With the correct message
