import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[-1]),''))
from SubtitleParser.CustomWordAligner import GetCustomAlignments
from SubtitleParser.CustomTokenizer import CustomTokenizer

class MTSystem():
    def __init__(
        self,
        hasAligner,
        aligner,
        name
    ):
        self.hasAligner = hasAligner
        self.aligner = aligner
        self.name = name
        self.alignerName = 'SimAlign'
        if self.hasAligner: self.alignerName = name
            

    def GetTranslationMetadata(self,text,translation,SourceNLP,TargetNLP,offsetSource,offsetTarget):
        tokenizerSource = CustomTokenizer(SourceNLP)
        tokenizerTarget = CustomTokenizer(TargetNLP)
        tokenizerSource.Tokenize(text,True)
        tokenizerTarget.Tokenize(translation,True)
        textTokens = SourceNLP(text).sentences[0]
        translationTokens = TargetNLP(translation).sentences[0]

        alignmentData = {
            'sourceTokens':{},
            'targetTokens':{},
            'sourceWordRanges':[],
            'targetWordRanges':[],
            'wordAlignment':[],
            'confidentWordAlignment':[],
            'translation':translation
        }

        for word in tokenizerSource.tokens:
            alignmentData['sourceTokens'][word.id+offsetSource] = word.value
            alignmentData['sourceWordRanges'].append([word.start,word.end])

        for word in tokenizerTarget.tokens:
            alignmentData['targetTokens'][word.id+offsetTarget] = word.value
            alignmentData['targetWordRanges'].append([word.start,word.end])

        alignments = GetCustomAlignments(self.aligner,list(alignmentData['sourceTokens'].values()),list(alignmentData['targetTokens'].values()))

        alignmentData['confidentWordAlignment'] = alignments['confidentWordAlignment']
        alignmentData['wordAlignment'] = alignments['wordAlignment']

        return alignmentData
