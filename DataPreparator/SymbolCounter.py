import srt
import re

filenamesEN = [
    'City.on.Fire.S01E03.1080p.WEB.H264-GGWP',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG',
    'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG',
]

def GetTotalSymbolCount(path):
    totalSymbols = 0
    totalSubtitles = 0

    for x in range(len(filenamesEN)):
        sourceInput = path+filenamesEN[x]+'.srt'
        
        f = open(sourceInput, encoding='utf-8-sig')
        subtitlesEN = list(srt.parse(f.read()))
        f.close()

        symbolCount = 0
        subtitleCount = 0

        for subtitle in subtitlesEN:
            text = subtitle.content.replace('\n',' ')
            text = re.sub(r'(\{.*?\}|<.*?>)','',text)
            symbolCount += len(text)
            subtitleCount += 1

        print(filenamesEN[x]+':',str(symbolCount)+' in '+str(subtitleCount)+' subtitles.',sep='\t')
        totalSymbols += symbolCount
        totalSubtitles += subtitleCount
    
    print('Total in '+path+':',str(totalSymbols)+' in '+str(totalSubtitles)+' subtitles.',sep='\t')
    print('---------------------------------------------------')

if __name__ == "__main__":
    GetTotalSymbolCount('DataPreparator/Original/')
    GetTotalSymbolCount('DataPreparator/Prepared/')