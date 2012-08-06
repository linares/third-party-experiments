"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import twitter

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        api=twitter.Api(consumer_key='ZU6XVnclcgHpQjdqK8zUw',consumer_secret='P0tRX3Pb1n5ExNYJfIc4oGlYtzufBSZj9Ou5Mkg5Q', access_token_key='19981603-Oh58oj8mZpc4gaTb81LhQdOTxSccYEyTsF5LyoeCv', access_token_secret='0VVAbyw9gHRuE7af38BZLad0kfN2weMgP3OIryRn6wM')
        timeline = api.GetUserTimeline(count=50, include_entities=True)
        print timeline


