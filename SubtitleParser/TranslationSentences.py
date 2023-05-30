import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Sentences import Sentences
from SubtitleParser.Caption import Caption
from SubtitleParser.SubtitleElementTokenizer import SubtitleElement
import SubtitleParser.Configurations.Constants as Constants
import SubtitleParser.Translator as Translator
from SubtitleParser.SentenceMetadataFunctions import SentenceMetadataFunctions
from SubtitleParser.CustomTokenizer import CustomTokenizer
from SubtitleParser.TaggedTextTokenizer import TaggedTextTokenizer
from SubtitleParser.Alignment import GetAlignmentGroups, GetAlignmentOrders
from SubtitleParser.TextBreaker import TextBreaker
import re

class TranslationToken():
    pass

class TranslationSentences(Sentences):
    """
        TranslationSentences class.
        Inherits methods from Sentences class. Is used to send sentences
        to machine translation system.
    """
    def __init__(self, subtitle: Caption, SourceNLP, TargetNLP, PretokenizeNLP, multiple: bool = False) -> None:
        super().__init__(subtitle, SourceNLP, TargetNLP, PretokenizeNLP, multiple)
    
    # Method to get string from certain parts.
    def __getTextFromAlignments(self,parts,inclusiveParts):
        text = ''
        last = None
        spaces = ''
        for i in range(len(parts)):
            if i in inclusiveParts:
                if text == '': text += parts[i].value
                else:
                    spaces += ' ' * (parts[i].start-last)
                    text += spaces + parts[i].value
                    spaces = ''
            elif len(text) > 0:
                if parts[i].subType == Constants.PUNCT_IN:
                    spaces = ' '
                else:
                    spaces += ' ' * (parts[i].start-last)
            last = parts[i].end
        return text
    
    # Method to check if it is necessary to include elipses at the start or end of caption
    def __getCaptionBooleans(self, index, count):
        if index == count: return (False,True)
        if index == 1: return (True,False)
        return (False,False)
    
    # Method to check if it is necessary to include elipses at the start or end of caption
    def __getTextPartsFromCaptions(self):
        parts: list[SubtitleElement] = []
        position = 0
        index = 1
        for caption in self._captions:
            (needStart,needEnd) = self.__getCaptionBooleans(index,len(self._captions))
            tempParts = caption.GetTextWithoutEllipses(needStart,needEnd)
            elemId = 0
            for part in tempParts:
                if not(part.subType == Constants.NEWLINE):
                    parts.append(part.copy(position+part.start,str(index-1)+'-'+str(elemId)))
                    elemId += 1
            position = parts[-1].end+1
            index += 1
        return parts
    
    # Method to get list with subtitle elements that are not styling tags.
    def __getTagglessParts(self,parts):
        taglessParts = []
        for i in range(len(parts)):
            if not(parts[i].subType in Constants.nonSymbols):
                taglessParts.append(i)
        return taglessParts
    
    # Method to get list with subtitle elements that are not styling tags divided by subtitles.
    def __getSubtitlePartsAndTags(self,parts):
        subtitleParts = []
        taglessParts = []
        openingTags = {}
        closingTags = {}
        temp = []
        lastElem = 0
        lastCaption = None
        tag = []
        for i in range(len(parts)):
            caption = int(parts[i].GetCaption())
            if not(parts[i].subType in Constants.nonSymbols):
                taglessParts.append(i)
                if len(temp)==0:
                    temp.append(i)
                else:
                    if lastCaption < caption:
                        subtitleParts.append(temp)
                        temp = []
                    temp.append(i)
                if len(tag)>0:
                    tag.sort(reverse=True)
                    openingTags[i] = tag
                    tag = []
                lastElem = i
            else:
                if parts[i].subType == Constants.TAG_CLOSE:
                    if lastElem not in closingTags.keys():
                        closingTags[lastElem] = []
                    closingTags[lastElem].append(i)
                else: 
                    tag.append(i)
            lastCaption = caption
            
        if len(temp)>0:
            subtitleParts.append(temp)
        
        return (taglessParts,subtitleParts,openingTags,closingTags)
    
    # Method to get sentences for translation.
    def GetSentences(self,hasAlignments):
        # Get all caption subtitle elements.
        parts: list[SubtitleElement] = self.__getTextPartsFromCaptions()

        # Get Tagless text and subtitle alignments as well as tag and align positions.
        taglessParts = self.__getTagglessParts(parts)
        
        # Get text in all captions as string.
        taglessText = self.__getTextFromAlignments(parts,taglessParts)

        # Get sentence metadata.
        tokenizer = CustomTokenizer(self.SourceNLP)
        tokenizer.Tokenize(taglessText)

        metadata = {
            'parts':parts,
            'sentences':[]
        }

        senMeta = SentenceMetadataFunctions()

        if not(len(taglessParts) == len(tokenizer.tokens)):
            parts = senMeta.FixParts(parts,tokenizer.GetTokenValues(tokenizer.tokens))

        # Don't get all metadata if MT uses alignments.
        if hasAlignments:
            taglessParts = self.__getTagglessParts(parts)
            tokenizer.GiveNewIds(taglessParts)
            metadata = {
                'parts':parts,
                'sentences':[],
                'ellipseIds':[]
            }
            for sentence in tokenizer.sentences:
                (textWithoutEllipses,ellipses) = senMeta.GetSentenceTextWithoutEllipses(sentence,parts)
                metadata['sentences'].append(self.__getTextFromAlignments(parts,textWithoutEllipses))
                metadata['ellipseIds'].extend(ellipses)
        else:
            (taglessParts,subtitleParts,openingTags,closingTags) = self.__getSubtitlePartsAndTags(parts)

            tokenizer.GiveNewIds(taglessParts)
            
            metadata['parts'] = parts
            metadata['ellipseIds'] = []
            metadata['openingTags'] = openingTags
            metadata['closingTags'] = closingTags
            metadata['textWithoutTags'] = taglessParts
            metadata['textWithoutEllipses'] = []
            metadata['ellipses'] = []
            metadata['subtitleTexts'] = subtitleParts
            metadata['divisionParts'] = []

            for sentence in tokenizer.sentences: 
                temp = senMeta.GetSentenceMetadata(sentence,parts)
                metadata['sentences'].append(self.__getTextFromAlignments(parts,temp['textWithoutEllipses']))
                metadata['textWithoutEllipses'].extend(temp['textWithoutEllipses'])
                metadata['divisionParts'].extend(temp['divisionParts'])
                metadata['ellipses'].extend(temp['ellipses'])

            metadata['ellipseIds'] = [item[0] for item in metadata['ellipses']]

        return metadata
    
    # Method to replace current subtitle parts with tokens used by MT system.
    def FixSubtitleParts(self,metadata):
        senMeta = SentenceMetadataFunctions()
        
        # Get all caption subtitle elements.
        (parts,ends) = senMeta.FixParts(metadata['parts'],list(metadata['sourceTokens'].values()),metadata['sentenceEnds'],metadata['ellipseIds'])

        # Get Tagless text and subtitle alignments as well as tag and align positions.
        taglessParts = self.__getTagglessParts(parts)
        
        # Get text in all captions as string.
        taglessText = ''
        for p in range(len(parts)):
            if p in taglessParts:
                if taglessText == '': taglessText += parts[p].value
                elif taglessText[-1] == '\n': taglessText += parts[p].value
                else: taglessText += ' ' + parts[p].value
                if p in ends: taglessText += '\n'

        taglessText = taglessText[:-1]

        tokenizer = CustomTokenizer(self.PretokenizeNLP)
        tokenizer.Tokenize(taglessText)
        
        (taglessParts,subtitleParts,openingTags,closingTags) = self.__getSubtitlePartsAndTags(parts)

        tokenizer.GiveNewIds(taglessParts)
        
        metadata['parts'] = parts
        metadata['openingTags'] = openingTags
        metadata['closingTags'] = closingTags
        metadata['textWithoutTags'] = taglessParts
        metadata['textWithoutEllipses'] = []
        metadata['ellipses'] = []
        metadata['subtitleTexts'] = subtitleParts
        metadata['divisionParts'] = []

        for sentence in tokenizer.sentences: 
            temp = senMeta.GetSentenceMetadata(sentence,parts)
            metadata['textWithoutEllipses'].extend(temp['textWithoutEllipses'])
            metadata['divisionParts'].extend(temp['divisionParts'])
            metadata['ellipses'].extend(temp['ellipses'])

        return metadata
    
    # Method to get new source tokens.
    def GetNewSourceTokens(self,metadata):
        newSourceTokens = {}
        ellipseId = 0
        oldTokenId = 0
        newTokens = {}
        ellipses = []
        for sT in range(len(metadata['textWithoutTags'])):
            tokenId = metadata['textWithoutTags'][sT]
            if tokenId not in metadata['textWithoutEllipses']:
                newSourceTokens[sT] = metadata['ellipses'][ellipseId][1][1]
                ellipses.append(sT)
            else:
                newSourceTokens[sT] = metadata['sourceTokens'][oldTokenId]
                newTokens[oldTokenId] = sT
                oldTokenId += 1
        return (newSourceTokens,newTokens,ellipses)
    
    # Method to get new token alignments.
    def __getNewAlignments(self,newSourceIds,newTargetIds,sourceAlignments,ellipses):
        newAlignments = {}
        for item in newSourceIds.items():
            temp = []
            for id in sourceAlignments[item[0]]:
                temp.append(newTargetIds[id])
            newAlignments[item[1]] = temp
        newAlignments = newAlignments | ellipses
        newAlignments = dict(sorted(newAlignments.items()))
        return newAlignments 
    
    # Method to update word alignment groups.
    def GetNewTokenAlignments(self,metadata,newTargetTokens,newTargetIds,newTargetEllipses,newTargetRanges):
        # Get new source tokens.
        (newSourceTokens,newSourceIds,newSourceEllipses) = self.GetNewSourceTokens(metadata)
        ellipsesSource = {}
        ellipsesTarget = {}
        # Get ellipse alignments.
        for id in range(len(newTargetEllipses)):
            ellipsesSource[newSourceEllipses[id]] = [newTargetEllipses[id]]
            ellipsesTarget[newTargetEllipses[id]] = [newSourceEllipses[id]]

        newSourceAlignments = self.__getNewAlignments(newSourceIds,newTargetIds,metadata['sourceAlignments'],ellipsesSource)
        newTargetAlignments = self.__getNewAlignments(newTargetIds,newSourceIds,metadata['targetAlignments'],ellipsesTarget)

        # Get new source and target token alignment group order.
        sourceAlignmentGroups = GetAlignmentGroups(newSourceAlignments,newTargetAlignments,0)
        targetAlignmentGroups = GetAlignmentGroups(newTargetAlignments,newSourceAlignments,0)
        newGroupAlignmentOrder = GetAlignmentOrders(sourceAlignmentGroups,targetAlignmentGroups,newTargetRanges,newTargetTokens)

        metadata['sourceAlignments'] = newSourceAlignments
        metadata['targetAlignments'] = newTargetAlignments
        metadata['sourceTokens'] = newSourceTokens
        metadata['targetTokens'] = newTargetTokens
        metadata['groupAlignmentOrder'] = newGroupAlignmentOrder
        metadata['targetWordRanges'] = newTargetRanges

        return metadata
                
    # Method to insert ellipses into translated tags
    def InsertEllipses(self,metadata):
        divisionId = 0
        ellipseId = 0
        tempSource = []
        tempTarget = []
        newTargetTokens = {}
        newTargetIds = {}
        newTargetEllipses = []
        newTargetRanges = []
        offset = 0

        for group in metadata['groupAlignmentOrder']:
            # First group to be inserted
            if len(tempSource) == 0:
                tempSource.extend(group[0])
                tempTarget.extend(group[1])
                for id in group[1]:
                    newTargetTokens[len(newTargetTokens)] = metadata['targetTokens'][id]
                    newTargetIds[id] = len(newTargetTokens)-1
                    newRange = list(map(lambda a : a + offset, metadata['targetWordRanges'][id].copy()))
                    newTargetRanges.append(newRange)
            else:
                divisionPart = metadata['divisionParts'][divisionId]
                nextSource = tempSource.copy() + group[0].copy()
                # If enough tokens inserted, then move to next division group.
                if len(nextSource) > len(divisionPart):
                    checkDivisionPart = []
                    # Go to next relevant division group.
                    while len(checkDivisionPart) < len(tempSource):
                        checkDivisionPart.extend(divisionPart.copy())
                        if divisionId + 1 == len(metadata['divisionParts']): break
                        divisionId += 1
                        divisionPart = metadata['divisionParts'][divisionId]
                    tempSource = []
                    tempTarget = []
                tempSource.extend(group[0])
                tempTarget.extend(group[1])
                divisionPart = metadata['divisionParts'][divisionId]
                # All ellipses have not been checked.
                if ellipseId < len(metadata['ellipses']):
                    ellipse = metadata['ellipses'][ellipseId]
                    # An ellipses needs to be inserted.
                    if divisionPart[0] >= ellipse[0]:
                        offset -= 1
                        lastEllipse = None
                        # Insert all ellipses that need to be inseerted.
                        while divisionPart[0] >= ellipse[0]:
                            newTargetTokens[len(newTargetTokens)] = ellipse[1][1]
                            newTargetEllipses.append(len(newTargetTokens)-1)
                            ellipseId += 1
                            (newRange,offsetAdd) = self.GetEllipseInsertRange(newTargetRanges[-1],lastEllipse,ellipse[1])
                            newTargetRanges.append(newRange)
                            offset += offsetAdd
                            if ellipseId == len(metadata['ellipses']): break
                            ellipse = metadata['ellipses'][ellipseId]
                            lastEllipse = ellipse[1][1]
                # Add new target tokens.
                for id in group[1]:
                    newTargetTokens[len(newTargetTokens)] = metadata['targetTokens'][id]
                    newTargetIds[id] = len(newTargetTokens)-1
                    newRange = list(map(lambda a : a + offset, metadata['targetWordRanges'][id].copy()))
                    newTargetRanges.append(newRange)

        if len(newTargetEllipses) > 0:
            metadata = self.GetNewTokenAlignments(metadata,newTargetTokens,newTargetIds,newTargetEllipses,newTargetRanges)

        return metadata
    
    # Method to get string index range for new ellipse.
    def GetEllipseInsertRange(
            self,
            lastRange,
            lastEllipse,
            pair  
        ):
        insertRange = []
        offsetAdd = 0

        if pair[0] == Constants.PUNCT_IN:
            insertRange = [lastRange[1],lastRange[1]+len(pair[1])]
            offsetAdd = len(pair[1])
        elif pair[0] == Constants.PUNCT_RIGHT:
            insertRange = [lastRange[1],lastRange[1]+len(pair[1])]
            offsetAdd = len(pair[1])+1
        else:
            if lastEllipse == None:
                if pair[0] == Constants.PUNCT_LEFT:
                    insertRange = [lastRange[1]+1,lastRange[1]+1+len(pair[1])]
                    offsetAdd = len(pair[1])+1
                elif pair[0] == Constants.PUNCT_OUT:
                    insertRange = [lastRange[1]+1,lastRange[1]+1+len(pair[1])]
                    offsetAdd = len(pair[1])+2
            else:
                if pair[0] == Constants.PUNCT_LEFT:
                    insertRange = [lastRange[1]+1,lastRange[1]+1+len(pair[1])]
                    offsetAdd = len(pair[1])
                elif pair[0] == Constants.PUNCT_OUT:
                    insertRange = [lastRange[1]+1,lastRange[1]+1+len(pair[1])]
                    offsetAdd = len(pair[1])+1

        return (insertRange,offsetAdd)
    
    # Method to insert tags in translated text.
    def InsertTags(self,metadata):
        for source in metadata['sourceAlignments']:
            elemId = metadata['textWithoutTags'][source]
            if elemId in metadata['openingTags']:
                targetId = metadata['sourceAlignments'][source][0]
                for tag in metadata['openingTags'][elemId]:
                    metadata['targetTokens'][targetId] = metadata['parts'][tag].value + metadata['targetTokens'][targetId]
            
            if elemId in metadata['closingTags']:
                targetId = metadata['sourceAlignments'][source][-1]
                for tag in metadata['closingTags'][elemId]:
                    metadata['targetTokens'][targetId] += metadata['parts'][tag].value
        
        return metadata
    
    # Main translation Method.
    def Translate(self,translator,hasSpaces,guidelines):
        if len(self._captions) == 1:
            if True in self._captions[0].IsIsolated():
                return self.TranslateIsolatedCaption(translator,hasSpaces,guidelines)
        return self.TranslateRegularCaptions(translator,hasSpaces,guidelines)
    
    # Translate regular sentences.
    def TranslateRegularCaptions(self,translator,hasSpaces,guidelines):
        # Get sentences.
        metadata = self.GetSentences(translator.hasAligner)

        # Translate them.
        metadata = Translator.Translator(metadata,self.SourceNLP,self.TargetNLP,translator)
        
        # Change current subtitle elements to use MT tokens if there are any.
        if translator.hasAligner:
            metadata = self.FixSubtitleParts(metadata)

        # Insert removed ellipses if there are any.
        if len(metadata['ellipses']) > 0:
            metadata = self.InsertEllipses(metadata)

        # Insert removed tags and curly bracket elements if there are any.
        if len(metadata['openingTags']) > 0 or len(metadata['closingTags']) > 0:
            metadata = self.InsertTags(metadata)

        textBreaker = TextBreaker(self.TargetNLP,guidelines,False)
        
        # Divide text into captions by word alignment.
        texts = textBreaker.DivideTranslationInCaptions(metadata,hasSpaces,self.GetIndexes())

        # Divide text into captions by syntactic chunks if cannot be done with word alignments.
        if texts == None:
            subtitleTexts = []
            for sIds in metadata['subtitleTexts']:
                subtitleTexts.append(self.__getTextFromAlignments(metadata['parts'],sIds))
            texts = textBreaker.GetSubtitleTextDividedIntoChunks(metadata,hasSpaces,subtitleTexts)

        # Get text lines from captions by syntactic chunks.
        texts = textBreaker.DivideTextIntoLines(texts,hasSpaces,self._captions,translator)

        return texts
    
    # Translate single caption that has special symbols (music notes).
    def TranslateIsolatedCaption(self,translator,hasSpaces,guidelines):
        # Get all subtitle elements in caption.
        parts: list[SubtitleElement] = self._captions[0].parts

        # Seperate them to get symbols and text divided from one another.
        textPieces = []
        translationPieces = []
        temp = ''
        last = None
        needToBreakLines = False
        for part in parts:
            spaces = ''
            if not(last == None): spaces = ' ' * (part.start-last.end)
            if part.subType in [Constants.EFFECT_OPEN,Constants.EFFECT_CLOSE,Constants.SYMBOL,Constants.ALIGN]:
                if len(temp)>0:
                    translationPieces.append(len(textPieces))
                    textPieces.append(temp)
                    temp = ''
                textPieces.append(spaces+part.value)
            elif part.subType == Constants.NEWLINE:
                print(len(textPieces),textPieces)
                print(len(temp),temp)
                tagless = re.sub(r'(\{.*?\}|<.*?>)','',temp)
                if len(textPieces)>0 and len(tagless)==0:
                    toInsert = temp
                    if len(toInsert)>0:
                        temp = ''
                    textPieces.append(toInsert+'\n')
                else:
                    temp += ' '
                    needToBreakLines = True
            else:
                if len(temp)==0:
                    if len(textPieces) > 0:
                        textPieces[-1] += spaces
                    temp += part.value
                else:
                    temp += spaces+part.value
            last = part
        
        if len(temp)>0:
            translationPieces.append(len(textPieces))
            textPieces.append(temp)

        print(textPieces)
        # Translate all text pieces found.
        for p in range(len(textPieces)):
            if p in translationPieces:
                textPieces[p] = translator.GetTranslationString(textPieces[p])

        textBreaker = TextBreaker(self.TargetNLP,guidelines,False)

        texts = { 0 : ''.join(textPieces)}

        # Get text lines from caption by syntactic chunks if text was in two lines and not seperated by symbols.
        if needToBreakLines:
            taggedTokenizer = TaggedTextTokenizer(texts[0],self.TargetNLP,True)
            texts[0] = textBreaker.GetTextLinesForSubtitle('',texts[0],'',taggedTokenizer,self._captions[0],hasSpaces)
        return texts