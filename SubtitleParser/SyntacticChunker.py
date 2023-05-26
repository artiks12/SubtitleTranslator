import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.TaggedTextTokenizer import TaggedTextTokenizer, TaggedToken
from SubtitleParser.Configurations.Punctuations import closings
import stanza

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

if __name__ == "__main__":
    # nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse,mwt,constituency', use_gpu=True)
    # text = 'To answer to him that she sleeps.'
    
    nlp = stanza.Pipeline(lang='lv', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    # text = 'Tas ir, izjokot šos puišus ir bijis viens no mūsu draudzības pamatā esošajiem pamudinājumiem.'
    # text = 'Līgo nakts zaļumballē ar tautā iemīlētām un populārām dziesmām līgotājus priecēs Andris Baltacis un grupa “Baltie lāči”.'
    # text = '"And along with that is the <b>importance</b> of stronger national security.'
    text = 'Otrā runātāja turpinājums tepat.'

    # nlp = stanza.Pipeline(lang='ja', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    # text = 'その犬はサッカーをしています。'
    
    test1 = TaggedTextTokenizer(text,nlp,True)

    for token in test1.tokens:
        print(token.id,token.start,token.end,token.value,token.upos)

    chunks = GetSyntachticChunksAsStrings(test1.tokens,False)
    for chunk in chunks:
        print(chunk)
