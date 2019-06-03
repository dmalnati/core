from libWeb import *

    
#
# Mimic php-like behavior.
#
# <? ... ?>
#
# Code between the tags executes like handler code.
#
# Content outside the tags are passed through untouched.
#
class PythonPageFileHandler(WebRequestHandler):
    def initialize(self, **name__value):
        self.webRoot = name__value["path"]
        self.db      = name__value["db"]
    
    def get(self, *argList):
        fileToGet = self.webRoot + "/" + argList[0]

        # Pull the sourc file
        fd = open(fileToGet)
        buf = fd.read()
        fd.close()
        
        strLen = len(buf)
        
        # having to encode everything is labor, so temporarily replace the
        # functionality with a handier version
        writeTmp = self.write
        
        def Write(strToPrint):
            writeTmp(str(strToPrint).encode())

        self.write = Write
        
        # for exec, pass in context from this world, namely 'self'
        context = dict(self=self)
        
        # walk through file contents and look for executable sections.
        # Those sections can behave as if they're part of this handler.
        idx = 0
        cont = True
        while cont:
            # look for data leading up to first tag
            # then get the stuff between tags
            # repeat
            idxTagStart = buf.find("<?", idx)
            if idxTagStart != -1:
                idxTagEnd = buf.find("?>", idxTagStart)
                
                if idxTagEnd != -1:
                    rawOutput = buf[idx:idxTagStart]
                    dynOutput = buf[idxTagStart + 2:idxTagEnd]
                    
                    idx = idxTagEnd + 2
                    
                    self.write(rawOutput)
                    #exec(dynOutput, context)
                    # hmm, dropped context, couldn't access trivial things like
                    # the Commas function.
                    # Be safe in there.
                    exec(dynOutput)
                    
                else:
                    # that's not good -- author missed the close tag somehow
                    cont = False
            else:
                cont = False
        
        
            if idx >= strLen:
                cont = False
                
        if idx != strLen:
            self.write(buf[idx:])
        
        # restore prior meaning of the write function
        self.write = writeTmp
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    