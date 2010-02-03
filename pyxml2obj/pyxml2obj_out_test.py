#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import unittest
from pyxml2obj import XMLin, XMLout

class XML2objOutTest(unittest.TestCase):
  def testScalar(self):
    xml = XMLout('scalar')
    self.assertEqual(XMLin(xml), 'scalar')

  def testHash(self):
    hash1 = {'one': '1', 'two': 'II', 'three': '...'}
    xml = XMLout(hash1)
    self.assertEqual(XMLin(xml), hash1)

  def testSimmpleArray(self):
    tree = {'array' : ['one', 'two', 'three']}
    expect = \
'''<root>
  <array>one</array>
  <array>two</array>
  <array>three</array>
</root>
'''
    xml = XMLout(tree)
    self.assertEqual(xml, expect)

  def testNestedHash(self):
    tree = { 'value' : '555 1234',
             'hash1' : { 'one' : 1 },
             'hash2' : { 'two' : 2 }}
    expected = \
'''<root value="555 1234">
  <hash1 one="1" />
  <hash2 two="2" />
</root>
'''
    xml = XMLout(tree)
    self.assertEqual(xml, expected)

  def testAnonymousArray(self):
    tree = ['1', 'two', 'Ⅲ']
    expected = \
'''<root>
  <anon>1</anon>
  <anon>two</anon>
  <anon>Ⅲ</anon>
</root>
'''
    xml = XMLout(tree)
    self.assertEqual(xml, expected)

  def testNestedAnonymousArray(self):
    tree = [[1.1, 1.2], [2.1, 2.2]]
    expected = \
'''<root>
  <anon>
    <anon>1.1</anon>
    <anon>1.2</anon>
  </anon>
  <anon>
    <anon>2.1</anon>
    <anon>2.2</anon>
  </anon>
</root>
'''
    xml = XMLout(tree)
    self.assertEqual(xml, expected)

  def testHashOfHash(self):
    tree = { 'country' : {
      'England' : { 'capital' : 'London' },
      'France'  : { 'capital' : 'Paris' },
      'Turkey'  : { 'capital' : 'Istanbul' },
      }}
    expected = \
'''<root>
  <country>
    <England capital="London" />
    <France capital="Paris" />
    <Turkey capital="Istanbul" />
  </country>
</root>
'''
    xml = XMLout(tree, {'keyattr':[]})
    self.assertEqual(xml, expected)

    expected = r'''
^\s*<(\w+)\s*>\s*
(
   <country(\s*fullname="Turkey"  |\s*capital="Istanbul" ){2}\s*/>\s*
  |<country(\s*fullname="France"  |\s*capital="Paris"    ){2}\s*/>\s*
  |<country(\s*fullname="England" |\s*capital="London"   ){2}\s*/>\s*
){3}
</\1>\s*$
'''
    xml = XMLout(tree, {'keyattr':['fullname']})
    self.assert_(re.match(expected, xml, re.VERBOSE))

    xml = XMLout(tree, {'keyattr':'fullname'})
    self.assert_(re.match(expected, xml, re.VERBOSE))

    xml = XMLout(tree, {'keyattr':{'country':'fullname'}})
    self.assert_(re.match(expected, xml, re.VERBOSE))

    xml = XMLout(tree, {'keyattr':{'country':'+fullname'}})
    self.assert_(re.match(expected, xml, re.VERBOSE))

    xml = XMLout(tree, {'keyattr':{'country':'-fullname'}})
    self.assert_(re.match(expected, xml, re.VERBOSE))

    expected = r'''
  ^\s*<(\w+)\s*>\s*
    (
      <country(\s*name="Turkey"|\s*capital="Istanbul"){2}\s*/>\s*
     |<country(\s*name="France"|\s*capital="Paris"){2}\s*/>\s*
     |<country(\s*name="England"|\s*capital="London"){2}\s*/>\s*
    ){3}
  </\1>$
  '''
    xml = XMLout(tree)
    self.assert_(re.match(expected, xml, re.VERBOSE))

  def test_forld_a_nested_hash(self):
    tree = { 'country' : { 'England' : { 'capital' : 'London' }}}
    xml = XMLout(tree)
    expected = r'''
  ^\s*<(\w+)\s*>\s*
    (
     <country(\s*name="England"|\s*capital="London"){2}\s*/>\s*
    )
  </\1>$
  '''
    self.assert_(re.match(expected, xml, re.VERBOSE))

  def test_xml_decl(self):
    tree = { 'one' : 1 }
    xml = XMLout(tree, {'xmldecl':1})
    no_header = xml.replace("<?xml version='1.0' standalone='yes'?>", '')
    self.assertTrue(xml != no_header)
    self.assert_(re.match(r'^\s*<root\s+one="1"\s*/>', no_header, re.VERBOSE))

    custom_header = '<?xml custom header ?>'
    xml = XMLout(tree, {'xmldecl':custom_header})
    no_header = xml.replace(custom_header, '')
    self.assertTrue(xml != no_header)
    self.assert_(re.match(r'^\s*<root\s+one="1"\s*/>', no_header, re.VERBOSE))

    
  def test_escape(self):
    tree = { 'a' : '<A>', 'b' : '"B"', 'c' : '&C&' }

    # check if xml is escaped 
    xml = XMLout(tree)
    self.assert_(re.search('a="&lt;A&gt;"', xml))
    self.assert_(re.search('b="&quot;B&quot;"', xml))
    self.assert_(re.search('c="&amp;C&amp;"', xml))

    # check escape off
    tree = { 'a' : '<A>', 'b' : '"B"', 'c' : ['&C&'] }
    xml = XMLout(tree, {'noescape':1})
    self.assert_(re.search(r'a="<A>"', xml))
    self.assert_(re.search(r'b=""B""', xml))
    self.assert_(re.search(r'<c>&C&</c>', xml))

  def test_circular_data(self):
    tree = {'a': '1'}
    tree['b'] = tree
    try:
      xml = XMLout(tree)
      self.fail('circular data is not detected')
    except:
      pass


if __name__ == '__main__':
  unittest.main()
