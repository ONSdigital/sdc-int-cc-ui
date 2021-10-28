import unittest
import zlib

import fakeredis
from bs4 import BeautifulSoup
from itsdangerous import base64_decode
from mock import patch

from app.setup import create_app
from app.utilities.json import json_loads
from application import configure_logging


class SetUpTestCase(unittest.TestCase):  # pylint: disable=too-many-public-methods
    def setUp(self):
        # Perform setup steps
        self._set_up_app()

    @property
    def test_app(self):
        return self._application

    def _set_up_app(self, setting_overrides=None):
        self._redis = patch("app.setup.Session", fakeredis.FakeStrictRedis)
        self._redis.start()

        configure_logging()

        overrides = {}

        if setting_overrides:
            overrides = overrides | setting_overrides

        self._application = create_app(overrides)

        self._client = self._application.test_client()
        self.session = self._client.session_transaction()

    def tearDown(self):
        self._redis.stop()

    def get(self, url, follow_redirects=True, **kwargs):
        """
        GETs the specified URL, following any redirects.

        If the response contains a CSRF token; it is cached to be use on
        the next POST.

        The URL will be cached for future POST requests.

        :param follow_redirects:
        :param url: the URL to GET
        """
        response = self._client.get(url, follow_redirects=follow_redirects, **kwargs)

        self._cache_response(response)

    def post(self, post_data=None, url=None, action=None, **kwargs):
        """
        POSTs to the specified URL with post_data and performs a GET
        with the URL from the re-direct.

        Will add the last received CSRF token to the post_data automatically.

        :param url: the URL to POST to; use None to use the last received URL
        :param post_data: the data to POST
        :param action: The button action to post
        """
        if url is None:
            url = self.last_url

        self.assertIsNotNone(url)

        _post_data = (post_data.copy() or {}) if post_data else {}

        if action:
            _post_data.update({f"action[{action}]": ""})

        response = self._client.post(
            url, data=_post_data, follow_redirects=True, **kwargs
        )

        self._cache_response(response)

    def _cache_response(self, response):
        environ = response.request.environ

        self.redirect_url = response.headers.get("Location")
        self.last_response = response
        self.last_response_headers = dict(response.headers)
        self.last_url = environ["PATH_INFO"]
        if environ["QUERY_STRING"]:
            self.last_url += "?" + environ["QUERY_STRING"]

    def getResponseData(self):
        """
        Returns the last received response data
        """
        return self.last_response.get_data(True)

    def getCookie(self):
        """
        Returns the last received response cookie session
        """
        cookie = self.last_response.headers["Set-Cookie"]
        cookie_session = cookie.split("session=.")[1].split(";")[0]
        decoded_cookie_session = decode_flask_cookie(cookie_session)
        return json_loads(decoded_cookie_session)

    def deleteCookie(self):
        """
        Deletes the test client cookie
        """
        self._client.delete_cookie("localhost", "session")

    def getHtmlSoup(self):
        """
        Returns the last received response data as a BeautifulSoup HTML object
        See https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        :return: a BeautifulSoup object for the response data
        """
        return BeautifulSoup(self.getResponseData(), "html.parser")

    # Extra Helper Assertions
    def assertInHead(self, content):
        self.assertInSelector(content, "head")

    # Extra Helper Assertions
    def assertInBody(self, content):
        self.assertInSelector(content, "body")

    # Extra Helper Assertions
    def assertNotInHead(self, content):
        self.assertNotInSelector(content, "head")

    # Extra Helper Assertions
    def assertNotInBody(self, content):
        self.assertNotInSelector(content, "body")

    def assertInSelector(self, content, selector):
        data = self.getHtmlSoup().select(selector)
        message = f"\n{content} not in \n{data}"

        # intentionally not using assertIn to avoid duplicating the output message
        self.assertTrue(content in str(data), msg=message)

    def assertInSelectorCSS(self, content, *selectors, **kwargs):
        data = self.getHtmlSoup().find(*selectors, **kwargs)
        message = f"\n{content} not in \n{data}"

        # intentionally not using assertIn to avoid duplicating the output message
        self.assertTrue(content in str(data), msg=message)

    def assertNotInSelector(self, content, selector):
        data = self.getHtmlSoup().select(selector)
        message = f"\n{content} in \n{data}"

        # intentionally not using assertIn to avoid duplicating the output message
        self.assertFalse(content in str(data), msg=message)

    def assertNotInPage(self, content, message=None):

        self.assertNotIn(
            member=str(content), container=self.getResponseData(), msg=str(message)
        )

    def assertRegexPage(self, regex, message=None):

        self.assertRegex(
            text=self.getResponseData(), expected_regex=str(regex), msg=str(message)
        )

    def assertEqualPageTitle(self, title):
        self.assertEqual(title, self.getHtmlSoup().title.string)

    def assertStatusOK(self):
        self.assertStatusCode(200)

    def assertBadRequest(self):
        self.assertStatusCode(400)

    def assertStatusUnauthorised(self):
        self.assertStatusCode(401)

    def assertStatusForbidden(self):
        self.assertStatusCode(403)

    def assertStatusNotFound(self):
        self.assertStatusCode(404)
        self.assertInBody("Page not found")

    def assertStatusCode(self, status_code):
        if self.last_response is not None:
            self.assertEqual(status_code, self.last_response.status_code)
        else:
            self.fail("last_response is invalid")

    def assertEqualUrl(self, url):
        if self.last_url:
            self.assertEqual(url, self.last_url)
        else:
            self.fail("last_url is invalid")

    def assertInUrl(self, content):
        if self.last_url:
            self.assertIn(content, self.last_url)
        else:
            self.fail("last_url is invalid")

    def assertNotInUrl(self, content):
        if self.last_url:
            self.assertNotIn(content, self.last_url)
        else:
            self.fail("last_url is invalid")

    def assertRegexUrl(self, regex):
        if self.last_url:
            self.assertRegex(text=self.last_url, expected_regex=regex)
        else:
            self.fail("last_url is invalid")

    def assertInRedirect(self, content):
        if self.redirect_url:
            self.assertIn(content, self.redirect_url)
        else:
            self.fail("no redirect found")


def decode_flask_cookie(cookie):
    """Decode a Flask cookie."""
    data = cookie.split(".")[0]
    data = base64_decode(data)
    data = zlib.decompress(data)
    return data.decode("utf-8")
