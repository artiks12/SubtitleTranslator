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
            print(indexes)
            translations: dict = c.Translate(self.translator,True,self.guidelines)
            for key in translations:
                index = indexes[key]-1
                if index not in result: result[index] = ''
                result[index] += translations[key]

        print('Begin writing in file',datetime.now())
        for s in range(len(subtitles)):
            subtitles[s].content = result[s]
        
        f = open(targetfile, mode='w', encoding='utf-8-sig')
        f.write(self.subtitleWritter(subtitles))
        f.close()

        print('Process finished at',datetime.now())

if __name__ == "__main__":
    SourceNLP = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    TargetNLP = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    PretokenizeNLP = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True, tokenize_pretokenized=True)
    reader = srt.parse
    writter = srt.compose
    simAlign = SentenceAligner(model='bert', token_type='bpe', matching_methods="maifr")
    translator = TildeTranslator(True,simAlign,system_id,client_id)
    subtitlingGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_LV')

    filenames = [
        # 'Lucky.Hank.S01E06.WEB'
        # 'CSI.Vegas.S02E18.WEBRip.x264.Hi',
        'Sample3',
    ]
    MainSystem = SubtitleTranslationSystem(SourceNLP,TargetNLP,PretokenizeNLP,reader,writter,translator,subtitlingGuidelines,simAlign)
    for filename in filenames:
        sourcefile = 'SubtitleParser/Subtitles/'+filename+'.srt'
        targetfile = 'SubtitleParser/Result/'+filename+'.srt'
        
        MainSystem.Execute(sourcefile,targetfile)
        