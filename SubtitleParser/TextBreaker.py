import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Sentences import Sentences
from SubtitleParser.Caption import Caption
from SubtitleParser.SubtitleElementTokenizer import SubtitleElement
import SubtitleParser.Configurations.Constants as Constants
import SubtitleParser.Translator as Translator
from SubtitleParser.SentenceMetadataFunctions import SentenceMetadataFunctions
from SubtitleParser.CustomTokenizer import CustomTokenizer
from SubtitleParser.TaggedTextTokenizer import TaggedToken, TaggedTextTokenizer
from SubtitleParser.SyntacticChunker import GetSyntachticChunksAsStrings
from SubtitleParser.SubtitleGuidelineMetrics import SubtitleGuidelineMetrics
import re
import math

class TextBreaker():
    def __init__(
            self,
            TargetNLP,
            guidelines: SubtitleGuidelineMetrics,
            useConstituency = False
        ) -> None:
        self.TargetNLP = TargetNLP
        self.guidelines = guidelines
        self.useConstituency = useConstituency

    def __getCaptionBooleans(self, index, count):
        if index == count: return (False,True)
        if index == 1: return (True,False)
        return (False,False)

    def DivideTranslationInCaptions(self,metadata,hasSpaces,captionIds):
        if len(captionIds) == 1:
            return {
                0: self.GetTextFromMetadata(list(metadata['targetTokens'].keys()),metadata['targetTokens'],metadata['targetWordRanges'])
            }
        
        result = self.__divideTranslationsWithLastPosition(metadata,hasSpaces,captionIds)

        if len(captionIds) == len(result):
            return result
        
        result = self.__divideTranslationsWithGroups(metadata)

        if len(captionIds) == len(result):
            return result
        
        return None
    
    def __divideTranslationsWithLastPosition(self,metadata,hasSpaces,captionIds):
        result = {}

        splitPoints = []
        id = -1
        for sT in range(len(metadata['subtitleTexts'])):
            if sT + 1 == len(metadata['subtitleTexts']): break
            id += len(metadata['subtitleTexts'][sT])
            splitPoints.append(id)

        elem = 0
        subtitleMetadata = {}
        for sub in range(len(captionIds)):
            if sub+1 == len(captionIds): subtitleMetadata[sub] = list(range(elem,len(list(metadata['targetTokens'].keys()))))
            else:
                tokenId = metadata['sourceAlignments'][splitPoints[sub]][-1]
                tokenRange = list(range(elem,tokenId+1))
                if len(tokenRange) > 0: subtitleMetadata[sub] = tokenRange
                elem = tokenId+1
                if len(tokenRange) > 0:
                    if elem < len(metadata['targetWordRanges']):
                        while re.match(r'(\.+|[?!]+|…|¿|¡|,+|:+|-+|–+)',metadata['targetTokens'][elem]):
                            subtitleMetadata[sub].append(elem)
                            elem += 1
                            if elem == len(metadata['targetWordRanges']): break
                if elem == len(metadata['targetWordRanges']): break
        result = {}
        for meta in subtitleMetadata:
            result[meta] = self.GetTextFromMetadata(subtitleMetadata[meta],metadata['targetTokens'],metadata['targetWordRanges'])
        
        return result

    def __divideTranslationsWithGroups(self,metadata):
        tempSource = []
        tempTarget = []
        subtitleId = 0
        subtitleMetadata = {}
        for group in metadata['groupAlignmentOrder']:
            tempSource.extend(group[0].copy())
            tempTarget.extend(group[1].copy())
            if len(metadata['subtitleTexts'][subtitleId]) <= len(tempSource):
                subtitleMetadata[subtitleId] = tempTarget
                tempSource = []
                tempTarget = []
                subtitleId += 1
        
        if len(tempTarget) > 0:
            subtitleMetadata[subtitleId] = tempTarget
        
        result = {}
        for meta in subtitleMetadata:
            result[meta] = self.GetTextFromMetadata(subtitleMetadata[meta],metadata['targetTokens'],metadata['targetWordRanges'])

        return result
        
    def GetTextFromMetadata(self,tokensIds,tokens,ranges):
        text = ''
        for x in tokensIds:
            if text == '':
                text += tokens[x]
            else:
                spaces = ' ' * (ranges[x][0]-ranges[x-1][1])
                text += spaces + tokens[x]
        return text

    def GetTextLinesForSubtitle(self,left,middle,right,taggedTokenizer,caption,hasSpaces):
        chunks = GetSyntachticChunksAsStrings(taggedTokenizer.tokens,hasSpaces)

        chunks[0] = left + chunks[0]
        chunks[-1] += right
        fullText = left + middle + right
        fullTextTagless = re.sub(r'(<.*?>|\{.*?\})','',fullText)

        if len(fullTextTagless) <= self.guidelines.symbols or caption.IsSubCaption: return left + middle + right
        elif len(chunks) == 1: return chunks[0]
        else:
            line1 = ''
            line2 = ''
            inBetween = ''
            lineLength = len(fullTextTagless)/self.guidelines.rows
            secondLine = False
            for chunk in chunks:
                if secondLine:
                    line2 += chunk
                else: 
                    next = line1 + chunk
                    nextTagless = re.sub(r'(<.*?>|\{.*?\})','',next)
                    if len(nextTagless) <= max(lineLength,self.guidelines.symbols):
                        line1 = next
                    else:
                        inBetween = chunk
                        secondLine = True
            text = line1
            if len(line1) <= len(line2):
                text += inBetween + '\n' + line2[1:]
            else:
                text += '\n' + inBetween[1:] + line2
            return text
        
    def GetSubtitleTextDividedIntoChunks(self,metadata,hasSpaces,subtitleTexts):
        text = self.GetTextFromMetadata(list(metadata['targetTokens'].keys()),metadata['targetTokens'],metadata['targetWordRanges'])
        taggedTokenizer = TaggedTextTokenizer(text,self.TargetNLP,True)
        chunks = GetSyntachticChunksAsStrings(taggedTokenizer.tokens,hasSpaces)
        
        lengthsSource = [len(item) for item in subtitleTexts]
        proportionsSource = [item/(sum(lengthsSource)+len(lengthsSource)-1) for item in lengthsSource]
        lengthsTarget = [math.floor(len(text)*item) for item in proportionsSource]

        result = {}
        lines = ''
        tagless = re.sub(r'(<.*?>|\{.*?\})','',lines)
        captionId = 0
        for chunk in chunks:
            next = lines + chunk
            nextTagless = re.sub(r'(<.*?>|\{.*?\})','',next)
            if captionId+1 == len(lengthsTarget):
                lines = next
            elif len(nextTagless) <= lengthsTarget[captionId]:
                lines = next
            else:
                before = lengthsTarget[captionId] - len(tagless)
                after = len(nextTagless) - lengthsTarget[captionId]
                if before > after or len(lines) == 0: 
                    lines = next
                else:
                    result[captionId] = lines
                    captionId += 1
                    if chunk[0] == ' ': lines = chunk[1:]
                    else: lines = chunk
            tagless = re.sub(r'(<.*?>|\{.*?\})','',lines)
        if len(lines)>0: result[captionId] = lines
        
        return result
    
    def DivideTextIntoLines(self,texts,hasSpaces,captions,translator):
        result = {}
        for t in texts:
            taggedTokenizer = TaggedTextTokenizer(texts[t],self.TargetNLP,True)
            caption = captions[t]
            (needStart,needEnd) = self.__getCaptionBooleans(t+1,len(texts))
            (start,end) = caption.GetSpeakerTextStartAndEnd(needStart,needEnd)
            
            left = self.GetTextForCaptionEnd(start,translator)
            right = self.GetTextForCaptionEnd(end,translator)

            if len(left) > 0:
                if not(caption.parts[len(start)].start == caption.parts[len(start)-1].end):
                    last = caption.parts[len(start)-1].end
                    next = caption.parts[len(start)].start
                    spaces = ' ' * (next-last)
                    left += spaces
            
            if len(right) > 0:
                id = end[0].GetIndex()
                last = caption.parts[id-1].end
                next = caption.parts[id].start
                if not(last == next):
                    spaces = ' ' * (next-last)
                    right = spaces + right

            # print(left,texts[t],right)

            result[t] = self.GetTextLinesForSubtitle(left,texts[t],right,taggedTokenizer,caption,hasSpaces)

        return result

    def GetTextForCaptionEnd(self,parts,translator):
        result = ''
        effect = ''
        spaces = ''
        isEffect = False
        for s in range(len(parts)):
            value = parts[s].value
            if not(isEffect):
                if parts[s].subType == Constants.SPEAKER and not(re.fullmatch(r'(–+|-+|:)',parts[s].value)):
                    if len(effect)>0:
                        spaces = ' ' * (parts[s].start-parts[s-1].end)
                    effect += spaces + value
                else:
                    if len(effect)>0:
                        effect = translator.GetTranslationString(effect)
                        result += effect
                    if result == '': result += value
                    else: 
                        spaces = ' ' * (parts[s].start-parts[s-1].end)
                        result += spaces + value
                    if parts[s].subType == Constants.EFFECT_OPEN:
                        isEffect = True
            else:
                if parts[s].subType == Constants.EFFECT_CLOSE:
                    effect = translator.GetTranslationString(effect)
                    result += effect + value
                    isEffect = False
                    effect = ''
                else:
                    spaces = ' ' * (parts[s].start-parts[s-1].end)
                    effect += spaces + value
        return result