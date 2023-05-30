# SubtitleTranslator
This is a program writen in python that translates SRT format subtitles. The program was created as part of university bachelors work.

# Used Packages
<ul>
<li>
<a href="https://pypi.org/project/srt/">srt</a> - library that stores srt subtitles as objects
</li>
<li>
<a href="https://github.com/tilde-nlp/mt-api-python-demo">tilde MT API</a> - created by SIA Tilde.Library allows the use of Tilde MT in solutiuon. Requires client_id.
</li>
<li>
<a href="https://github.com/cisnlp/simalign">SimAlign</a> - created by Sabet M.J., Dufter P., Yvon F., Schutze H. (2021). Used for acquiring word alignments if MT API or MT system does not return word alignment data. Uses MT license.
</li>
<li>
<a href="https://github.com/fyvo/EvalSubtitle">EvalSubtitle</a> - created by Karakanta A., Buet F., Cettolo M. and Yvon F. (2022). Used for subtitle segmentation evaluation. Already comes with <a href="https://github.com/mjpost/sacrebleu">sacreBLEU</a> to evaluate MT systems. EvalSubtitle is licensed under a <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>
</li>
</ul>

# File Structure
Solution consists of 4 folders:
<ul>
<li>
DataPreparator - stores data used and prepared for evaluation.
</li>
<li>
SubtitleEvaluator - stores scripts for data evaluation and evaluation results.
</li>
<li>
SubtitleParser - stores the main program that evaluates subtitles.
</li>
</ul>

Root folder has a script file "SubtitleSentenceTranslator.py" that translates subtitles in the same way as the main program, only difference being that no word alignments are aquired during script process, meaning that no ellipses and no tags are removed from within text and text is divided into subtitles, using syntactic chunks.

## DataPreparator
Folder consists of 4 other folders:
<ul>
<li>
Original - stores subtitle files downloaded from OpenSubtitles with no changes.
</li>
<li>
Paralel - stores subtitle files from original files with tags, alignments and formatting symbols removed and files contatin only paralel subtitles between languages.
</li>
<li>
Translated - stores machine translated original subtitle files.
</li>
<li>
TranslatedParalel - stores machine translated original subtitle files with tags, alignments and formatting symbols removed and files contatin only paralel subtitles aquired from subtitle files in "Paralel" folder.
</li>
</ul>

Folders "Translated" and "TranslatedParalel" consist of 4 subfolders that store machine translated subtitles depending on translation method:
<ul>
<li>
Docuemnt - subtitles translated with Tilde document translator
</li>
<li>
Sentences - subtitles translated, using "SubtitleSentenceTranslator.py" script in root folder.  
</li>
<li>
SimAlign - subtitles translated with this program, using Tilde MT API and word alignments aquired with SimAlign.
</li>
<li>
Tilde - subtitles translated with this program, using Tilde MT API and word alignments aquired with Tilde MT API.
</li>
</ul>

DataPrepeartor.py script takes two subtitle files as input and acquires paralel subtitles (check description of "Paralel" folder).


## SubtitleEvaluator
Folder consists of 3 other folders:
<ul>
<li>
GuidelineScores - stores results of subtitle compliance to subtitling guidelines.
</li>
<li>
QualityScores - stores Sigma, BLEU, chrF++ and TER results of translated subtitle files.  
</li>
<li>
SubERscores - stores SubER results of translated subtitle files.
</li>
</ul>

Files in all folders are text files and should be interteded like this:
<ul>
<li>
tilde.document.txt - results for subtitles translated with Tilde document translator.
</li>
<li>
tilde.Sentences.txt - results for subtitles translated, using "SubtitleSentenceTranslator.py" script in root folder.
</li>
<li>
tilde.SimAlign.txt - results for subtitles translated with this program, using Tilde MT API and word alignments aquired with SimAlign.
</li>
<li>
tilde.tilde.txt - results for subtitles translated with this program, using Tilde MT API and word alignments aquired with Tilde MT API.
</li>
</ul>

Folder consists of 3 python script files:
<ul>
<li>
GuidelineEvaluator.py - used to evaluate subtitle compliance to subtitling guidelines.
</li>
<li>
QualityEvaluator.py - used to evaluate Sigma, BLEU, chrF++ and TER scores for subtitles. Code taken from EvalSubtitle.
</li>
</ul>

## SubtitleParser
Folder consists of 4 other folders:
<ul>
<li>
Configurations - stores values used throughout solution like subtitle element types (Constants.py) and punctuations suported by the system (Punctuations.py).
</li>
<li>
Result - default output folder for translated subtitle files 
</li>
<li>
Subtitles - default input folder for translated subtitle files
</li>
<li>
Translators - stores MTSystem class and its subclasses. The subclasses use MT system APIs or systems themselves to translate text and aquire word alignments.
</li>
</ul>

Folder consists of 15 script files:
<ul>
<li>
Alignment.py - uses alignment info aquired by MT API or SimAlign to get full alignment and alignment group data.
</li>
<li>
Caption.py - contains Caption class that has functions for text and subtitle element processing.
</li>
<li>
Combiner.py - contains functions for combining subtitles together.
</li>
<li>
CustomTokenizer.py - uses existing Stanza tokenizer but modified to aquire ellipses and seperate text in brackets from other text. 
</li>
<li>
CustomWordAligner.py - uses SimAlign tool to acquire word alignments
</li>
<li>
SentenceMetadataFunctions.py - contains functions for sentence processing that includes removal of ellipses or fixing tokens when different tokenizer get different tokens.
</li>
<li>
Sentences.py - contains base class for storing and combining combined subtitles.
</li>
<li>
SubtitleElementTokenizer.py - contains functions that aquire subtitle elements from tokens.
</li>
<li>
SubtitleGuidelineMetrics.py - contains a class that stores info about subtitling guideline metric values (reading speed and symbol count).
</li>
<li>
SubtitleTranslationSystem.py - main file that translates subtitles.
</li>
<li>
SyntacticChunker.py - contains function that divides text into syntactic chunks. Works with tagged text.
</li>
<li>
TaggedTextTokenizer.py - contains functions that process tags alignment symbols and newline symbols so that text can be correctly tokenized
</li>
<li>
TextBreaker.py - contatins functions that use word alignments and syntactic chunks to divide text into subtitles and text lines.
</li>
<li>
TranslationSentences.py - contains execution of all text translation steps such as acquiring whole sentences, removal of ellipses, translation, ellipse reinsertion and dividing text into subtitles and text lines.
</li>
<li>
Translator.py - uses functions from MTSystem class and Alignment.py to acquire translations and word alignments
</li>
</ul>

# Using the program
There is a CLI for this program that can be opened by running the following command in terminal from root folder:
```console
python Main.py
```
evalGuide and evalQuality require both subtitle files to contain equal amount of subtitles.
## Translating subtitle files
Assuming that we want to translate a file named "Sample.srt". To translate a subtitle file, place it in SubtitleParser/Subtitles folder and run the following command:
```console
> translate -f Sample
```
Result is stored in SubtitleParser/Result folder. translate method has the following parameters:
```console
-f      Subtitle file name without extension. "Sample" is default name.
-sl     Source language for subtitle file. "en" is default source language.
-tl     Target language for translation. "lv" is default target language.
-gv     Subtitling guideline metric values in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).
-gp     Subtitling guideline metric values as predefined string (available: BBC_EN, BBC_LV). "BBC_LV" is default preset.
-sam    Model used for SimAlign. mBERT is used by default.
-sat    Tokenizer used by SimAlign. "bpe" is used by default.
-ip     Input file path. "SubtitleParser/Subtitles/" is used by default.
-op     Output file path. "SubtitleParser/Result/" is used by default.
-t      Translator to be used in format name:client_id:system_id:aligner.
-wa     Should word aligner be used. True - Yes. False - No. Word aligner is used by default.
```

## Acquiring paralel data
Assuming that we want to get paralel data from files "SampleSource.srt" and "SampleTarget.srt". To acquire paralel data, place both "SampleSource.srt" and "SampleTarget.srt" in SubtitleParser/Subtitles folder and run the following command:
```console
> paralelData -sf SampleSource -tf SampleTarget
```
Result is stored in DataPreparator/Result folder. paralelData method has the following parameters:
```console
-f      Subtitle source and target file name without extension. "Sample" is default name.
-sf     Subtitle source file name without extension. "Sample" is default name.
-tf     Subtitle target file name without extension. "Sample" is default name.
-sl     Source language for subtitle file. "en" is default source language.
-tl     Target language for translation. "lv" is default target language.
-tn     Should target language subtitles be normalized. True - Yes. False - No. Target subtitles are normalized by default.
-ip     Input file path. "SubtitleParser/Subtitles/" is used by default.
-op     Output file path. "DataPreparator/Result/" is used by default.
```

## Evaluating subtitle compliance to subtitling guidelines
Assuming that we want to compare compliance to subtitling guidlines for "SampleSource.srt" and "SampleTarget.srt". To compare compliance, place "SampleSource.srt" in SubtitleEvaluator/Hypotheses folder and "SampleTarget.srt" in SubtitleEvaluator/References folder and run the following command:
```console
> evalGuide -hf SampleSource -rf SampleTarget
```
Result is stored in SubtitleEvaluator/GuidelineScores folder. evalGuide method has the following parameters:
```console
-f      Subtitle file name for both hypotheses and reference without extension.
-hf     Subtitle hypothesis file name without extension. "Sample" is default name.
-rf     Subtitle reference file name without extension. "Sample" is default name.
-hgv    Subtitling guideline metric values for hypotheses in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).
-hgp    Subtitling guideline metric values for hypotheses as predefined string (available: BBC_EN, BBC_LV). "BBC_EN" is default preset for hypotheses.
-rgv    Subtitling guideline metric values for reference in format l:s:r (l - line count, s - symbol count, r - reading speed in characters per second).
-rgp    Subtitling guideline metric values for reference as predefined string (available: BBC_EN, BBC_LV). "BBC_LV" is default preset for reference.
-hp     Hypotheses file path. "SubtitleEvaluator/Hypotheses is used by default.
-rp     Reference file path. "SubtitleEvaluator/References/" is used by default.
-op     Output file path. "SubtitleEvaluator/GuidelineScores/" is used by default.
```

## Evaluating subtitle quality to reference
Assuming that we want to get subtitle quality for "SampleSource.srt" with respect to "SampleTarget.srt". To evaluate subtitle quality, place "SampleSource.srt" in SubtitleEvaluator/Hypotheses folder and "SampleTarget.srt" in SubtitleEvaluator/References folder and run the following command:
```console
> evalQuality -hf SampleSource -rf SampleTarget
```
Result is stored in SubtitleEvaluator/QualityScores folder. evalQuality method has the following parameters:
```console
-f      Subtitle file name for both hypotheses and reference without extension.
-hf     Subtitle hypothesis file name without extension. "Sample" is default name.
-rf     Subtitle reference file name without extension. "Sample" is default name.
-hp     Hypotheses file path. "SubtitleEvaluator/Hypotheses is used by default.
-rp     Reference file path. "SubtitleEvaluator/References/" is used by default.
-op     Output file path. "SubtitleEvaluator/GuidelineScores/" is used by default.
```

# Interpreting guideline compliance scores
The result of evalGuide method is a text file with following content:
```console
ReadingSpeedScores:
	bothFollow:349,
	sourceFollows:42,
	targetFollows:83,
	neitherFollows:206,
SymbolCountScores:
	bothFollow:537,
	sourceFollows:30,
	targetFollows:95,
	neitherFollows:18,
TotalCompliance:
	bothFollow:301,
	sourceFollows:41,
	targetFollows:114,
	neitherFollows:224,
```
<b>ReadingSpeedScores</b> reffers to subtitle reading speed scores, <b>SymbolCountScores</b> reffers to subtitle symbol count per line scores where all lines cannot exceed subtitling guideline limit and <b>TotalCompliance</b> reffers to both ReadingSpeed and SymbolCount compliance for subtitles assumimg that all subtitles do not exceed more than 2 text lines. The numbers count the amount of subtitles where:
<ul>
<li>
Both source and target subtitles comply to metric (<b>bothFollow</b>)
</li>
<li>
Only source subtitles comply to metric (<b>sourceFollows</b>)
</li>
<li>
Only target subtitles comply to metric (<b>targetFollows</b>)
</li>
<li>
Neither source and target subtitles comply to metric (<b>neitherFollows</b>)
</li>
</ul>

# Adding Machine translator to solution
In SubtitleParser/Translators folder create a python file that will store machine translator class. This class needs to inherit from MTSystem class. Let's take TildeTranslator class as an example:
```console
import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Translators.MTSystem import MTSystem
import requests

class TildeTranslator(MTSystem):
    def __init__(
        self,
        hasAligner,
        aligner,
        system_id,
        client_id,
    ) -> None:
        super().__init__(hasAligner,aligner,'tilde')
        self.system_id = system_id
        self.client_id = client_id
```
<ul>
<li>
hasAligner (mandatory) - boolean that tells if MT API word aligner is used.
</li>
<li>
aligner (mandatory) - instance of default aligner. Use SimAlign.
</li>
<li>
system_id (if necessary) - which machine translation system to use.
</li>
<li>
client_id (if necessary) - client id that allows user to use MT API.
</li>
</ul>
in "super().__init__(hasAligner,aligner,'tilde')" instead of tilde you should add the name of your machine translation system.

There should be a Translate method that is called when translation is neede for text.
```console
def Translate(self,text,withTags,SourceNLP,TargetNLP,offsetSource,offsetTarget):
	data = self.__apiCall(text,withTags)

	if self.hasAligner:
		return self.GetTildeMetadata(data,text,offsetSource,offsetTarget,SourceNLP,TargetNLP)
	return self.GetTranslationMetadata(text,data['translation'],SourceNLP,TargetNLP,offsetSource,offsetTarget) 
```
Here __apiCall should return all translation data including:
<ul>
<li>
source text tokens 
</li>
<li>
target text tokens
</li>
<li>
word alignments
</li>
<li>
token ranges in text.
</li>
<li>
translation.
</li>
</ul>

After getting all data, Translate method checks if machine translator word aligner is used. If no then GetTranslationMetadata should be called (It is already made in MTSystem class). Otherwise you should implement a method that gets all data in specific format:
```console
def GetTildeMetadata(self,data,text,offsetSource,offsetTarget,SourceNLP,TargetNLP):
	(sourceTokens,targetTokens) = self.GetTokensForSourceAndTarget(text,data,offsetSource,offsetTarget)
	alignmentData = {
		'sourceTokens':sourceTokens,
		'targetTokens':targetTokens,
		'sourceWordRanges':data['sourceWordRanges'],
		'targetWordRanges':data['targetWordRanges'],
		'wordAlignment':data['wordAlignment'],
		'confidentWordAlignment':data['confidentWordAlignment'],
		'translation':data['translation']
	}
	if len(data['wordAlignment']) == 0:
		alignmentData = self.GetTranslationMetadata(text,data['translation'],SourceNLP,TargetNLP,offsetSource,offsetTarget)
	return alignmentData
```
Key values may be different for each machine translator and every machine translator can have different output values, but Translate method needs to return all data with keys as shown for alignmentData dictionary. Assuming we Translate "This is a sentence." to latvian which would be "Šis ir teikums." alignmentData should contain all data in following formats:
```console
alignmentData = {
	'sourceTokens': {0: 'This', 1: 'is', 2: 'a', 3: 'sentence', 4: '.'},
	'targetTokens': {0: 'Šis', 1: 'ir', 2: 'teikums', 3: '.'},
	'sourceWordRanges': [ [0, 4], [5, 7], [8, 9], [10, 18], [18, 19] ],
	'targetWordRanges': [ [0, 3], [4, 6], [7, 14], [14, 15] ],
	'wordAlignment': [ [0, 0], [1, 1], [2, 2], [3, 2], [4, 3] ],
	'confidentWordAlignment': [ [0, 0], [1, 1], [2, 2], [3, 2], [4, 3] ],
	'translation': 'Šis ir teikums'
}
```
confidentWordAlignment value can be None because it is not currently used. Every token from source tokens should be aligned to at least one token from target and vice versa.
The final if statement in GetTildeMetadata is used in case no word alignment data is returned by API, which is the case for the example above so your method should include such statement as well.

In Main.py file in GetTranslator method add if statement for your machine translation system. Assuming the translation system class is "MyMTsystem" and name added in its constructor is "my_system" you should add the following if statement in GetTranslator method:
```console
if translator == 'my_system':
	return MyMTsystem(hasAligner,aligner,system,id)
```
The result would look like this:
```console
def GetTranslator(translator,system,id,hasAligner,aligner):
    if translator == 'tilde':
        return TildeTranslator(hasAligner,aligner,system,id)
	if translator == 'my_system':
		return MyMTsystem(hasAligner,aligner,system,id)
```

# Licensing
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
