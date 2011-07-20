# Python script for additional style validation
# Author: Rintze M. Zelle
# Requires lxml library (http://lxml.de/)
# Checks
# - whether ".csl" files conform to naming scheme [a-z0-9] with optional single
#   hyphen delimiters
# - whether style ID (content of cs:id) matches the URI generated by the Zotero
#   Style Repository:
#   "http://www.zotero.org/styles/" + filename - extension
# - whether "self" link (value of "href" on cs:link with rel="self") matches the
#   Zotero Style Repository
# - for independent styles, whether "template" link (value of "href" on cs:link
#   with rel="template") points to the Zotero Style Repository style URI of an
#   independent style.
# - for dependent styles, whether "independent-parent" link (value of "href" on
#   cs:link with rel="template") points to the Zotero Style Repository style URI
#   of an independent style.

import os, glob, re
from lxml import etree

path = 'C:\Users\Rintze Zelle\Documents\git\styles\\'

def parseStyle(stylePath):
    style = etree.parse(stylePath)
    styleElement = style.getroot()
    metadata = {}
    try:
        metadata["id"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}id").text
        metadata["selfLink"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='self']").attrib.get("href")
    except:
        pass
    try:
        metadata["template"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='template']").attrib.get("href")
    except:
        pass
    try:
        metadata["independentParent"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='independent-parent']").attrib.get("href")
    except:
        pass
    return(metadata)

def checkFileName(fileName):
    if not(re.match("[a-z0-9](-?[a-z0-9]+)*(.csl)", fileName)):
        print("Non-conforming filename: " + fileName)

metadataList = []
metadata = {}
for independentStyle in glob.glob( os.path.join(path, '*.csl') ):
    fileName = os.path.basename(independentStyle)

    checkFileName(fileName)
    
    metadata = parseStyle(independentStyle)
    metadata["fileName"] = fileName

    try:
        if not(("http://www.zotero.org/styles/"+fileName) == (metadata["selfLink"]+".csl")):
            print("Name Mismatch - Filename & Style URI (value 'href' on cs:link[@rel=self]): " + fileName)
    except:
        print("Missing Style URI (value 'href' on cs:link[@rel=self]): " + fileName)
    try:
        if not(("http://www.zotero.org/styles/"+fileName) == (metadata["id"]+".csl")):
            print("Name Mismatch - Filename & Style ID (content cs:id): " + fileName)
    except:
        print("Missing Style ID (content cs:id): " + fileName)
    
    metadataList.append(metadata)

for queryMetadataDict in metadataList:
    match = True
    try:
        if(queryMetadataDict["template"]):
            match = False
            for metadataDict in metadataList:
                if(queryMetadataDict["template"] == metadataDict["selfLink"]):
                    match = True
            if(match == False):
                print("Non-existing Style Template URI (value 'href' on cs:link[@rel=template]): " + queryMetadataDict["fileName"])
    except:
        pass

metadataListDependents = []
metadataDependents = {}
for dependentStyle in glob.glob( os.path.join(path, "dependent", '*.csl') ):
    fileName = os.path.basename(dependentStyle)
    
    checkFileName(fileName)

    metadataDependents = parseStyle(dependentStyle)
    metadataDependents["fileName"] = fileName
    
    try:
        if not(("http://www.zotero.org/styles/"+fileName) == (metadataDependents["selfLink"]+".csl")):
            print("Name Mismatch - Filename & Style URI (value 'href' on cs:link[@rel=self]): (dependent) " + fileName)
    except:
        pass
    try:
        if not(("http://www.zotero.org/styles/"+fileName) == (metadataDependents["id"]+".csl")):
            print("Name Mismatch - Filename & Style ID (content cs:id): (dependent) " + fileName)
    except:
        print("Missing Style ID (content cs:id): (dependent) " + fileName)
    try:
        metadataDependents["independentParent"]
    except:
        print("Missing Parent Style ID value 'href' on cs:link[@rel=independent-parent]): (dependent) " + fileName)

    metadataListDependents.append(metadataDependents)

for queryMetadataDict in metadataListDependents:
    match = True
    try:
        if(queryMetadataDict["independentParent"]):
            match = False
            for metadataDict in metadataList:
                if(queryMetadataDict["independentParent"] == metadataDict["selfLink"]):
                    match = True
            if(match == False):
                print("Non-existing Parent Style URI (value 'href' on cs:link[@rel=independent-parent]): (dependent) " + queryMetadataDict["fileName"])
    except:
        pass
