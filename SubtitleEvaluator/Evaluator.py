import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))

from datetime import timedelta
import srt
import re
from SubtitleParser.SubtitleGuidelineMetrics import SubtitleGuidelineMetrics

class Measure():
    def __init__(self,sourceLimit,targetLimit):
        self.bothFollow = 0
        self.sourceFollows = 0
        self.targetFollows = 0
        self.neitherFollows = 0
        self.sourceLimit = sourceLimit
        self.targetLimit = targetLimit

    def AddToScores(self,source,target):
        if source and target: self.bothFollow += 1
        if not(source) and not(target): self.neitherFollows += 1
        if source and not(target): self.sourceFollows += 1
        if not(source) and target: self.targetFollows += 1

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

    def Execute(self,sourceFile,targetFile):
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

            print(readingSpeed)
            print(symbolCount)
            print(totalCompliance)

        else:
            print('Amount of subtitles between source and target must be equal.')

if __name__ == "__main__":
    reader = srt.parse
    sourceGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_EN')
    targetGuidelines = SubtitleGuidelineMetrics().GetPredefined('BBC_LV')

    evaluator = Evaluator(sourceGuidelines,targetGuidelines,reader)

    filenames = [
        # 'Lucky.Hank.S01E06.WEB'
        'CSI.Vegas.S02E18.WEBRip.x264.Hi',
        # 'Sample3',
    ]
    sourceLanguage = 'en'
    targetLanguage = 'lv'
    for filename in filenames:
        sourcefile = sys.path[0]+'\\Data\\'+filename+'.'+sourceLanguage+'.srt'
        targetfile = sys.path[0]+'\\Data\\'+filename+'.'+targetLanguage+'.srt'

        result = evaluator.Execute(sourcefile,targetfile)
        