import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
import srt
from SubtitleParser.Combiner import combiner
import stanza

def GetSubcaptionCount(file,nlp):
    f = open(file, encoding='utf-8-sig')

    subtitles = list(srt.parse(f.read()))
    f.close()     

    combined = combiner(subtitles,nlp,None,None)

    combCount = 0
    singleCount = 0
    combGroupCount = 0
    singleGroupCount = 0
    for c in combined:
        indexes = c.GetIndexes()
        result = len(indexes)
        if result == 1: 
            singleCount += result
            singleGroupCount += 1
        else: 
            combCount += result
            combGroupCount += 1

    print(file)
    print('Captions:',combCount+singleCount,singleCount,combCount)
    print('Groups:',combGroupCount+singleGroupCount,singleGroupCount,combGroupCount)

if __name__ == "__main__":
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)

    filenames = [
        'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
        'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
        'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
        'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
        'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
    ]
    for filename in filenames:
        file = 'DataPreparator/Paralel/'+filename+'.srt'
        
        GetSubcaptionCount(file,nlp)