from app.routes.sel import highlight_term, is_address_input_valid


class TestSelFunctions:
    def test_highlight_simple(self):
        h = highlight_term('a b c', 'b', '[', ']')
        assert h == 'a [b] c'

    def test_highlight_nothing(self):
        h = highlight_term('', 'b', '[', ']')
        assert h == ''

    def test_highlight_empty_search(self):
        h = highlight_term('a b c', '', '[', ']')
        assert h == 'a b c'

    def test_highlight_start_hit(self):
        h = highlight_term('a b c', 'a', '[', ']')
        assert h == '[a] b c'

    def test_highlight_end_hit(self):
        h = highlight_term('a b c', 'c', '[', ']')
        assert h == 'a b [c]'

    def test_highlight_postcode(self):
        h = highlight_term('6A Okehampton Road, Exeter, EX4 1EH', 'EX4 1EH', '<b>', '<b/>')
        assert h == '6A Okehampton Road, Exeter, <b>EX4 1EH<b/>'

    def test_highlight_postcode_space_insensitive(self):
        h = highlight_term('6A Okehampton Road, Exeter, EX4 1EH', 'EX41EH', '<b>', '<b/>')
        assert h == '6A Okehampton Road, Exeter, <b>EX4 1EH<b/>'

    def test_highlight_address_partial_spase_insensitive(self):
        h = highlight_term('6A Okehampton Road, Exeter, EX4 1EH', 'Oke hamp  ton', '<b>', '<b/>')
        assert h == '6A <b>Okehampton<b/> Road, Exeter, EX4 1EH'

    def test_valid_input(self):
        assert is_address_input_valid('abcdefg')

    def test_valid_input_with_stripped(self):
        assert is_address_input_valid(" a,bc'd'e,  ")

    def test_reject_input_too_few_when_stripped(self):
        assert not is_address_input_valid(" a,bc'd',  ")
