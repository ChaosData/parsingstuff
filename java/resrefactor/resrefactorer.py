#!/usr/local/bin/jython

import sys
import xmltodict
sys.path.append('/home/jtd/java/javaparser-core-2.0.0.jar')

from com.github.javaparser.ast.expr import IntegerLiteralExpr

#iddict = {}
#striddict = {}


def fixtilde(argv):
  tildeswap = []
  for arg in argv:
    if arg.startswith('~/'):
      tildeswap.append(1)
    else:
      tildeswap.append(0)
  if sum(tildeswap) > 0:
    import subprocess
    id = subprocess.Popen('id', stdout=subprocess.PIPE)
    uname = id.communicate()[0].split(')')[0].split('(')[1]
    homedir = ''
    with open('/etc/passwd') as fd:
      for line in fd:
        if line.startswith(uname + ':'):
          homedir = line.split(':')[5]
    retargv = []
    for i in range(len(tildeswap)):
      if tildeswap[i] == 1:
        retargv.append(homedir + argv[i][1:])
      else:
        retargv.append(argv[i])
    return retargv
  else:
    return argv

'''
argv = fixtilde(sys.argv)
decpath = argv[1]
respath = argv[2]

publicxml = None
with open(respath + '/public.xml') as fd:
  publicxml = xmltodict.parse(fd.read()) 

stringsxml = None
with open(respath + '/strings.xml') as fd:
  stringsxml = xmltodict.parse(fd.read()) 
'''

import collections

def stringify(s):
  return s.replace('\r\n','\n').replace('\n', '\\n')

def commentify(s):
  return '"' + stringify(s) + '"'


context_things =  [ "Context", "ContextWrapper", "MockContext", "AbstractInputMethodService", "AccessibilityService",
                    "AccountAuthenticatorActivity", "ActionBarActivity", "Activity", "ActivityGroup", "AliasActivity",
                    "Application", "BackupAgent", "BackupAgentHelper", "CarrierMessagingService", "ContextThemeWrapper",
                    "DreamService", "ExpandableListActivity", "FragmentActivity", "HostApduService", "InputMethodService",
                    "IntentService", "IsolatedContext", "JobService", "LauncherActivity", "ListActivity",
                    "MediaBrowserService", "MediaRouteProviderService", "MockApplication", "MultiDexApplication",
                    "MutableContextWrapper", "NativeActivity", "NotificationCompatSideChannelService",
                    "NotificationListenerService", "OffHostApduService", "PreferenceActivity", "PrintService",
                    "RecognitionService", "RemoteViewsService", "RenamingDelegatingContext", "Service",
                    "SettingInjectorService", "SpellCheckerService", "TabActivity", "TestActivity", "TextToSpeechService",
                    "TvInputService", "VoiceInteractionService", "VoiceInteractionSessionService", "VpnService",
                    "WallpaperService" ]


'''
b = 0
for element in publicxml['resources']['public']:
  if isinstance(publicxml['resources']['public'], collections.OrderedDict):
    element = publicxml['resources']['public']
    b = 1
  if element['@type'] == u'string':
    iddict[element['@id']] = { 'name': element['@name']}
  if b == 1:
    break

b = 0
for element in stringsxml['resources']['string']:
  if isinstance(stringsxml['resources']['string'], collections.OrderedDict):
    element = stringsxml['resources']['string']
    b = 1
  if '#text' in element:
    striddict[element['@name']] = element['#text']
  else:
    striddict[element['@name']] = xmltodict.unparse(element, full_document=False).split('</@name>')[1]
  if b == 1:
    break

for id in iddict.keys():
  if iddict[id]['name'] in striddict:
    iddict[id]['#text'] = striddict[ iddict[id]['name'] ]
  else:
    sys.stderr.write("MISSING ID. id: " + id + " name: " + iddict[id]['name'] + "\n")
'''

import com.github.javaparser.ASTHelper
import com.github.javaparser.ast.CompilationUnit
import com.github.javaparser.ast.body.AnnotationDeclaration
import com.github.javaparser.ast.comments.BlockComment
import com.github.javaparser.ast.expr.AnnotationExpr
import com.github.javaparser.ast.stmt.AssertStmt
import com.github.javaparser.ast.type.ClassOrInterfaceType
import com.github.javaparser.ast.visitor.CloneVisitor

class MethodCallVisitor(com.github.javaparser.ast.visitor.ModifierVisitorAdapter):
  def resToString(self, res):
    i = None
    try:
      i = int(res, 10)
    except:
      try:
        i = int(res, 16)
      except:
        pass
    if i == None:
      return None
    hexi = hex(i)
    if hexi in self.iddict and '#text' in self.iddict[hexi]:
      return self.iddict[hexi]['#text']
    return None


  def __init__(self, respath):
    self.publicxml = None
    with open(respath + '/public.xml') as fd:
      self.publicxml = xmltodict.parse(fd.read()) 

    self.stringsxml = None
    with open(respath + '/strings.xml') as fd:
      self.stringsxml = xmltodict.parse(fd.read()) 
    self.iddict = {}
    self.striddict = {}
    b = 0
    for element in self.publicxml['resources']['public']:
      if isinstance(self.publicxml['resources']['public'], collections.OrderedDict):
        element = self.publicxml['resources']['public']
        b = 1
      if element['@type'] == u'string':
        self.iddict[element['@id']] = { 'name': element['@name']}
      if b == 1:
        break

    b = 0
    for element in self.stringsxml['resources']['string']:
      if isinstance(self.stringsxml['resources']['string'], collections.OrderedDict):
        element = self.stringsxml['resources']['string']
        b = 1
      if '#text' in element:
        self.striddict[element['@name']] = element['#text']
      else:
        self.striddict[element['@name']] = xmltodict.unparse(element, full_document=False).split('</@name>')[1]
      if b == 1:
        break

    for id in self.iddict.keys():
      if not id in self.iddict:
        print "missing id: " + str(id)
        continue
      if self.iddict[id]['name'] in self.striddict:
        self.iddict[id]['#text'] = self.striddict[ self.iddict[id]['name'] ]
      else:
        sys.stderr.write("MISSING ID. id: " + id + " name: " + self.iddict[id]['name'] + "\n")
    

    pass
  def visit(self, n, object):
    if not isinstance(n, com.github.javaparser.ast.expr.MethodCallExpr):
      if isinstance(n, com.github.javaparser.ast.body.Parameter):
       return
      return com.github.javaparser.ast.visitor.ModifierVisitorAdapter.visit(self, n, object)
    if n.getName() == "getString":
      found = False
      if str(n.getScope()) in ["this", "context", "", "None"]:
        from com.github.javaparser.ast.body import MethodDeclaration, ClassOrInterfaceDeclaration
        from com.github.javaparser.ast import CompilationUnit
        p = n.getParentNode()
        while not isinstance(p, CompilationUnit):
          if isinstance(p, MethodDeclaration):
            if p.getName() == "getString":
              return n
          elif isinstance(p, ClassOrInterfaceDeclaration):
             for extend in p.getExtends():
               if str(extend) in context_things:
                 found = True
                 break
          p = p.getParentNode()
      c = n.getChildrenNodes()
      if len(c) in [1,2] and isinstance(c[-1], IntegerLiteralExpr):
        res = c[-1].getValue()
        s = self.resToString(res)
        if s != None:
          if found:
            from com.github.javaparser.ast.expr import StringLiteralExpr
            snode = StringLiteralExpr()
            snode.setValue(stringify(s))
            return snode
          else:
            from com.github.javaparser.ast.comments import BlockComment
            n.setComment(BlockComment("? " + commentify(s) + " ?"))
            return n
    elif n.getName() == "makeText" and str(n.getScope()) == 'Toast':
      ncns = n.getChildrenNodes()
      if len(ncns) == 4:
        if isinstance(ncns[2], IntegerLiteralExpr):
          res = ncns[2].getValue()
          s = self.resToString(res)
          if s != None:
            from com.github.javaparser.ast.expr import StringLiteralExpr
            snode = StringLiteralExpr()
            snode.setValue(stringify(s))
            newargs = [ncns[0], ncns[1], snode, ncns[3]]
            n.setArgs(newargs)
            return n

    return com.github.javaparser.ast.visitor.ModifierVisitorAdapter.visit(self, n, object)





def main():
  if len(sys.argv) != 3:
    sys.stderr.write('usage: ' + sys.argv[0] + ' <decompiled Java file> <path/to/res/values(-XX)>\n')
    sys.exit(1)

  argv = fixtilde(sys.argv)
  decpath = argv[1]
  respath = argv[2]

  cu = None
  with open(decpath, 'r') as fd:
    cu = com.github.javaparser.JavaParser.parse(fd)

  if (cu == None):
    sys.exit(1)

  print type(cu)

  print cu
  print "======================"
  cu2 = MethodCallVisitor(respath).visit(cu, None)
  print cu2
  


if __name__ == '__main__':
  main()

