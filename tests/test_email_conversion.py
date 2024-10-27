from beautifulemail.base import _standarise_email

def test_email_conversion():

    assert 'test@test.com' == _standarise_email('test@test.com')
    assert 'Last, First <test@test.com>' == _standarise_email({'fname': 'First', 'LName': 'Last', 'email_address': 'test@test.com'})
    assert 'First <test@test.com>' == _standarise_email({'first_name': 'First', 'email': 'test@test.com'})
    assert 'First Last <test@test.com>' == _standarise_email({'full_name': 'First Last', 'email': 'test@test.com'})
    assert 'test@test.com' == _standarise_email({'emailaddress': 'test@test.com'})