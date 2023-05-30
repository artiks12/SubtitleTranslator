import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
import SubtitleParser.Alignment as Alignment

def Translator(metadata,SourceNLP,TargetNLP,translator) -> dict:
    offsetSource = 0
    offsetTarget = 0
    startSource = 0
    startTarget = 0
    metadata['sourceAlignments'] = {}
    metadata['targetAlignments'] = {}
    metadata['sourceTokens'] = {}
    metadata['targetTokens'] = {}
    metadata['targetWordRanges'] = []
    metadata['groupAlignmentOrder'] = []
    metadata['sentenceEnds'] = []
    for sentence in metadata['sentences']:
        alignmentData = translator.Translate(sentence,False,SourceNLP,TargetNLP,offsetSource,offsetTarget)
        alignments = Alignment.GetAlignment(alignmentData,offsetSource,offsetTarget,startSource,startTarget)
        metadata['sourceTokens'] = metadata['sourceTokens'] | alignmentData['sourceTokens']
        metadata['targetTokens'] = metadata['targetTokens'] | alignmentData['targetTokens']
        metadata['sourceAlignments'] = metadata['sourceAlignments'] | alignments['sourceAlignments']
        metadata['targetAlignments'] = metadata['targetAlignments'] | alignments['targetAlignments']
        metadata['targetWordRanges'].extend(alignments['targetWordRanges'])
        metadata['groupAlignmentOrder'].extend(alignments['groupAlignmentOrder'])
        metadata['sentenceEnds'].append(list(alignmentData['sourceTokens'].keys())[-1])
        offsetSource = len(metadata['sourceTokens'])
        offsetTarget = len(metadata['targetTokens'])
        startSource += len(sentence) + 1
        startTarget += len(alignmentData['translation']) + 1
    return metadata

def BatchTranslator(metadata,SourceNLP,TargetNLP,translator) -> dict:
    offsetSource = 0
    offsetTarget = 0
    startSource = 0
    startTarget = 0
    metadata['sourceAlignments'] = {}
    metadata['targetAlignments'] = {}
    metadata['sourceTokens'] = {}
    metadata['targetTokens'] = {}
    metadata['targetWordRanges'] = []
    metadata['groupAlignmentOrder'] = []
    metadata['sentenceEnds'] = []
    for sentence in metadata['sentences']:
        alignmentData = translator.Translate(sentence,False,SourceNLP,TargetNLP,offsetSource,offsetTarget)
        alignments = Alignment.GetAlignment(alignmentData,offsetSource,offsetTarget,startSource,startTarget)
        metadata['sourceTokens'] = metadata['sourceTokens'] | alignmentData['sourceTokens']
        metadata['targetTokens'] = metadata['targetTokens'] | alignmentData['targetTokens']
        metadata['sourceAlignments'] = metadata['sourceAlignments'] | alignments['sourceAlignments']
        metadata['targetAlignments'] = metadata['targetAlignments'] | alignments['targetAlignments']
        metadata['targetWordRanges'].extend(alignments['targetWordRanges'])
        metadata['groupAlignmentOrder'].extend(alignments['groupAlignmentOrder'])
        metadata['sentenceEnds'].append(list(alignmentData['sourceTokens'].keys())[-1])
        offsetSource = len(metadata['sourceTokens'])
        offsetTarget = len(metadata['targetTokens'])
        startSource += len(sentence) + 1
        startTarget += len(alignmentData['translation']) + 1
    return metadata