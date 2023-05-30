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

variant = {
    '.tilde.SimAlign.srt':'SimAlign/',
    '.tilde.tilde.srt':'Tilde/',
    '.tilde.docuemnt.srt':'Document/',
    '.tilde.Sentences.srt':'Sentences/',
}

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
        text = caption.SpeakingTextWithNewLines()
        while re.fullmatch(r'[\n\r\s\t]+',text[-1]):
            text = text[:-1]
        return text

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
    output = path+file
    
    f = open(output, mode='w', encoding='utf-8-sig')
    f.write(srt.compose(subtitles))
    f.close()

def MainPreparator(
    sourceFile,
    targetFile,
    needTargetNormalize,
    sourceLang = 'en',
    targetLang = 'lv',
    pathInput = 'SubtitleParser/Subtitles/',
    pathOutput = 'DataPreparator/Result/',
    subtitleFormat = 'srt'
):
    SourceNLP = stanza.Pipeline(lang=sourceLang, processors='tokenize,pos,lemma,depparse', use_gpu=True)
    TargetNLP = stanza.Pipeline(lang=targetLang, processors='tokenize,pos,lemma,depparse', use_gpu=True)

    sourceInput = pathInput+sourceFile+'.'+subtitleFormat
    targetInput = pathInput+targetFile+'.'+subtitleFormat
    
    f = open(sourceInput, encoding='utf-8-sig')
    subtitlesSource = list(srt.parse(f.read()))
    f.close()
    
    f = open(targetInput, encoding='utf-8-sig')
    subtitlesTarget = list(srt.parse(f.read()))
    f.close()

    subtitlesSource = Normalize(subtitlesSource,SourceNLP)
    if needTargetNormalize:
        subtitlesTarget = Normalize(subtitlesTarget,TargetNLP)

    subtitlesSource, subtitlesTarget = GetParalelSubtitles(subtitlesSource,subtitlesTarget)

    print(folder,filenamesEN[x])
    
    CheckSubtitleSpeakerEquality(subtitlesSource, subtitlesTarget)

    WriteToFile(pathOutput,sourceFile+'.'+subtitleFormat,subtitlesSource)
    if needTargetNormalize:
        WriteToFile(pathOutput,targetFile+'.'+subtitleFormat,subtitlesTarget)


if __name__ == "__main__":
    nlpEN = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)

    for file in variant:
        folder = variant[file]
        for x in range(5):
            sourceInput = 'DataPreparator/TranslatedOriginal/'+folder+filenamesEN[x]+file
            targetInput = 'DataPreparator/Paralel/'+filenamesLV[x]+'.srt'
            
            f = open(sourceInput, encoding='utf-8-sig')
            subtitlesEN = list(srt.parse(f.read()))
            f.close()
            
            f = open(targetInput, encoding='utf-8-sig')
            subtitlesLV = list(srt.parse(f.read()))
            f.close()

            subtitlesEN = Normalize(subtitlesEN,nlpEN)
        
            subtitlesEN, subtitlesLV = GetParalelSubtitles(subtitlesEN,subtitlesLV)

            print(folder,filenamesEN[x])
            
            CheckSubtitleSpeakerEquality(subtitlesEN, subtitlesLV)
            
            pathMT = 'DataPreparator/TranslatedOriginalToParalel/'+folder
            WriteToFile(pathMT,filenamesEN[x]+file,subtitlesEN)
