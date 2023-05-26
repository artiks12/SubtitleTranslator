import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
import srt

hypothesesFiles = [
    'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
    'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
]

def GetDifferentSubtitles(simalign, tilde):
    result= []

    if len(simalign)==len(tilde):
        for x in range(len(tilde)):
            if not(simalign[x].content == tilde[x].content):
                result.append(x+1)

    return result

if __name__ == "__main__":
    path = 'DataPreparator\\TranslatedParalel\\'
    for x in range(5):
        simalign = path+hypothesesFiles[x]+'.tilde.SimAlign.srt'
        tilde = path+hypothesesFiles[x]+'.tilde.tilde.srt'
        
        f = open(simalign, encoding='utf-8-sig')
        subtitlesSimalign = list(srt.parse(f.read()))
        f.close()
        f = open(tilde, encoding='utf-8-sig')
        subtitlesTilde = list(srt.parse(f.read()))
        f.close()

        result = GetDifferentSubtitles(subtitlesSimalign,subtitlesTilde)

        print(len(subtitlesSimalign),len(result))
        print(result)
        print('-------------------------------------------------')