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

def GetNormalizedText(caption: Caption):
    if caption.HasMultipleSpeakers():
        speakers = []
        for i in range(caption.GetSpeakerCount()):
            newCaption = caption.GetCopyWithOneSpeaker(i)
            if newCaption.IsIsolated()[0]: continue
            text = newCaption.SpeakingTextWithNewLines()
            if not(re.fullmatch(r'[\n\r\s\t]+',text)) and len(text)>0:
                speakers.append(text)
        if len(speakers) == 0: return ''
        elif len(speakers) == 1:
            text = speakers[0]
            while re.fullmatch(r'[\n\r\s\t]+',text[-1]): text = text[:-1]
            return text
        else:
            speakers = ['- '+item for item in speakers]
            return ''.join(speakers)
    else:
        if caption.IsIsolated()[0]: return ''
        return caption.SpeakingTextWithNewLines()

def Normalize(subtitles,nlp):
    newSubtitles = []
    result = {}
    for s in subtitles:
        t = Caption().NewCaption(s.content,s.index,nlp)
        result[s.index-1] = GetNormalizedText(t)

    for s in range(len(subtitles)):
        if len(result[s]) > 0:
            index = len(newSubtitles)+1
            newSubtitles.append(srt.Subtitle(index,subtitles[s].start,subtitles[s].end,result[s]))

    return newSubtitles

def withinRange(LV,EN,range):
    return abs(LV-EN)<timedelta(milliseconds=range)

def intFromTimedelta(time):
    result = time.seconds*1000 + time.microseconds/1000
    return int(result)

def timeDifference(LV,EN):
    return str(intFromTimedelta(LV) - intFromTimedelta(EN))

def GetParalelSubtitles(source,target):
    targetId = 0
    sourceId = 0

    newSource = []
    newTarget = []

    while targetId < len(target) and sourceId<len(source):
        if withinRange(target[targetId].start,source[sourceId].start,500) and withinRange(target[targetId].end,source[sourceId].end,500):
            newSource.append(source[sourceId])
            newTarget.append(target[targetId])
            targetId += 1
            sourceId += 1
        else:
            if target[targetId].start < source[sourceId].start:
                targetId += 1
            elif target[targetId].start > source[sourceId].start:
                sourceId += 1
            else:
                if target[targetId].end < source[sourceId].end:
                    targetId += 1
                else:
                    sourceId += 1

    return newSource, newTarget

def CheckSubtitleSpeakerEquality(source, target):
    speakerProblems = []

    if len(source)==len(target):
        for x in range(len(source)):
            s:str = source[x].content.split('\n')
            t:str = target[x].content.split('\n')

            speakersSource = [item for item in s if s[0] == '-']
            speakersTarget = [item for item in t if t[0] == '-']

            if not(len(speakersSource) == len(speakersTarget)):
                side = len(speakersSource) < len(speakersTarget)
                speakerProblems.append((x+1,side))
    else:
        print('Not equal subtitle amount')
        return None
    
    if len(speakerProblems) > 0:
        print(speakerProblems)
    
def WriteToFile(path,file,subtitles):
    output = path+file+'.srt'
    
    f = open(output, mode='w', encoding='utf-8-sig')
    f.write(srt.compose(subtitles))
    f.close()

if __name__ == "__main__":
    nlpEN = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    nlpLV = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True)

    for x in range(len(filenamesEN)):
        sourceInput = 'DataPreparator/Original/'+filenamesEN[x]+'.srt'
        targetInput = 'DataPreparator/Original/'+filenamesLV[x]+'.srt'
        
        f = open(sourceInput, encoding='utf-8-sig')
        subtitlesEN = list(srt.parse(f.read()))
        f.close()
        f = open(targetInput, encoding='utf-8-sig')
        subtitlesLV = list(srt.parse(f.read()))
        f.close()

        subtitlesEN = Normalize(subtitlesEN,nlpEN)
        subtitlesLV = Normalize(subtitlesLV,nlpLV)
    
        subtitlesEN, subtitlesLV = GetParalelSubtitles(subtitlesEN,subtitlesLV)

        print(filenamesEN[x])
        
        CheckSubtitleSpeakerEquality(subtitlesEN, subtitlesLV)
        
        path = 'DataPreparator/Prepared/'
        WriteToFile(path,filenamesEN[x],subtitlesEN)
        WriteToFile(path,filenamesLV[x],subtitlesLV)
