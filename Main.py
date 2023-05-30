from SubtitleParser.SubtitleTranslationSystem import MainTranslate
from DataPreparator.DataPreparator import MainPreparator
from SubtitleEvaluator.GuidelineEvaluator import MainGuideline
from SubtitleParser.SubtitleGuidelineMetrics import SubtitleGuidelineMetrics
from SubtitleParser.Translators.TildeTranslator import TildeTranslator
from simalign import SentenceAligner
from SubtitleParser.Translators.ids import *
from SubtitleSentenceTranslator import MainSentences
from SubtitleEvaluator.QualityEvaluator import MainQualityEvaluator

def GetTranslator(translator,system,id,hasAligner,aligner):
    if translator == 'tilde':
        return TildeTranslator(hasAligner,aligner,system,id)

def EvalGuide(args: list):
    if len(args) == 1 and args[0] == '-h':
        print('Available parameters for guideline evaluation method:')
        print('-f\t','Subtitle file name for both hypotheses and reference without extension.')
        print('-hf\t','Subtitle hypothesis file name without extension. "Sample" is default name.')
        print('-rf\t','Subtitle reference file name without extension. "Sample" is default name.')
        print('-hgv\t','Subtitling guideline metric values for hypotheses in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).')
        print('-hgp\t','Subtitling guideline metric values for hypotheses as predefined string (available: BBC_EN, BBC_LV). "BBC_EN" is default preset for hypotheses.')
        print('-rgv\t','Subtitling guideline metric values for reference in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).')
        print('-rgp\t','Subtitling guideline metric values for reference as predefined string (available: BBC_EN, BBC_LV). "BBC_LV" is default preset for reference.')
        print('-hp\t','Hypotheses file path. "SubtitleEvaluator/Hypotheses is used by default.')
        print('-rp\t','Reference file path. "SubtitleEvaluator/References/" is used by default.')
        print('-op\t','Output file path. "SubtitleEvaluator/GuidelineScores/" is used by default.')
    elif len(args)%2 == 1:
        print('Argument key and value amount is not even. Command Failed.')
    else:
        params = [(args[x],args[x+1]) for x in range(0,len(args),2)]
        hypFilename = 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP'
        refFilename = 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP'
        hypGuidelines = SubtitleGuidelineMetrics().GetPredefined("BBC_EN")
        refGuidelines = SubtitleGuidelineMetrics().GetPredefined("BBC_LV")
        pathHyp = 'SubtitleEvaluator/Hypotheses/'
        pathRef = 'SubtitleEvaluator/References/'
        outputPath = 'SubtitleEvaluator/GuidelineScores/'
        subtitleFormat = 'srt'
        for param in params:
            if not(param[0][0] == '-'):
                print(param[0],'is not a correct flag. Command failed.')
                return
            else:
                if param[0] == '-f': 
                    hypFilename = param[1]
                    refFilename = param[1]
                if param[0] == '-hf': hypFilename = param[1]
                if param[0] == '-rf': refFilename = param[1]
                if param[0] == '-hgv':
                    values = param[1].split(';')
                    if not(len(values) == 3):
                        print('Guideline metric value count is not 3.')
                        return
                    rows,symbols,speed = tuple([int(item) for item in values])
                    hypGuidelines = SubtitleGuidelineMetrics.GetCustom(rows,symbols,speed)
                if param[0] == '-hgp': hypGuidelines = SubtitleGuidelineMetrics.GetPredefined(param[1])
                if param[0] == '-rgv':
                    values = param[1].split(';')
                    if not(len(values) == 3):
                        print('Guideline metric value count is not 3.')
                        return
                    rows,symbols,speed = tuple([int(item) for item in values])
                    refGuidelines = SubtitleGuidelineMetrics.GetCustom(rows,symbols,speed)
                if param[0] == '-rgp': refGuidelines = SubtitleGuidelineMetrics.GetPredefined(param[1])
                if param[0] == '-hp': pathHyp = param[1]
                if param[0] == '-rp': pathRef = param[1]
                if param[0] == '-op': outputPath = param[1]
        MainGuideline(
            hypFilename,
            refFilename,
            hypGuidelines,
            refGuidelines,
            pathHyp,
            pathRef,
            outputPath,
            subtitleFormat,
            None
        )

def EvalQuality(args: list):
    if len(args) == 1 and args[0] == '-h':
        print('Available parameters for quality evaluation method:')
        print('-f\t','Subtitle file name for both hypotheses and reference without extension.')
        print('-hf\t','Subtitle hypothesis file name without extension. "Sample" is default name.')
        print('-rf\t','Subtitle reference file name without extension. "Sample" is default name.')
        print('-hp\t','Hypotheses file path. "SubtitleEvaluator/Hypotheses is used by default.')
        print('-rp\t','Reference file path. "SubtitleEvaluator/References/" is used by default.')
        print('-op\t','Output file path. "SubtitleEvaluator/GuidelineScores/" is used by default.')
    elif len(args)%2 == 1:
        print('Argument key and value amount is not even. Command Failed.')
    else:
        params = [(args[x],args[x+1]) for x in range(0,len(args),2)]
        hypFilename = 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP'
        refFilename = 'City.on.Fire.S01E03.1080p.WEB.H264-GGWP'
        pathHyp = 'SubtitleEvaluator/Hypotheses/'
        pathRef = 'SubtitleEvaluator/References/'
        outputPath = 'SubtitleEvaluator/GuidelineScores/'
        subtitleFormat = 'srt'
        for param in params:
            if not(param[0][0] == '-'):
                print(param[0],'is not a correct flag. Command failed.')
                return
            else:
                if param[0] == '-f': 
                    hypFilename = param[1]
                    refFilename = param[1]
                if param[0] == '-hf': hypFilename = param[1]
                if param[0] == '-rf': refFilename = param[1]
                if param[0] == '-hp': pathHyp = param[1]
                if param[0] == '-rp': pathRef = param[1]
                if param[0] == '-op': outputPath = param[1]
        MainQualityEvaluator(
            hypFilename,
            refFilename,
            pathHyp,
            pathRef,
            outputPath,
            subtitleFormat,
            None
        )

def ParalelData(args: list):
    if len(args) == 1 and args[0] == '-h':
        print('Available parameters for paralel data method:')
        print('-f\t','Subtitle source and target file name without extension. "Sample" is default name.')
        print('-sf\t','Subtitle source file name without extension. "Sample" is default name.')
        print('-tf\t','Subtitle target file name without extension. "Sample" is default name.')
        print('-sl\t','Source language for subtitle file. "en" is default source language.')
        print('-tl\t','Target language for translation. "lv" is default target language.')
        print('-tn\t','Should target language subtitles be normalized. True - Yes. False - No. Target subtitles are normalized by default.')
        print('-ip\t','Input file path. "SubtitleParser/Subtitles/" is used by default.')
        print('-op\t','Output file path. "DataPreparator/Result/" is used by default.')
    elif len(args)%2 == 1:
        print('Argument key and value amount is not even. Command Failed.')
    else:
        params = [(args[x],args[x+1]) for x in range(0,len(args),2)]
        sourceFile = 'Sample'
        targetFile = 'Sample'
        sourceLang = 'en'
        targetLang = 'lv'
        needTargetNormalize = True
        pathInput = 'SubtitleParser/Subtitles/'
        pathOutput = 'DataPreparator/Result/'
        subtitleFormat = 'srt'
        for param in params:
            if not(param[0][0] == '-'):
                print(param[0],'is not a correct flag. Command failed.')
                return
            else:
                if param[0] == '-f': 
                    sourceFile = param[1]
                    targetFile = param[1]
                if param[0] == '-sf': sourceFile = param[1]
                if param[0] == '-tf': targetFile = param[1]
                if param[0] == '-sl': sourceLang = param[1]
                if param[0] == '-tl': targetLang = param[1]
                if param[0] == '-tn': needTargetNormalize = bool(param[1])
                if param[0] == '-ip': pathInput = param[1]
                if param[0] == '-op': pathOutput = param[1]
        MainPreparator(
            sourceFile,
            targetFile,
            needTargetNormalize,
            sourceLang,
            targetLang,
            pathInput,
            pathOutput,
            subtitleFormat
        )

def Translate(args: list):
    if len(args) == 1 and args[0] == '-h':
        print('Available parameters for translate method:')
        print('-f\t','Subtitle file name without extension. "Sample" is default name.')
        print('-sl\t','Source language for subtitle file. "en" is default source language.')
        print('-tl\t','Target language for translation. "lv" is default target language.')
        print('-gv\t','Subtitling guideline metric values in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).')
        print('-gp\t','Subtitling guideline metric values as predefined string (available: BBC_EN, BBC_LV). "BBC_LV" is default preset.')
        print('-sam\t','Model used for SimAlign. mBERT is used by default.')
        print('-sat\t','Tokenizer used by SimAlign. "bpe" is used by default.')
        print('-ip\t','Input file path. "SubtitleParser/Subtitles/" is used by default.')
        print('-op\t','Output file path. "SubtitleParser/Result/" is used by default.')
        print('-t\t','Translator to be used in format - name:client_id:system_id:aligner')
        print('-wa\t','Should word aligner be used. True - Yes. False - No. Word aligner is used by default')
    elif len(args)%2 == 1:
        print('Argument key and value amount is not even. Command Failed.')
    else:
        params = [(args[x],args[x+1]) for x in range(0,len(args),2)]
        filename = 'Sample'
        subtitlingGuidelines = SubtitleGuidelineMetrics().GetPredefined("BBC_LV")
        sourceLang = 'en'
        targetLang = 'lv'
        pathInput = 'SubtitleParser/Subtitles/'
        pathOutput = 'SubtitleParser/Result/'
        subtitleFormat = 'srt'
        wordAligner = True
        simAlign = SentenceAligner(model='bert', token_type='bpe', matching_methods="maifr")
        translator = TildeTranslator(True,simAlign,system_id,client_id)
        for param in params:
            if not(param[0][0] == '-'):
                print(param[0],'is not a correct flag. Command failed.')
                return
            else:
                if param[0] == '-f': filename = param[1]
                if param[0] == '-sl': sourceLang = param[1]
                if param[0] == '-tl': targetLang = param[1]
                if param[0] == '-gv':
                    values = param[1].split(':')
                    if not(len(values) == 3):
                        print('Guideline metric value count is not 3.')
                        return
                    rows,symbols,speed = tuple([int(item) for item in values])
                    subtitlingGuidelines = SubtitleGuidelineMetrics.GetCustom(rows,symbols,speed)
                if param[0] == '-gp': subtitlingGuidelines = SubtitleGuidelineMetrics.GetPredefined(param[1])
                if param[0] == '-sam': simAlign.model = param[1]
                if param[0] == '-sat': simAlign.token_type = param[1]
                if param[0] == '-ip': pathInput = param[1]
                if param[0] == '-op': pathOutput = param[1]
                if param[0] == '-wa': wordAligner = bool(param[1])
                if param[0] == '-t': 
                    values = param[1].split(':')
                    translator = GetTranslator(values[0],values[1],values[2],bool(values[3]),simAlign)
        if wordAligner:
            MainTranslate(
                filename,
                subtitlingGuidelines,
                simAlign,
                translator,
                sourceLang,
                targetLang,
                pathInput,
                pathOutput,
                subtitleFormat
            )
        else:
            MainSentences(
                filename,
                subtitlingGuidelines,
                translator,
                sourceLang,
                targetLang,
                pathInput,
                pathOutput,
                subtitleFormat,
            )

if __name__ == "__main__":
    print('Welcome to subtitle translation program!')
    print('To see all commands, type "commands". To see command parameters, write command name with -h flag.')
    command = ""
    
     # Programm works as long as we don't make it stop with "q" or "quit" command
    while command != "q" and command != "quit":
        command = input("> ")
        method = command.split()

        if method[0] not in ['translate','evalGuide','evalQuality','paralelData',"commands",'quit']:
            print(method[0],'is not a valid command!')
            command = ''
        else:
            if method[0] == 'commands':
                print('translate - translate subtitle files')
                print('evalGuide - evaluate subtitle file compliance to guidelines')
                print('evalQuality - evaluate subtitle quality metrics (Sigma,BLEU,chrF++,TER)')
            elif method[0] == 'translate':
                Translate(method[1:])
            elif method[0] == 'evalGuide':
                EvalGuide(method[1:])
            elif method[0] == 'evalQuality':
                EvalQuality(method[1:])
            elif method[0] == 'paralelData':
                ParalelData(method[1:])
