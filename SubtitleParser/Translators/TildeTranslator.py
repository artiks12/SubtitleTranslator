import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Translators.MTSystem import MTSystem
import requests

class TildeTranslator(MTSystem):
    def __init__(
        self,
        hasAligner,
        aligner,
        system_id,
        client_id,
    ) -> None:
        super().__init__(hasAligner,aligner,'tilde')
        self.system_id = system_id
        self.client_id = client_id

    def Translate(self,text,withTags,SourceNLP,TargetNLP,offsetSource,offsetTarget):
        data = self.__apiCall(text,withTags)

        if self.hasAligner:
            return self.GetTildeMetadata(data,text,offsetSource,offsetTarget,SourceNLP,TargetNLP)
        return self.GetTranslationMetadata(text,data['translation'],SourceNLP,TargetNLP,offsetSource,offsetTarget)   

    def GetTranslationString(self,text):
        return self.__apiCall(text,True)['translation'].replace('&quot;','"')
    
    def __apiCall(self,text,withTags):
        options = 'alignment,markSentences'
        if withTags: options += ',tagged'
        
        response = requests.post('https://www.letsmt.eu/ws/service.svc/json/TranslateEx',
                                headers={'Content-Type': 'application/json',
                                        'client-id': self.client_id},
                                json={'appID': 'TechChillDemo',
                                    'systemID': self.system_id,
                                    'text': text,
                                    'options': options})
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(e.response.status_code)
            print(e.response.content)
        return response.json()
    
    def GetTildeMetadata(self,data,text,offsetSource,offsetTarget,SourceNLP,TargetNLP):
        (sourceTokens,targetTokens) = self.GetTokensForSourceAndTarget(text,data,offsetSource,offsetTarget)
        alignmentData = {
            'sourceTokens':sourceTokens,
            'targetTokens':targetTokens,
            'sourceWordRanges':data['sourceWordRanges'],
            'targetWordRanges':data['targetWordRanges'],
            'wordAlignment':data['wordAlignment'],
            'confidentWordAlignment':data['confidentWordAlignment'],
            'translation':data['translation']
        }
        if len(data['wordAlignment']) == 0:
            alignmentData = self.GetTranslationMetadata(text,data['translation'],SourceNLP,TargetNLP,offsetSource,offsetTarget)
        return alignmentData

    def GetTokensForAlignment(self,text,wordRanges,offset):
        result = {}
        for i in range(len(wordRanges)):
            start = wordRanges[i][0]
            end = wordRanges[i][1]
            result[i+offset] = text[start:end]
        return result

    def GetTokensForSourceAndTarget(self,text,MT,offsetSource,offsetTarget):
        sourceTokens = self.GetTokensForAlignment(text,MT['sourceWordRanges'],offsetSource)
        targetTokens = self.GetTokensForAlignment(MT['translation'],MT['targetWordRanges'],offsetTarget)
        return (sourceTokens,targetTokens)


if __name__ == "__main__":
    from ids import system_id, client_id
    translator = TildeTranslator(False,None,system_id,client_id)

    print(translator.GetTranslationString('I want to--'))
    print(translator.GetTranslationString('If you want to go--'))
    print(translator.GetTranslationString('If he sees them--'))
    print(translator.GetTranslationString('I want to')+'--')
    print(translator.GetTranslationString('If you want to go')+'--')
    print(translator.GetTranslationString('If he sees them')+'--')
