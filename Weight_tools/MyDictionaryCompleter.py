#===============================================================================
# MyDictionaryCompleter
#===============================================================================
from PyQt5 import QtGui, QtCore, QtWidgets
class MyDictionaryCompleter(QtWidgets.QCompleter):
#|-----------------------------------------------------------------------------|
# class Variables
#|-----------------------------------------------------------------------------| 
    insertText = QtCore.pyqtSignal(str)
    #no classVariables
#|-----------------------------------------------------------------------------|
# Constructor  
#|-----------------------------------------------------------------------------|
    def __init__(self, myKeywords=None,parent=None):


        myKeywords =['apple','aggresive','ball','bat','cat','cycle','dog','dumb',\
                     'elephant','engineer','food','file','good','great',\
                     'hippopotamus','hyper','india','ireland','just','just',\
                     'key','kid','lemon','lead','mute','magic',\
                     'news','newyork','orange','oval','parrot','patriot',\
                     'question','queue','right','rest','smile','simple',\
                     'tree','urban','very','wood','xylophone','yellow',\
                     'zebra']
        QtGui.QCompleter.__init__(self, myKeywords, parent)
        self.connect(self,
            QtCore.SIGNAL("activated(const QString&)"), self.changeCompletion)
#|--------------------------End of Constructor---------------------------------| 
#|-----------------------------------------------------------------------------| 
# changeCompletion
#|-----------------------------------------------------------------------------|
    def changeCompletion(self, completion):
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        print(completion)
        self.insertText.emit(completion)
#|-----------------------End of changeCompletion-------------------------------|