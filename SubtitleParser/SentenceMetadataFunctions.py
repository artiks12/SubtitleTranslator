import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.CustomTokenizer import CustomToken
import SubtitleParser.Configurations.Constants as Constants
import re
from SubtitleParser.TaggedTextTokenizer import TaggedToken
from SubtitleParser.SubtitleElementTokenizer import SubtitleElement

class Sentence():
    pass

class SentenceMetadataFunctions():
    def __needSpaceForEllipses(self,currentType):
        if currentType == Constants.PUNCT_IN or currentType == Constants.PUNCT_RIGHT: return False
        if currentType == Constants.PUNCT_OUT or currentType == Constants.PUNCT_LEFT: return True

    def __getEllipseStringsForMetadata(
            self,
            ellipses:dict
            ):
        result = {}
        lastKey = None
        lastType = None
        keyToAdd = None
        ellipseString = ''
        for key in ellipses.keys():
            value = ellipses[key]
            if lastKey == None:
                if value[0] == Constants.PUNCT_OUT or value[0] == Constants.PUNCT_LEFT:
                    ellipseString = ' '
                ellipseString += value[1]
                keyToAdd = key
            else:
                if lastKey + 1 == key:
                    if self.__needSpaceForEllipses(value[0]):
                        ellipseString += ' '
                    ellipseString += value[1]
                else:
                    if lastType == Constants.PUNCT_OUT or lastType == Constants.PUNCT_RIGHT:
                        ellipseString += ' '
                    result[keyToAdd] = [ellipseString]
                    if value[0] == Constants.PUNCT_OUT or value[0] == Constants.PUNCT_LEFT:
                        ellipseString = ' '
                    ellipseString += value[1]
                    keyToAdd = key
            lastKey = key
            lastType = value[0]

        if len(ellipseString)>0:
            result[keyToAdd] = [ellipseString]
              
        return result

    def __getEllipsesForMetadata(
            self,
            sentence: list[CustomToken],
            parts: list,
            ):
        ellipses = {}
        lastEllipse = None
        lastPosition = None
        for i in range(len(sentence)):
            elem = sentence[i]
            part = parts[elem.id]
            if re.match(r'(…|\.\.+|--+|––+)',elem.value):
                ellipses[elem.id] = [part.subType,part.value]
                lastEllipse = elem.id
                lastPosition = i
        
        if not(lastEllipse == None):
            if lastEllipse == sentence[-1].id:
                ellipses.pop(lastEllipse)
            else:
                for i in range(lastPosition+1,len(sentence)):
                    if sentence[i].upos == 'PUNCT':
                        ellipses.pop(lastEllipse)
                    break
        
        return ellipses
    
    def __getDivisionParts(self,ellipses,sentence):
        result = []
        phraseRange = []
        Id = 0
        for token in sentence:
            if token.id in ellipses.keys():
                if len(phraseRange) > 0:
                    result.append(phraseRange)
                    phraseRange = []
            else:
                phraseRange.append(token.id)
            Id += 1
        if len(phraseRange) > 0:
            result.append(phraseRange)
        return result
    
    # Method to get single sentence metadata.
    def GetSentenceMetadata(
            self,
            sentence,
            parts
        ):
        ellipses = self.__getEllipsesForMetadata(sentence,parts)
        textWithEllipses = [item.id for item in sentence]
        textWithoutEllipses = []
        for token in sentence:
            if not(token.id in ellipses):
                textWithoutEllipses.append(token.id)

        divisionParts = self.__getDivisionParts(ellipses,sentence)
        
        metadata = {
            'textWithEllipses': textWithEllipses,
            'textWithoutEllipses':textWithoutEllipses,
            'ellipses':list(ellipses.items()),
            'divisionParts':divisionParts,
            'ellipseStrings':self.__getEllipseStringsForMetadata(ellipses)
        }

        return metadata
    
    def GetSentenceTextWithoutEllipses(
            self,
            sentence,
            parts
        ):
        ellipses = self.__getEllipsesForMetadata(sentence,parts)
        textWithoutEllipses = []
        for token in sentence:
            if not(token.id in ellipses):
                textWithoutEllipses.append(token.id)

        return (textWithoutEllipses,ellipses)
    
    def FixParts(self,parts,tokens,sentenceEnds = [],toIgnore = []):
        captionId = None
        elementId = 0
        partId = 0
        tokenId = 0
        result = []
        ends = []
        partValue = ''
        tokenValue = ''
        while partId < len(parts) or tokenId < len(tokens):
            if not(captionId == parts[partId].GetCaption()):
                elementId = 0
            captionId = parts[partId].GetCaption()
            if parts[partId].subType in Constants.nonSymbols:
                result.append(parts[partId].copy(newId=str(captionId)+'-'+str(elementId)))
                partId += 1
            elif partId in toIgnore:
                result.append(parts[partId].copy(newId=str(captionId)+'-'+str(elementId)))
                partId += 1
            else:
                partValue += parts[partId].value
                tokenValue += tokens[tokenId]
                if not(partValue == tokenValue):
                    start = parts[partId].start
                    start_char = parts[partId].start_char
                    while not(len(partValue) == len(tokenValue)):
                        if len(partValue) > len(tokenValue):
                            token = TaggedToken(tokens[tokenId],start,start+len(tokens[tokenId]),
                                                'X',start_char,start_char+len(tokens[tokenId]))
                            result.append(SubtitleElement(token,parts[partId].subType,str(captionId)+'-'+str(elementId)))
                            elementId += 1
                            start += len(tokens[tokenId])
                            start_char += len(tokens[tokenId])
                            if len(partValue) == len(tokenValue): break
                            tokenId += 1
                            tokenValue += tokens[tokenId]
                        else:
                            if len(partValue) == len(tokenValue): break
                            partId += 1
                            partValue += parts[partId].value
                    token = TaggedToken(tokens[tokenId],start,start+len(tokens[tokenId]),
                                        'X',start_char,start_char+len(tokens[tokenId]))
                    result.append(SubtitleElement(token,parts[partId].subType,str(captionId)+'-'+str(elementId)))
                else:
                    result.append(parts[partId].copy(newId=str(captionId)+'-'+str(elementId)))
                if tokenId in sentenceEnds:
                    ends.append(len(result)-1)
                partValue = ''
                tokenValue = ''
                partId += 1
                tokenId += 1
            elementId += 1
        if len(sentenceEnds) > 0:
            return (result,ends)
        return result