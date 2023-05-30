from datetime import datetime
from SubtitleParser.Translators.TildeTranslator import TildeTranslator
from SubtitleParser.Translators.ids import system_id, client_id
from SubtitleParser.Caption import Caption
from SubtitleParser.TextBreaker import TextBreaker
from SubtitleParser.SubtitleGuidelineMetrics import SubtitleGuidelineMetrics
from SubtitleParser.TaggedTextTokenizer import TaggedTextTokenizer
from SubtitleParser.Combiner import combiner
import srt
import stanza

class SubtitleSentenceTranslator():
    def __init__(
        self,
        sourceNLP,
        targetNLP,
        guidelines,
        subtitleReader,
        subtitleWritter,
        translator,
    ):
        self.SourceNLP = sourceNLP
        self.TargetNLP = targetNLP
        self.guidelines = guidelines
        self.subtitleReader = subtitleReader
        self.subtitleWritter = subtitleWritter
        self.translator = translator

    def __getCaptionBooleans(self, index, count):
        if index == count: return (False,True)
        if index == 1: return (True,False)
        return (False,False)
    
    def TranslateRegularCaptions(self,captions,textBreaker):
        subtitleTexts = []
        for x in range(len(captions)):
            (needStart,needEnd) = self.__getCaptionBooleans(x+1,len(captions))
            subtitleTexts.append(captions[x].SpeakingTextWithoutStartAndEndEllipses(needStart,needEnd))
        text = ' '.join(subtitleTexts)
        translation = self.translator.GetTranslationString(text)

        taggedTokenizer = TaggedTextTokenizer(translation,self.TargetNLP,True)

        metadata = {
            'targetTokens':dict([[item.id,item.value] for item in taggedTokenizer.tokens]),
            'targetWordRanges':[[item.start,item.end] for item in taggedTokenizer.tokens]
        }
        
        texts = textBreaker.GetSubtitleTextDividedIntoChunks(metadata,True,subtitleTexts)

        return textBreaker.DivideTextIntoLines(texts,True,captions,self.translator)

    def Execute(self,sourcefile,targetfile):
        f = open(sourcefile, encoding='utf-8-sig')

        subtitles = list(self.subtitleReader(f.read()))
        f.close()     

        print('Begin combining',datetime.now())

        combined = combiner(subtitles,self.SourceNLP,self.TargetNLP,None)
        
        print('Begin translating',datetime.now())
        result = {}
        textBreaker = TextBreaker(self.TargetNLP,self.guidelines)
        for c in combined:
            indexes = c.GetIndexes()
            captions = c.GetCaptions()
            print(indexes)
            texts = None
            if len(captions) == 1 and True in captions[0].IsIsolated():
                texts = c.TranslateIsolatedCaption(translator,True,self.guidelines)
            else:
                texts = self.TranslateRegularCaptions(captions,textBreaker)

            for key in texts:
                index = indexes[key]-1
                caption = captions[key]
                if index not in result: result[index] = []
                result[index].append((caption.Order,texts[key]))

        print('Begin writing in file',datetime.now())
        for s in range(len(subtitles)):
            temp = sorted(result[s], key=lambda x: x[0])
            subtitles[s].content = ''.join([item[1] for item in temp])
        
        f = open(targetfile, mode='w', encoding='utf-8-sig')
        f.write(self.subtitleWritter(subtitles))
        f.close()

        print('Process finished at',datetime.now())

def MainSentences(
    filename,
    subtitlingGuidelines,
    translator,
    sourceLang = 'en',
    targetLang = 'lv',
    pathInput = 'SubtitleParser/Subtitles/',
    pathOutput = 'SubtitleParser/Result/',
    subtitleFormat = 'srt',
):
    SourceNLP = stanza.Pipeline(lang=sourceLang, processors='tokenize,pos,lemma,depparse', use_gpu=True)
    TargetNLP = stanza.Pipeline(lang=targetLang, processors='tokenize,pos,lemma,depparse', use_gpu=True)
    reader = srt.parse
    writter = srt.compose

    MainSystem = SubtitleSentenceTranslator(SourceNLP,TargetNLP,subtitlingGuidelines,reader,writter,translator)

    sourcefile = pathInput+filename+'.'+subtitleFormat
    targetfile = pathOutput+filename+'.'+subtitleFormat
    
    MainSystem.Execute(sourcefile,targetfile)

if __name__ == "__main__":
    SourceNLP = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    TargetNLP = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    subtitlingGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_LV')
    reader = srt.parse
    writter = srt.compose
    translator = TildeTranslator(False,None,system_id,client_id)

    filenames = [
        # 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
        # 'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
        # 'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
        # 'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
        # 'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
        'Sample'
    ]
    MainSystem = SubtitleSentenceTranslator(SourceNLP,TargetNLP,subtitlingGuidelines,reader,writter,translator)
    import sys
    for filename in filenames:
        # sourcefile = sys.path[0]+'\\DataPreparator\\Paralel\\'+filename+'.srt'
        # sourcefile = sys.path[0]+'\\DataPreparator\\Original\\'+filename+'.srt'
        sourcefile = sys.path[0]+'\\SubtitleParser\\Subtitles\\'+filename+'.srt'
        targetfile = sys.path[0]+'\\SubtitleParser\\Result\\'+filename+'.'+translator.name+'.Sentences.srt'
        
        MainSystem.Execute(sourcefile,targetfile)
        