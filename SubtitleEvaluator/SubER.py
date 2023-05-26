import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from subprocess import check_output

referenceFiles = [
    'City.on.Fire.S01E03.WEB.x264-TORRENTGALAXY.Latvian.LAV.srt',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.Latvian.LAV.srt',
    'silo.s01e03.720p.web.h264-ggez.Latvian.LAV.srt',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA.LAV.srt',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.Latvian.LAV.srt',
]

hypothesesFiles = [
    'City.on.Fire.S01E03.1080p.WEB.H264-GGWP.',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG.',
    'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG.',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG.',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG.',
]

variant = {
    'tilde.SimAlign.srt':'TildeSimAlign\\',
    'tilde.tilde.srt':'TildeTilde\\',
    'srt':'TildeDocument\\',
    'tilde.Sentences.srt':'TildeSentences\\',
}

if __name__ == "__main__":
    pathHyp = sys.path[-1]+'DataPreparator\\TranslatedParalel\\'
    pathRef = sys.path[-1]+'DataPreparator\\Paralel\\'
        
    logFile = open(sys.path[-1]+'SubtitleEvaluator\\log.txt', mode='w', encoding='utf-8-sig')
    for file in variant:
        result = open(sys.path[-1]+'SubtitleEvaluator\\SubERscores\\'+file+'.txt', mode='w', encoding='utf-8-sig')
        folder = variant[file]
        for x in range(5):
            hypFile = pathHyp+folder+hypothesesFiles[x]+file
            refFile = pathRef+referenceFiles[x]

            result.write(hypothesesFiles[x]+'\n')
            result.write(str(check_output(["suber", "-H", hypFile, '-R', refFile]) )+'\n')
        result.close()
    logFile.close()