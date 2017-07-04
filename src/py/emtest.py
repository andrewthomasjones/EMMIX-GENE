#!C:/Python21/python.exe

# Jigger path
import sys
sys.path.append("../bin/lib")
sys.path.append("../DLLs")

import unittest
import EmmixProcessManager
import MessageStore

class EPMTest(unittest.TestCase):

    def testToolhelp(self):
        listToCheck = ['PYTHON.EXE']
        exes = EmmixProcessManager.listExes(listToCheck)
        self.assertEqual(exes[0], listToCheck[0])
        
    def testSpawn(self):
        try:
            os.remove('epmtestout.txt')
        except:
            pass
        EmmixProcessManager.spawn(None, None, "epmtest.exe < epmtestin.txt")
        result=open('epmtestout.txt','r').read()
        expected=open('epmtestin.txt','r').read()
        self.assertEqual(result, expected)
        
    def testSpawn2(self):
        try:
            os.remove('epmtestout.txt')
        except:
            pass
        EmmixProcessManager.spawn(None, None, "epmtest.exe popen3 < epmtestin2.txt")

class MStoreTest(unittest.TestCase):

    def testNonBlockMessageBox(self):
        MessageStore.NonBlockingMessageBox(0, "Unit Test","Title")
        
#class EmmixTest(unittest.TestCase):
#
#    def testEmmixT(self):
#        os.popen('../emmix-t.exe  
    
if __name__ == '__main__':
    unittest.main(defaultTest="EPMTest.testSpawn2")
