import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))

from datetime import timedelta
import srt
import re
from SubtitleParser.SubtitleGuidelineMetrics import SubtitleGuidelineMetrics
import math

files = [
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

class Measure():
    def __init__(self,sourceLimit,targetLimit):
        self.bothFollow = 0
        self.sourceFollows = 0
        self.targetFollows = 0
        self.neitherFollows = 0
        self.sourceLimit = sourceLimit
        self.targetLimit = targetLimit

    def AddToScores(self,source,target):
        if source:
            if target: self.bothFollow += 1
            else: self.sourceFollows += 1
        else:
            if target: self.targetFollows += 1
            else: self.neitherFollows += 1

    def _getScoresAsString(self):
        return f"\tbothFollow:{self.bothFollow},\n\tsourceFollows:{self.sourceFollows},\n\ttargetFollows:{self.targetFollows},\n\tneitherFollows:{self.neitherFollows},\n"

    # def _getQualityChange(self):
    #     return f"\tqualityWorse:{self.sourceFollows},\n\tqualityNotWorse:{self.bothFollow+self.targetFollows+self.neitherFollows},\n"

class MeasureCollector(Measure):
    def __init__(self):
        self.bothFollow = 0
        self.sourceFollows = 0
        self.targetFollows = 0
        self.neitherFollows = 0

    def Check(self,metricScores):
        source = [item[0] for item in metricScores]
        target = [item[1] for item in metricScores]

        sourceScore = not(False in source)
        targetScore = not(False in target)

        self.AddToScores(sourceScore,targetScore)

    def __str__(self) -> str:
        return 'TotalCompliance:\n' + self._getScoresAsString()

class ReadingSpeedMeasure(Measure):
    def __init__(self,sourceLimit,targetLimit):
        super().__init__(sourceLimit,targetLimit)

    def Check(self,source:srt.Subtitle,target:srt.Subtitle):
        time = self.GetSecondsFromTimedelta(source.start,source.end)
        sourceString = re.sub(r'(<.*?>|\{.*?\}|\n)','',source.content)
        targetString = re.sub(r'(<.*?>|\{.*?\}|\n)','',target.content)
        
        sourceScore = (len(sourceString)/time)<=self.sourceLimit
        targetScore = (len(targetString)/time)<=self.targetLimit

        self.AddToScores(sourceScore,targetScore)

        return [sourceScore,targetScore]

    def GetSecondsFromTimedelta(self,startTime:timedelta,endTime:timedelta):
        start = startTime.seconds + startTime.microseconds/1000000
        end = endTime.seconds + endTime.microseconds/1000000
        return float("{:.3f}".format(end-start))
    
    def __str__(self) -> str:
        return 'ReadingSpeedScores:\n' + self._getScoresAsString()

class SymbolCountMeasure(Measure):
    def __init__(self,sourceLimit,targetLimit):
        super().__init__(sourceLimit,targetLimit)

    def Check(self,source:srt.Subtitle,target:srt.Subtitle):
        sourceStrings = re.sub(r'(<.*?>|\{.*?\})','',source.content).split('\n')
        targetStrings = re.sub(r'(<.*?>|\{.*?\})','',target.content).split('\n')
        
        sourceScore = True
        targetScore = True

        for s in sourceStrings:
            if len(s) > self.sourceLimit:
                sourceScore = False
                break

        for t in targetStrings:
            if len(t) > self.targetLimit:
                targetScore = False
                break

        self.AddToScores(sourceScore,targetScore)

        return [sourceScore,targetScore]
    
    def __str__(self) -> str:
        return 'SymbolCountScores:\n' + self._getScoresAsString()

class Evaluator():
    def __init__(
        self,
        sourceGuidelines,
        targetGuidelines,
        subtitleReader
    ):
        self.sourceGuidelines = sourceGuidelines
        self.targetGuidelines = targetGuidelines
        self.subtitleReader = subtitleReader

    def Execute(self,sourceFile,targetFile,resultFile):
        # print(sourceFile)
        # print(targetFile)
        # print('–-----------------------------------------------')
        f = open(sourceFile, encoding='utf-8-sig')
        source: list[srt.Subtitle] = list(self.subtitleReader(f.read()))
        f.close()     

        f = open(targetFile, encoding='utf-8-sig')
        target: list[srt.Subtitle] = list(self.subtitleReader(f.read()))
        f.close()

        readingSpeed = ReadingSpeedMeasure(self.sourceGuidelines.speed,self.targetGuidelines.speed)
        symbolCount = SymbolCountMeasure(self.sourceGuidelines.symbols,self.targetGuidelines.symbols)
        totalCompliance = MeasureCollector()

        if len(source) == len(target):
            for x in range(len(source)):
                metricScores = []
                metricScores.append(readingSpeed.Check(source[x],target[x]))
                metricScores.append(symbolCount.Check(source[x],target[x]))
                totalCompliance.Check(metricScores)

            resultFile.writelines([str(readingSpeed),str(symbolCount),str(totalCompliance)])

        else:
            print('Amount of subtitles between source and target must be equal.')

if __name__ == "__main__":
    reader = srt.parse
    sourceGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_EN')
    targetGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_LV')

    evaluator = Evaluator(sourceGuidelines,targetGuidelines,reader)

    pathHyp = sys.path[-1]+'DataPreparator\\TranslatedOriginal\\'
    pathRef = sys.path[-1]+'DataPreparator\\Original\\'

    for file in variant:
        result = open(sys.path[-1]+'SubtitleEvaluator\\GuidelineScores\\'+file+'.txt', mode='w', encoding='utf-8-sig')
        folder = variant[file]
        for x in range(5):
            hypFile = pathHyp+folder+files[x]+file
            refFile = pathRef+files[x]+'srt'

            result.write(files[x]+'\n')

            evaluator.Execute(refFile,hypFile,result)
        result.close()

