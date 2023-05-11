from CustomWordAligner import GetCustomAlignments

class MTSystem():
    def __init__(
        self,
        hasAligner,
        aligner,
    ):
        self.hasAligner = hasAligner
        self.aligner = aligner

    def GetTranslationMetadata(self,text,translation,SourceNLP,TargetNLP,offsetSource,offsetTarget):
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

        for word in textTokens.words:
            alignmentData['sourceTokens'][word.id-1+offsetSource] = word.text
            alignmentData['sourceWordRanges'].append([word.start_char,word.end_char])

        for word in translationTokens.words:
            alignmentData['targetTokens'][word.id-1+offsetTarget] = word.text
            alignmentData['targetWordRanges'].append([word.start_char,word.end_char])

        alignments = GetCustomAlignments(self.aligner,list(alignmentData['sourceTokens'].values()),list(alignmentData['targetTokens'].values()))

        alignmentData['confidentWordAlignment'] = alignments['confidentWordAlignment']
        alignmentData['wordAlignment'] = alignments['wordAlignment']

        return alignmentData
