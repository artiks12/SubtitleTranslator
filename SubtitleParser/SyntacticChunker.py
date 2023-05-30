import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.TaggedTextTokenizer import TaggedToken
from SubtitleParser.Configurations.Punctuations import closings

OpenPOS = ['ADJ','ADV','INTJ','NOUN','PROPN','VERB']
ClosedPOS = ['ADP','AUX','CCONJ','DET','NUM','PART','PRON','SCONJ']
OtherPOS = ['PUNCT','SYM','X']

def OpeningBracketApostrophe(
        word,
        last
    ):
    if (word.value == '"' or word.value == "'") and not(word.start == last.end):
        return True
    return word.value in closings.keys()

def GetSyntachticChunksAsStrings(
        taggedTokens: list[TaggedToken],
        hasSpaces: bool # Checks if the language uses spaces between words.
    ):
    result: list[str] = []
    temp: str = ''
    lastUpos = None
    last = None
    lastNonTag = None
    for token in taggedTokens:
        if len(temp) == 0:
            temp += token.value
        else:
            spaces = ' ' * (token.start-last.end)
            if last.upos == 'PUNCT':
                if not(OpeningBracketApostrophe(token,last)):
                    lastUpos = last.upos
                    lastNonTag = last
            elif last.upos not in ['OTAG','CTAG','ALIGN','NLINE']:
                lastUpos = last.upos
                lastNonTag = last
            if not(last.end == token.start) or not(hasSpaces):
                if not(lastUpos == None):
                    if last.upos == 'PUNCT' and token.upos == 'PUNCT' and not(last.end == token.start):
                        result.append(temp)
                        temp = ''
                    elif lastUpos in OtherPOS and not(last.end == token.start):
                        result.append(temp)
                        temp = ''
                    else:
                        if lastUpos in OpenPOS and token.upos in ClosedPOS:
                            result.append(temp)
                            temp = ''
                        # From Netflix subtitling guidelines
                        elif token.upos in ['ADP','CCONJ','SCONJ']:
                            result.append(temp)
                            temp = ''
                        # From BBC subtitling guidelines
                        elif lastUpos in ['VERB','AUX'] and token.upos not in ['VERB','AUX'] + OtherPOS:
                            result.append(temp)
                            temp = ''
                        elif lastUpos in OpenPOS and token.upos in OpenPOS:
                            if not(lastNonTag.dep == token.id or lastNonTag.id == token.dep):
                                result.append(temp)
                                temp = ''
            temp += spaces + token.value
        last = token
        
    if len(temp) > 0:
        result.append(temp)
    return result