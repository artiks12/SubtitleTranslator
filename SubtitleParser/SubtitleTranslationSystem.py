from datetime import datetime
from Combiner import combiner
from Translators.TildeTranslator import TildeTranslator
from Translators.ids import system_id, client_id
import stanza
import srt
from SubtitleGuidelineMetrics import SubtitleGuidelineMetrics
from simalign import SentenceAligner
import sys

class SubtitleTranslationSystem():
    def __init__(
        self,
        sourceTokenizer,
        targetTokenizer,
        targetPretokenizer,
        subtitleReader,
        subtitleWritter,
        translator,
        guidelines,
        customAligner,
    ):
        self.sourceTokenizer = sourceTokenizer
        self.targetTokenizer = targetTokenizer
        self.targetPretokenizer = targetPretokenizer
        self.subtitleReader = subtitleReader
        self.subtitleWritter = subtitleWritter
        self.translator = translator
        self.guidelines = guidelines
        self.customAligner = customAligner

    def Execute(self,sourcefile,targetfile):
        f = open(sourcefile, encoding='utf-8-sig')

        subtitles = list(self.subtitleReader(f.read()))
        f.close()     

        print('Begin subtitle combining',datetime.now())
        combined = combiner(subtitles,self.sourceTokenizer,self.targetTokenizer,self.targetPretokenizer)
        
        print('Begin translating',datetime.now())
        result = {}
        for c in combined:
            indexes = c.GetIndexes()
            captions = c.GetCaptions()
            print(indexes)
            translations: dict = c.Translate(self.translator,True,self.guidelines)
            for key in translations:
                index = indexes[key]-1
                caption = captions[key]
                if index not in result: result[index] = []
                result[index].append((caption.Order,translations[key]))

        print('Begin writing in file',datetime.now())
        for s in range(len(subtitles)):
            temp = sorted(result[s], key=lambda x: x[0])
            subtitles[s].content = ''.join([item[1] for item in temp])
        
        f = open(targetfile, mode='w', encoding='utf-8-sig')
        f.write(self.subtitleWritter(subtitles))
        f.close()

        print('Process finished at',datetime.now())

if __name__ == "__main__":
    SourceNLP = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    TargetNLP = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    PretokenizeNLP = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True, tokenize_pretokenized=True)
    reader = srt.parse
    writter = srt.compose
    simAlign = SentenceAligner(model='bert', token_type='bpe', matching_methods="maifr")
    translator = TildeTranslator(True,simAlign,system_id,client_id)
    subtitlingGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_LV')

    filenames = [
        # 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
        # 'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
        # 'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
        # 'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
        # 'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
        'Sample'
    ]
    MainSystem = SubtitleTranslationSystem(SourceNLP,TargetNLP,PretokenizeNLP,reader,writter,translator,subtitlingGuidelines,simAlign)
    for filename in filenames:
        # sourcefile = 'DataPreparator/Paralel/'+filename+'.srt'
        # sourcefile = 'DataPreparator/Original/'+filename+'.srt'
        sourcefile = 'SubtitleParser/Subtitles/'+filename+'.srt'
        targetfile = 'SubtitleParser/Result/'+filename+'.'+translator.name+'.'+translator.alignerName+'.srt'
        
        MainSystem.Execute(sourcefile,targetfile)
        