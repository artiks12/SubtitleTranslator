import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))

import re
from SubtitleParser.Caption import Caption
from datetime import timedelta
import stanza
import srt

filenamesEN = [
    'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
    'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
]
filenamesLV = [
    'City.on.Fire.S01E03.WEB.x264-TORRENTGALAXY.Latvian.LAV',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.Latvian.LAV',
    'silo.s01e03.720p.web.h264-ggez.Latvian.LAV',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA.LAV',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.Latvian.LAV',
]

def RemoveSubCaptions(subtitles):
    newSubtitles = []
    index = 1
    for subtitle in subtitles:
        lines = subtitle.content.split('\n')
        speakers = [item for item in lines if item[0] == '-']
        if len(speakers)==0:
            newSubtitles.append(srt.Subtitle(index,timedelta(seconds=index),timedelta(seconds=index+1),subtitle.content))
            index += 1
        else:
            for line in lines:
                newSubtitles.append(srt.Subtitle(index,timedelta(seconds=index),timedelta(seconds=index+1),line[1:].strip()))
                index += 1
    return newSubtitles
    
def WriteToFile(path,file,subtitles):
    output = path+file+'.srt'
    
    f = open(output, mode='w', encoding='utf-8-sig')
    f.write(srt.compose(subtitles))
    f.close()

def GetParalelHumanMade():
    for x in range(len(filenamesEN)):
        sourceInput = 'DataPreparator/Paralel/'+filenamesEN[x]+'.srt'
        targetInput = 'DataPreparator/Paralel/'+filenamesLV[x]+'.srt'
        
        f = open(sourceInput, encoding='utf-8-sig')
        subtitlesEN = list(srt.parse(f.read()))
        f.close()
        f = open(targetInput, encoding='utf-8-sig')
        subtitlesLV = list(srt.parse(f.read()))
        f.close()

        subtitlesEN = RemoveSubCaptions(subtitlesEN)
        subtitlesLV = RemoveSubCaptions(subtitlesLV)

        path = 'DataPreparator/ParalelEvaluation/'
        WriteToFile(path,filenamesEN[x],subtitlesEN)
        WriteToFile(path,filenamesLV[x],subtitlesLV)

def GetParalelMTTranslated():
    for x in range(len(filenamesEN)):
        sourceInput = 'DataPreparator/Paralel/'+filenamesEN[x]+'.srt'
        targetInput = 'DataPreparator/Paralel/'+filenamesLV[x]+'.srt'
        
        f = open(sourceInput, encoding='utf-8-sig')
        subtitlesEN = list(srt.parse(f.read()))
        f.close()
        f = open(targetInput, encoding='utf-8-sig')
        subtitlesLV = list(srt.parse(f.read()))
        f.close()

        subtitlesEN = RemoveSubCaptions(subtitlesEN)
        subtitlesLV = RemoveSubCaptions(subtitlesLV)

        path = 'DataPreparator/ParalelEvaluation/'
        WriteToFile(path,filenamesEN[x],subtitlesEN)
        WriteToFile(path,filenamesLV[x],subtitlesLV)

if __name__ == "__main__":
    GetParalelHumanMade()
