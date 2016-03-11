#!/usr/bin/python

################################
##
##  mergeSafBookmarks
##  A tool to merge Safari Bookmarks
##
#############################################################


## Setup our variables

import sys, getopt, re, os, os.path, string, types, datetime, time
import logging, logging.handlers, plistlib, shutil, subprocess

######################### START FUNCTIONS ###############################

def helpMessage():
    print '''mergeSafBookmarks: A tool to merge Safari Bookmarks
     
Syntax: 
    mergeSafBookmarks -i newbookmarkfile -f bookmarkfile
    
Flags: 
    -i newbookmarks    -- path to imported bookmarks file
    -f bookmarkfile    -- path to master bookmarks file
    -v                 -- Print out version info.
     '''


def mergeBookmarkList(list,importList):
    '''function to merge two bookmark lists into a single list'''
    newList = []
    newCount = 1
    for bookmark in importList:
        bookmarkFound = False
        for existingBookmark in list:
            try:
                if bookmark["WebBookmarkType"] == "WebBookmarkTypeList":
                        if (bookmark["Title"] == existingBookmark["Title"]
                        and existingBookmark["WebBookmarkType"] == "WebBookmarkTypeList"):
                            print "mergeBookmarkList() merging bookmark list with title: %s" % bookmark["Title"]
                            mergedBookmarks = mergeBookmarkList(bookmark["Children"],existingBookmark["Children"])
                            existingBookmark["Children"] = mergedBookmarks
                            bookmarkFound = True                       
                else:
                    ##print "here for bookmark:%s, existing bookmark:%s" % (bookmark['URLString'],existingBookmark['URLString'])
                    if existingBookmark['URLString'] == bookmark['URLString']:
                        bookmarkFound = True
            except:
                pass
                
        if not bookmarkFound:
            try:
                if bookmark["WebBookmarkType"] == "WebBookmarkTypeList":
                    print "Adding new bookmark list: #%s Title:%s" % (newCount, bookmark["Title"])
                elif bookmark["WebBookmarkType"] == "WebBookmarkTypeLeaf":
                    print "Adding new bookmark: #%s URL:%s" % (newCount, bookmark["URLString"])
                else:
                    print "Adding new bookmark: #%s Type:%s" % (newCount, bookmark["WebBookmarkType"])
            except:
                print "Adding unknown existing bookmark: #%s" % newCount
            newList.append(bookmark)
            newCount += 1
                
    ## next iterate through all existingBookmarks and add them to our new list
    count = 1
    for existingBookmark in list:
        """
        try:
            if bookmark["WebBookmarkType"] == "WebBookmarkTypeList":
                print "Adding existing bookmark list: #%s Title:%s" % (count, existingBookmark["Title"])
            elif bookmark["WebBookmarkType"] == "WebBookmarkTypeLeaf":
                print "Adding existing bookmark: #%s URL:%s" % (count, existingBookmark["URLString"])
            else:
                print "Adding existing bookmark: #%s Type:%s" % (count, existingBookmark["WebBookmarkType"])
        except:
            print "Adding unknown existing bookmark: #%s" % count
        """
        count += 1
        newList.append(existingBookmark)
            
    print "mergeBookmarkList() Item count: ExistingList:%s ImportList:%s NewList:%s" % (len(list),len(importList),len(newList))

    return newList

######################### END FUNCTIONS #################################


######################### MAIN SCRIPT START #############################


importfile=""
file=""
backupFile = True
version="0.1"
build="2009121105"


## initialize our lists
importBookMarksBarData = []
importBookMarksMenuData = []
fileBookMarksBarData = []
fileBookMarksMenuData = []
newFileBookMarksBarData = []
newFileBookMarksMenuData = []


## Get our flags
try:
    optlist, list = getopt.getopt(sys.argv[1:],':vi:f::')
except getopt.GetoptError:
    print "Syntax Error!"
    helpMessage()
    sys.exit(1)
    
for opt in optlist:
    if opt[0] == '-i':
        if (os.path.isfile(opt[1])):
            importfile = opt[1]
        else:
            print "InFile does not exist at path: '%s'" % opt[1]
            sys.exit(2)
    if opt[0] == '-f':
        if (os.path.isfile(opt[1])):
            file  = opt[1]
        else:
            print "File does not exist at path: '%s'" % opt[1]
            sys.exit(2)
    if opt[0] == '-v':
        print "mergeSafBookmarks version %s build %s\n Written by Beau Hunter\n" % (version,build)
        sys.exit(0)

if not importfile or not file:
    print "Syntax Error!"
    helpMessage()
    sys.exit(1)

## convert our file to XML formatted plist
subprocess.call("/usr/bin/plutil -convert xml1 '%s'" % file,shell=True,universal_newlines=True)

## Read in our files plist data
importFileData = plistlib.readPlist(importfile)
fileData = plistlib.readPlist(file)



## Create our new data vars
try:
    importBookMarksBarData = importFileData["Children"][1]["Children"]
except:
    pass
try:
    importBookMarksMenuData = importFileData["Children"][2]["Children"]
except:
    pass

try:
    fileBookMarksBarData = fileData["Children"][1]["Children"]
except:
    pass
try:
    fileBookMarksMenuData = fileData["Children"][2]["Children"]
except:
    pass
    
newFileBookMarksBarData = []
newFileBookMarksMenuData = []


## iterate through our bookmarks bar data, for each item, look for an associated
## item in our existing file
if importBookMarksBarData:
     newFileBookMarksBarData = mergeBookmarkList(fileBookMarksBarData, importBookMarksBarData)
else:
    newFileBookMarksBarData = fileBookMarksBarData

## iterate through our bookmarks menu data, for each item, look for an associated
## item in our existing file
if importBookMarksMenuData:
    newFileBookMarksMenuData = mergeBookmarkList(fileBookMarksMenuData,importBookMarksMenuData)
else:
    newFileBookMarksMenuData = fileBookMarksMenuData

## Take existing bookmark data, copy it, then replace our values
newFileData = fileData;
newFileData["Children"][1]["Children"] = newFileBookMarksBarData
newFileData["Children"][2]["Children"] = newFileBookMarksMenuData 

## backup the original file if we're supposed to
if backupFile:
    ## get the directory
    backupDir = os.path.dirname(file)
    backupFileName = "Bookmarks_bak"
    if os.path.exists(os.path.join(backupDir,"%s.plist" % backupFileName)):
        count = 1
        while os.path.exists("%s_%d.plist" % (backupFileName, count)):
            count+=1;
        backupFile = os.path.join(backupDir,"%s_%d.plist" % (backupFileName,count))
    else:
        backupFile = os.path.join(backupDir,"%s.plist" % backupFileName)
    
    shutil.copyfile(file,backupFile)
    
## debug data
existingBookmarkMenuCount = len(fileBookMarksMenuData)
existingBookmarkBarCount = len(fileBookMarksBarData)

newBookMarkBarCount = len(newFileBookMarksBarData)
newBookMarkMenuCount = len(newFileBookMarksMenuData)

print "Debug: Item count: Existing File(menu: %s bar: %s) New File(menu: %s bar: %s)" % (existingBookmarkMenuCount,existingBookmarkBarCount,newBookMarkMenuCount,newBookMarkBarCount)


plistlib.writePlist(newFileData,file)


