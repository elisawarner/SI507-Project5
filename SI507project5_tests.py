# least 1 subclass of unittest.TestCase
# at least 5 total test methods (consider what you most need to test!)
# X at least one use of the setUp and tearDown test methods.
# Each of the test methods you write must be good tests (meaning they won't always pass -- or always fail
# they will catch semantic errors -- not just syntax errors).

import unittest
import csv
from SI507project5_code import *

class Part1(unittest.TestCase):
	def setUp(self):
		self.cache = open('cache_contents.json')
		self.csv1 = open('csv1.csv')
		self.csv2 = open('csv2.csv')
		# OAuth Creds
		self.creds = open('creds.json')

	def test_cache_exists(self):
        self.assertTrue(self.cache.read(), 'No cache found')
        self.assertTrue(self.csv1.read(), 'No CSV1 found')
        self.assertTrue(self.csv2.read(), 'No CSV2 found')

    def test_creds(self):
    	self.assertTrue(self.creds.read(),'No OAuth creds found')

    # csv contains rows with 4 columns each
    def test_csv_columns(self):
    	# checks first row
    	self.assertEqual(len(self.csv1.readline()).split(','),4)
    	self.assertEqual(len(self.csv2.readline()).split(','),4)

    # csv tags is a list
    def test_tags_list(self):
    	# should return True as a list
    	reader = csv.reader(csv1, delimiter=',')
    	row1 = next(reader)
    	self.assertEqual(type(row1[3]),type([1,2,3]))

    def test_successful_requests(self):
    	# tests if status code is 200
    	# CHANGE TO TUMBLR VARIABLES
    	r = get_data_from_api(twitter_search_baseurl,"Twitter",twitter_search_params)
    	self.assertTrue(r.status_code == requests.codes.ok)


	def tearDown(self):
		self.cache.close()
		self.csv1.close()
		self.csv2.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
