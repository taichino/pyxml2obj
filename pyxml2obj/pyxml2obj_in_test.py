#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyxml2obj import XMLin

class Xml2objInTest(unittest.TestCase):

  def testSimpleXML(self):
    expected = {'name1':'value1',
                'name2':'value2'}
    
    # attribute
    opt = XMLin('<opt name1="value1" name2="value2"></opt>')
    self.assertEqual(opt, expected)
    self.assertEqual(isinstance(opt, dict), True)

    # no close tag
    opt = XMLin('<opt name1="value1" name2="value2" />')
    self.assertEqual(opt, expected)

    # element
    opt = XMLin("""
    <opt> 
      <name1>value1</name1>
      <name2>value2</name2>
    </opt>
    """)
    self.assertEqual(opt, expected)

  def testTwoLists(self):
    opt = XMLin("""
    <opt> 
      <name1>value1.1</name1>
      <name1>value1.2</name1>
      <name1>value1.3</name1>
      <name2>value2.1</name2>
      <name2>value2.2</name2>
      <name2>value2.3</name2>
    </opt>""")
    self.assertEqual(opt, {
      'name1': [ 'value1.1', 'value1.2', 'value1.3' ],
      'name2': [ 'value2.1', 'value2.2', 'value2.3' ]})

  def testSimpleNestedHash(self):
    # simple nested hash
    opt = XMLin('<opt><item name1="value1" name2="value2" /></opt>')
    self.assertEqual(opt, {
      'item': {'name1':'value1', 'name2':'value2'}})

    # list of nested hash
    opt = XMLin('''
    <opt> 
      <item name1="value1" name2="value2" />
      <item name1="value3" name2="value4" />
    </opt>
    ''')
    self.assertEqual(opt, {
      'item' : [
        { 'name1': 'value1', 'name2':'value2' },
        { 'name1': 'value3', 'name2':'value4' }]
      })

    # list of nested hashes transformed into a hash using default key names
    xml = '''
    <opt> 
      <item name="item1" attr1="value1" attr2="value2" />
      <item name="item2" attr1="value3" attr2="value4" />
    </opt>
    '''
    opt = XMLin(xml)
    self.assertEqual(opt, {
      'item': {
        'item1': { 'attr1': 'value1', 'attr2': 'value2' },
        'item2': { 'attr1': 'value3', 'attr2': 'value4' }}
      })

    # some thing left as an array by supperssing default key names
    opt = XMLin(xml, {
      'keyattr' : [],
      'contentkey':'-content'})
    self.assertEqual(opt, {
      'item': [
        {'name' : 'item1', 'attr1' : 'value1', 'attr2' : 'value2' },
        {'name' : 'item2', 'attr1' : 'value3', 'attr2' : 'value4' }
        ]})
    # same again with alternative key suppression
    opt = XMLin(xml, {
      'keyattr' : {},
      'contentkey':'-content'})
    self.assertEqual(opt, {
      'item': [
        {'name' : 'item1', 'attr1' : 'value1', 'attr2' : 'value2' },
        {'name' : 'item2', 'attr1' : 'value3', 'attr2' : 'value4' }
        ]})
    # try the other default key attribute names
    opt = XMLin('''
    <opt> 
      <item key="item1" attr1="value1" attr2="value2" />
      <item key="item2" attr1="value3" attr2="value4" />
    </opt>
    ''', {'contentkey':'-content'})
    self.assertEqual(opt,{
      'item' : {
        'item1' : { 'attr1' : 'value1', 'attr2' : 'value2' },
        'item2' : { 'attr1' : 'value3', 'attr2' : 'value4' }
	  }})
    opt = XMLin('''
    <opt> 
      <item id="item1" attr1="value1" attr2="value2" />
      <item id="item2" attr1="value3" attr2="value4" />
    </opt>
    ''', {'contentkey':'-content'})
    self.assertEqual(opt,{
      'item' : {
        'item1' : { 'attr1' : 'value1', 'attr2' : 'value2' },
        'item2' : { 'attr1' : 'value3', 'attr2' : 'value4' }
	  }})

  def testUserKey(self):
    xml = '''
    <opt> 
      <item xname="item1" attr1="value1" attr2="value2" />
      <item xname="item2" attr1="value3" attr2="value4" />
    </opt>
    '''
    target = {
      'item' : {
        'item1' : { 'attr1' : 'value1', 'attr2' : 'value2' },
        'item2' : { 'attr1' : 'value3', 'attr2' : 'value4' }
        }
      }
    opt = XMLin(xml, {'keyattr':['xname'], 'contentkey':'-content'})
    self.assertEqual(opt, target)

    # same again but with key field further down the list
    opt = XMLin(xml, {'keyattr':['wibble', 'xname'], 'contentkey':'-content'})
    self.assertEqual(opt, target)

    # with precise element/key specification
    opt = XMLin(xml, {'keyattr':{'item' : 'xname'}, 'contentkey':'-content'})
    self.assertEqual(opt, target)

    # with field supplied as scalar
    opt = XMLin(xml, {'keyattr': 'xname', 'contentkey':'-content'})
    self.assertEqual(opt, target)

    # with mixed-case option name
    opt = XMLin(xml, {'KeyAttr': 'xname', 'contentkey':'-content'})
    self.assertEqual(opt, target)

    # with underscores in option name
    opt = XMLin(xml, {'key_attr': 'xname', 'contentkey':'-content'})
    self.assertEqual(opt, target)

  def testOverlapKey(self):
    xml = '''
    <opt>
      <item id="one" value="1" name="a" />
      <item id="two" value="2" />
      <item id="three" value="3" />
    </opt>
    '''
    target = { 'item' : {
      'three' : { 'value' : '3' },
      'a'     : { 'value' : '1', 'id' : 'one' },
      'two'   : { 'value' : '2' }
      }}
    opt = XMLin(xml, {'contentkey':'-content'})
    self.assertEqual(opt, target)
    target = { 'item' : {
      'one'   : { 'value' : '1', 'name' : 'a' },
      'two'   : { 'value' : '2' },
      'three' : { 'value' : '3' },
      }}
    opt = XMLin(xml, {'keyattr':{'item':'id'}, 'contentkey':'-content'})
    self.assertEqual(opt, target)

  def testMoreComplex(self):
    xml = '''
    <opt>
      <car license="SH6673" make="Ford" id="1">
        <option key="1" pn="6389733317-12" desc="Electric Windows"/>
        <option key="2" pn="3735498158-01" desc="Leather Seats"/>
        <option key="3" pn="5776155953-25" desc="Sun Roof"/>
      </car>
      <car license="LW1804" make="GM"   id="2">
        <option key="1" pn="9926543-1167" desc="Steering Wheel"/>
      </car>
    </opt>
    '''
    target = {
      'car' : {
        'LW1804' : {
          'id' : '2',
          'make' : 'GM',
          'option' : {
            '9926543-1167' : { 'key' : '1', 'desc' : 'Steering Wheel' }
            }
          },
        'SH6673' : {
          'id' : '1',
          'make' : 'Ford',
          'option' : {
            '6389733317-12' : { 'key' : '1', 'desc' : 'Electric Windows' },
            '3735498158-01' : { 'key' : '2', 'desc' : 'Leather Seats' },
            '5776155953-25' : { 'key' : '3', 'desc' : 'Sun Roof' }
            }
          }
        }
      }
    opt = XMLin(xml, {'forcearray':1, 'keyattr':{'car':'license', 'option':'pn'}, 'contentkey':'-content'})
    self.assertEqual(opt, target)

    xml = '''
    <opt>
      <item>
        <name><firstname>Bob</firstname></name>
        <age>21</age>
      </item>
      <item>
        <name><firstname>Kate</firstname></name>
        <age>22</age>
      </item>
    </opt>    
    '''
    target = {
      'item' : [
        { 'age' : '21', 'name' : {'firstname' : 'Bob'}},
        { 'age' : '22', 'name' : {'firstname' : 'Kate'}},
        ]}
    opt = XMLin(xml, {'contentkey':'-content'})
    self.assertEqual(opt, target)

  def testAnounymousArray(self):
    xml = '''
      <opt>
        <row>
          <anon>0.0</anon><anon>0.1</anon><anon>0.2</anon>
        </row>
        <row>
          <anon>1.0</anon><anon>1.1</anon><anon>1.2</anon>
        </row>
        <row>
          <anon>2.0</anon><anon>2.1</anon><anon>2.2</anon>
        </row>
      </opt>
      '''
    expected = {
      'row' : [
        [ '0.0', '0.1', '0.2' ],
        [ '1.0', '1.1', '1.2' ],
        [ '2.0', '2.1', '2.2' ]
        ]
      }
    opt = XMLin(xml, {'contentkey':'-content'})
    self.assertEqual(opt, expected)

    xml = '''
    <opt>
      <anon>one</anon>
      <anon>two</anon>
      <anon>three</anon>
    </opt>
    '''
    opt = XMLin(xml)
    target = ['one', 'two', 'three']
    self.assertEqual(opt, target)

    xml = '''
    <opt>
      <anon>1</anon>
      <anon>
        <anon>2.1</anon>
        <anon>
          <anon>2.2.1</anon>
          <anon>2.2.2</anon>
        </anon>
      </anon>
    </opt>
    '''
    opt = XMLin(xml)
    target = [
      '1', ['2.1', [ '2.2.1', '2.2.2']]]
    self.assertEqual(opt, target)

  def testContentAttribute(self):
    xml = '''
    <opt>
      <item attr="value">text</item>
    </opt>
    '''
    target = {
      'item' : {
        'content' : 'text',
        'attr'    : 'value'
        }}
    opt = XMLin(xml)
    self.assertEqual(opt, target)

    # check that we can change its name if required
    opt = XMLin(xml, {'contentkey' : 'text_content'})
    self.assertEqual(opt,{
      'item' : {
        'text_content' : 'text',
        'attr'    : 'value'
        }})

    # check that it doesnt get screwed up by forcearray option
    xml = '<opt attr="value">text content</opt>'
    opt = XMLin(xml, {'forcearray' : 1});
    self.assertEqual(opt, {
      'attr'    : 'value',
      'content' : 'text content'})

  def test_forcearray(self):
    xml = '''
    <opt zero="0">
      <one>i</one>
      <two>ii</two>
      <three>iii</three>
      <three>3</three>
      <three>c</three>
    </opt>    
    '''
    opt = XMLin(xml, {'forcearray':['two']})
    self.assertEqual(opt, {
      'zero'  : '0',
      'one'   : 'i',
      'two'   : [ 'ii' ],
      'three' : [ 'iii', '3', 'c' ]})

  def testJapaneseNode(self):
    xml = '''
    <opt> 
      <name1>バリュー１</name1>
      <name2>バリュー２</name2>
    </opt>
    '''
    target = {
      'name1': u'バリュー１',
      'name2': u'バリュー２'
      }
    opt = XMLin(xml)
    self.assertEqual(opt, target)
    
if __name__ == '__main__':
  unittest.main()
