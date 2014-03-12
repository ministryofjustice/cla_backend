import unittest

from ..util import BetweenDict


class BetweenDictTestCase(unittest.TestCase):
	def setUp(self):
		self.bd = BetweenDict({
		    (0, 6): 1,
		    (6, 10): 2
		})

	def test_direct_get(self):
		for i in range(0, 6):
			self.assertEqual(self.bd[i], 1, u"get(%s) - %s != 1" % (i, self.bd[i]))

		for i in range(6, 10):
			self.assertEqual(self.bd[i], 2, u"get(%s) - %s != 2" % (i, self.bd[i]))

		self.assertRaises(KeyError, lambda : self.bd[10])
		self.assertRaises(KeyError, lambda : self.bd[-1])
		self.assertRaises(KeyError, lambda : self.bd[10000])

	def test_direct_get_with_gaps(self):
		gapped_bd = BetweenDict({
		    (0, 6): 1,
		    (11, 13): 2
		})

		for i in range(0, 6):
			self.assertEqual(gapped_bd[i], 1, u"get(%s) - %s != 1" % (i, gapped_bd[i]))

		for i in range(6, 11):
			self.assertRaises(KeyError, lambda : gapped_bd[i])

		for i in range(11, 13):
			self.assertEqual(gapped_bd[i], 2, u"get(%s) - %s != 2" % (i, gapped_bd[i]))


	def test_get_with_default(self):
		for i in range(0, 6):
			self.assertEqual(self.bd.get(i), 1, u"get(%s) - %s != 1" % (i, self.bd[i]))

		for i in range(6, 10):
			self.assertEqual(self.bd.get(i), 2, u"get(%s) - %s != 2" % (i, self.bd[i]))

		self.assertEqual(self.bd.get(10, 90), 90)
		self.assertEqual(self.bd.get(-1, 90), 90)
		self.assertEqual(self.bd.get(10000, 90), 90)

	def test_contains(self):
		for i in range(0, 10):
			self.assertTrue(i in self.bd)

		self.assertFalse(10 in self.bd)
		self.assertFalse(-1 in self.bd)
		self.assertFalse(10000 in self.bd)

	def test_iter_not_implemented(self):
		"""
		Test that cannot iterate over the between dict
		"""
		self.assertRaises(NotImplementedError, lambda : [i for i in self.bd])

	def test_del_not_implemented(self):
		"""
		Test that cannot delete elements in the between dict
		"""
		def del_el():
			del self.bd[0]
		self.assertRaises(TypeError, del_el)

	def test_len(self):
		self.assertEqual(len(self.bd), 2)

	def test_overlapping_values(self):
		self.assertRaises(ValueError, BetweenDict, {
		    (0, 6): 1,
		    (5, 10): 2
		})

		self.assertRaises(ValueError, BetweenDict, {
		    (5, 6): 1,
		    (0, 6): 2
		})

