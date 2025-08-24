# Unit test for 404 error page
from django.test import TestCase


class PageNotFoundTestCase(TestCase):
    def test_page_not_found(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "archives/404.html")
