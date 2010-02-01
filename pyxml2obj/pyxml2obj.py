#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import re
from xml.sax import *

def XMLin(content, options={}):
  obj = xml2obj(options)
  obj.XMLin(content)
  return obj.tree

StrictMode  = 0
KnownOptIn  = 'keyattr keeproot forcecontent contentkey noattr \
               forcearray cache suppressempty parseropts \
               grouptags nsexpand datahandler varattr variables \
               normalizespace valueattr'.split()
KnownOptOut = 'keyattr keeproot contentkey noattr \
               rootname xmldecl outputfile noescape suppressempty \
               grouptags nsexpand handler noindent attrindent nosort \
               valueattr numericescape'.split()
DefKeyAttr     = 'name key id'.split()
DefRootName    = 'opt'
DefContentKey  = 'content'
DefXmlDecl     = "<?xml version='1.0' standalone='yes'?>"


class xml2obj(ContentHandler):

  def __init__(self, options={}):
    known_opt = {}
    for key in KnownOptIn + KnownOptOut:
      known_opt[key] = None

    def_opt = {}
    for key, val in options.items():
      lkey = key.lower().replace('_', '')
      if not lkey in known_opt:
        raise KeyError('%s is not acceptable' % (lkey,))
      def_opt[lkey] = val
    self.def_opt = def_opt

  def XMLin(self, content, options={}):
    self.handle_options('in', options)
    self.build_tree(content)

  def build_tree(self, content):
    parseString(content, self)

  def handle_options(self, dirn, options):
    known_opt = {}
    if dirn == 'in':
      for key in KnownOptIn:
        known_opt[key] = key
    else:
      for key in KnownOptOut:
        known_opt[key] = key
    
    row_opt = options
    self.opt = {}

    for key, val in row_opt:
      lkey = key.lower().replace('_', '')
      if key not in known_opt:
        raise KeyError('%s is not acceptable'  (key,))
      self.opt[lkey] = val

    # marge in options passed to constructor
    for key in known_opt:
      if not key in self.opt:
        if key in self.def_opt:
          self.opt[key] = self.def_opt[key]

    # set sensible defaults if not supplied
    if 'rootname' in self.opt:
      if not self.opt['rootname']:
        self.opt['rootname'] = '';
    else:
      self.opt['rootname'] = DefRootName
      
    if 'xmldecl' in self.opt and self.opt['xmldecl'] == '1':
      self.opt['xmldecl'] = DefXmlDecl
      
    if 'contentkey' in self.opt:
      m = re.match('^-(.*)$', self.opt['contentkey'])
      if m:
        self.opt['contentkey'] = m.group(1)
        self.opt['collapseagain'] = 1
    else:
      self.opt['contentkey'] = DefContentKey
      
    if not 'normalizespace' in self.opt:
      self.opt['normalizespace'] = 0

    # special cleanup for forcearray
    if 'forcearray' in self.opt:
      pass
    else:
      self.opt['forcearray'] = 0

    # special cleanup for keyattr
    if 'keyattr' in self.opt:
      if isinstance(self.opt['keyattr'], dict):
        # make a copy so we can mess with it
        self.keyattr = self.opt['keyattr']

        # Convert keyattr : {elem: '+attr'}
        # to keyattr : {elem: ['attr', '+']}
        for el in self.opt['keyattr']:
          m = re.match('^(\+|-)?(.*)$', self.opt['keyattr'][el])
          if m:
            self.opt['keyattr'][el] = [m.group(2), m.group(1)]
            if self.opt['forcearray'] == 1:
              continue
            if isinstance(self.opt['forcearray'], dict) and el in self.opt['forcearray']:
              continue
            if StrictMode and dirn == 'in':
              raise ValueError("<%s> set in KeyAttr but not in ForceArray" % (el,))
          else:
            del self.opt['keyattr'][el]
      elif isinstance(self.opt['keyattr'], list):
        self.keyattr = self.opt['keyattr']
      else:
        self.opt['keyattr'] = [ self.opt['keyattr']];
    else:
      if StrictMode:
        raise ValueError("No value specified for 'KeyAttr' option in call to XML%s()" % (dirn,))
      self.opt['keyattr'] = DefKeyAttr

    if 'valiables' in self.opt:
      self._var_values = self.opt['variables']
    elif 'varattr' in self.opt:
      self._var_values = {}

  def collapse(self, attr, tree):
    # start with the hash of attributes
    if 'noattr' in self.opt:
      attr = {}
    elif 'normalizespace' in self.opt and self.opt['normalizespace'] == 2:
      for key, val in attr.items():
        attr[key] = self.normalize_space(val)

    for key, val in zip(tree[::2],tree[1::2]):
      if isinstance(val, list):
        val = self.collapse(val[0], val[1:])
        if not val and 'suppressempty' in self.opt:
          continue
      elif key == '0':
        if re.match('^\s*$', val): # skip all whitespace content
          continue
        
        # do variable substitutions
        if hasattr(self, '_var_values'):
          re.sub('\$\{(\w+)\}', lambda match: self.get_var(match.group(1)))
          
        # look for variable definitions
        if 'varattr' in self.opt:
          var = self.opt['varattr']
          if attr.has_key(var):
            self.set_var(attr[var], val)
            
        # collapse text content in element with no attributes to a string
        if not len(attr) and val == tree[-1]:
          return { self.opt['contentkey'] : val } if 'forcecontent' in self.opt else val
        key = self.opt['contentkey']

      # combine duplicate attributes
      if attr.has_key(key):
        if isinstance(attr[key], list):
          attr[key].append(val)
        else:
          attr[key] = [attr[key], val]
      elif val and isinstance(val, list):
        attr[key] = [val]
      else:
        if 'contentkey' in self.opt and key != self.opt['contentkey'] and \
              (self.opt['forcearray'] == 1 or \
                 (isinstance(self.opt['forcearray'], dict) and key in self.opt['forcearray'])):
            attr[key] = [val]
        else:
          attr[key] = val

    # turn array into hash if key fields present
    if self.opt.has_key('keyattr'):
      for key, val in attr.items():
        if val and isinstance(val, list):
          attr[key] = self.array_to_hash(key, val)

    # disintermediate grouped tags
    if self.opt.has_key('grouptags'):
      for key, val in attr.items():
        if not (isinstance(val, dict) and len(val) == 1):
          continue
        if not self.opt['grouptags'].has_key(key):
          continue
        child_key, child_val = val.popitem()
        if self.opt['grouptags'][key] == child_key:
          attr[key] = child_val

    # fold hashes containing a single anonymous array up into just the array
    count = len(attr)
    if count == 1 and attr.has_key('anon') and isinstance(attr['anon'], list):
      return attr['anon']

    # do the right thing if hash is empty otherwise just return it
    if not len(attr) and self.opt.has_key('suppressempty'):
      if self.opt['suppressempty'] == '':
        return ''
      return None

    # roll up named elements with named nested 'value' attributes
    if self.opt.has_key('valueattr'):
      for key, val in attr.items():
        if not self.opt['valueattr'].has_key(key):
          continue
        if not (isinstance(val, dict) and len(val) == 1):
          continue
        k = val.keys()[0]
        if not k == self.opt['valueattr'][key]:
          continue
        attr[key] = val[key]

    return attr


  def normalize_space(self, text):
    text = re.sub('\s\s+', ' ', text.strip())
    return text

  # helper routine for collapse
  # attempt to 'fold' an array of hashes into an hash
  def array_to_hash(self, name, array):
    hash = {}

    # handle keyattr => {...}
    if isinstance(self.opt['keyattr'], dict):
      if not name in self.opt['keyattr']:
        return array
      (key, flag) = self.opt['keyattr'][name]
      for item in array:
        if isinstance(item, dict) and key in item:
          val = item[key]
          if isinstance(val, list) or isinstance(val, dict):
            if StrictMode:
              raise ValueError("<%s> element has non-scalar '%s' key attribute" % (name, key))
            warnings.warn("Warning: <%s> element has non-scalar '%s' key attribute" % (name, key))
            return array
          if self.opt['normalizespace'] == 1:
            val = self.normalize_space(val)
          hash[val] = item
          if flag == '-':
            hash[val]['-%s' % (key,)] = hash[val][key]
          if flag != '+':
            del hash[val][key]
        else:
          if StrictMode:
            raise ValueError('<%s> element has no %s key attribute' % (name, key))
          warnings.warn("Warning: <%s> element has no '%s' key attribute" % (name, key))
          return array
    # or assume keyattr => [...]
    else:
      for item in array:
        next = False
        if not isinstance(item, dict):
          return array
        for key in self.opt['keyattr']:
          if key in item:
            val = item[key]
            if isinstance(val, dict) or isinstance(val, list):
              return array
            if 'normalizespace' in self.opt and self.opt['normalizespace'] == 1:
              val = self.normalize_space(val)
            hash[val] = item
            del hash[val][key]
            next = True
            break
        if next:
          continue
        return array

    # collapse any hashes which now only have a content key
    if 'collapseagain' in self.opt:
      hash = self.collapse_content(hash)

    return hash

  def collapse_content(self, hash):
    contentkey = self.opt['contentkey']

    # first go through the values, checking that they are fit to collapse
    for val in hash.values():
      if not (isinstance(val, dict) and len(val) == 1 and contentkey in val):
        return hash

    # now collapse them
    for key in hash:
      hash[key] = hash[key][contentkey]

    return hash
      
      
  #
  # following methods overwrite ContentHandler
  #
  
  def startDocument(self):
    self.lists = []
    self.curlist = self.tree = []

  def startElement(self, name, attrs):
    attributes = {}
    for attr in attrs.items():
      attributes[attr[0]] = attr[1]
    newlist = [attributes]
    self.curlist.extend([name, newlist])
    self.lists.append(self.curlist)
    self.curlist = newlist

  def characters(self, content):
    text = content
    pos = len(self.curlist) - 1

    if pos > 0 and self.curlist[pos - 1] == '0':
      self.curlist[pos] += text
    else:
      self.curlist.extend(['0', text])

  def endElement(self, name):
    self.curlist = self.lists.pop()

  def endDocument(self):
    del self.curlist
    del self.lists
    tree = self.tree
    del self.tree

    if 'keeproot' in self.opt:
      tree = self.collapse({}, tree)
    else:
      tree = self.collapse(tree[1][0], tree[1][1:])
    self.tree = tree

if __name__ == '__main__':
#   opt = XMLin('''
#     <opt> 
#       <item key="item1" attr1="value1" attr2="value2" />
#       <item key="item2" attr1="value3" attr2="value4" />
#     </opt>
#     ''', {'contentkey':'-content'})

  xml = '''
    <opt>
      <car license="LW1804" make="GM"   id="2">
        <option key="1" pn="9926543-1167" desc="Steering Wheel"/>
      </car>
    </opt>
    '''
  opt = XMLin(xml, {'keyattr':{'car':'license', 'option':'pn'}, 'contentkey':'-content'})
  print opt
  

