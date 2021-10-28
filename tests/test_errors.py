from tests.set_up_test_case import SetUpTestCase


class TestErrors(SetUpTestCase):
    def test_404_renders_template(self):
        self.get("/unknown-path")
        self.assertStatusNotFound()
