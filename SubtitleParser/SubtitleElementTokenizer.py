import stanza
from typing import TypeVar
import re

import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Configurations.Punctuations import *
from SubtitleParser.Configurations.Tags import *
from SubtitleParser.Configurations import Constants
from SubtitleParser.TaggedTextTokenizer import TaggedToken, TaggedTextTokenizer

SubtitleElementType = TypeVar("SubtitleElementType", bound="SubtitleElement")

class SubtitleElement():
    """
        Subtitle element class.
        A higher level token that turns text tokens into subtitle elements.
        Such elements include speaker labels and dashes, sound effect constructions,
        symbols that wrap around text (music notes, hash symbol, etc.).
    """
    # Initialize subtitle element.
    def __init__(
            self,
            element: TaggedToken | SubtitleElementType, # Tagged token or subtitle element.
            subType: str, # Subtitle element type (check Constants.py).
            id: str, # Subtitle element identifier. A "caption-index" pair.
        ) -> None:
        self.subType: str = subType
        self.value: str = element.value
        self.id: str = id
        self.start: int = element.start
        self.end: int = element.end
        self.start_char: int = element.start_char
        self.end_char: int = element.end_char
        self.tag: str | None = element.tag

    # Method to convert subtitle element to string.
    def __str__(
            self
        ) -> str:
        return self.value
    
    # Method to create a copy of the element, where start and end indexes can change.
    def copy(
            self,
            newStart: int|None = None, # New starting index. If None then current value is used.
            newId: str| None = None,
            newValue: str|None = None
        ):
        obj = SubtitleElement(self,self.subType,self.id)
        if not(newStart == None):
            obj.start = newStart
            obj.end = newStart+len(obj.value)
        if not(newId == None):
            obj.id = newId
        if not(newValue == None):
            obj.value = newValue  
        return obj
    
    # Method to get element index form element id.
    def GetIndex(
            self
        ) -> int:
        return int(self.id.split('-')[1])
    
    # Method to get caption index form element id.
    def GetCaption(
            self
        ) -> int:
        return int(self.id.split('-')[0])

class SubtitleElementTokenizer():
    """
        Subtitle Elment Tokenizer class.
        Takes tokenized text elements and turns them into subtitle elmenets.
        Check Constants.py file to learn about subtitle element types.
    """
    # Initialize tokenizer.
    def __init__(
            self,
            tokens: list[TaggedToken], # Tokenized text elements.
            captionId: int, # Subtitle identifier in subtitle file.
        ):
        self.parts = self.__getElements(tokens,captionId)

    # Method to get last inserted non tag element.
    def __getLast(
            self,
            elements: list[SubtitleElement]
        ) -> SubtitleElement | None:
        for elem in reversed(elements):
            if not(elem.subType in [Constants.TAG_OPEN, Constants.TAG_CLOSE, Constants.ALIGN]):
                return elem
        return None
    
    # Method to get next comming non tag element.
    def __getNext(
            self,
            elements: list[TaggedToken]
        ) -> TaggedToken | None:
        for elem in elements:
            if not(elem.upos in ['OTAG','CTAG','ALIGN']):
                return elem
        return None
    
    # Method to get HTML tag type.
    def __getTagType(
            self,
            tag: str # Tag POS value.
        ) -> str:
        if tag == 'OTAG': return Constants.TAG_OPEN
        return Constants.TAG_CLOSE

    # Methot to turn text tokens into subtitle tokens.
    def __getElements(
            self,
            tokens: list[TaggedToken], # Tokenized text elements.
            captionId: int # Subtitle identifier in subtitle file.
        ) -> list[SubtitleElement]:
        needSpeaker = True # Checks if it is necessary to check if element is speaker identifier.
        isText = False # Checks if text shown on screen is present.
        isEffect = False  # Checks if text is in square brackets.
        result: list[SubtitleElement] = [] # Result list.
        count: int = 0 # Number of elements inserted in result list.
        symbols: list[int] = [] # list of symbol element indexes.
        for token in tokens:
            index = str(captionId) + '-' + str(token.id) # Subtitle elment index.
            subType = '' # Subtitle type.
            
            # Aquire subtitle element type.
            # Token is an HTML tag.
            if token.upos in ['OTAG','CTAG']:
                subType = self.__getTagType(token.upos)
            # Token is not an HTML tag, but is an alignment element.
            elif token.upos == 'ALIGN':
                subType = Constants.ALIGN
            # Token is not an HTML tag and an alignment element.
            else:
                # Token is a symbol.
                if self.__isSymbol(token.upos,token.value):
                    # Symbols wrapping around text lines are considdered as symbols.
                    if isText == False or re.match(r'(♪+)',token.value):
                        subType = Constants.SYMBOL
                    # Symbols in-between text are considdered as words.
                    else:
                        subType = Constants.WORD
                        symbols.append(token.id) # For checking later.
                # Token is a newline.
                elif token.upos == 'NLINE':
                    subType = Constants.NEWLINE
                    # Reset isText and newline values for new lines.
                    isText = False
                    needSpeaker = True
                    # All symbols wrapping around text are changed to symbol type.
                    for s in symbols:
                        result[s].subType = Constants.SYMBOL
                # The rest of tokens.
                else:
                    symbols.clear() # Since all symbols wrapped around words are coinsidered as words.
                    last = self.__getLast(result)
                    next = self.__getNext(tokens[count+1:])
                    subType = self.__getSubtitleType(token,last,next,needSpeaker,isEffect)

                    # Makes it possible to have speaker labels with multiple words
                    if subType == Constants.SPEAKER and token.value == ':':
                        for r in reversed(result):
                            if r.subType == Constants.NEWLINE: break
                            elif r.subType == Constants.WORD and r.value.isupper():
                                result[r.GetIndex()].subType = Constants.SPEAKER
                    isText = True
                    # Check if proceding text is in square brackets.
                    if subType == Constants.EFFECT_OPEN:
                        isEffect = True
                    elif subType == Constants.EFFECT_CLOSE:
                        isEffect = False
                    # If speaking text starts then speaker identifier search is done.
                    if not(subType == Constants.SPEAKER) and not(token.value.isupper()):
                        needSpeaker = False

            result.append(SubtitleElement(token,subType,index))
            count += 1

        # All symbols wrapping around text are changed to symbol type.
        if len(symbols)>0:
            for s in symbols:
                result[s].subType = Constants.SYMBOL

        return result

    # Method to get subtitle type for punctuation element.
    def __getPunctuationType(
            self,
            elem: TaggedToken, # Current element.
            last: SubtitleElement | None, # Last added subtitle element.
            next: TaggedToken | None # Next comming subtitle element.
        ) -> str:
        if last == None:
            nextDistance = next.start_char - elem.end_char # Distance between current and next element.
            if nextDistance == 0:
                return Constants.PUNCT_LEFT
        elif elem.value == ':' and last.subType == Constants.EFFECT_CLOSE:
            return Constants.SPEAKER
        elif next == None:
            lastDistance = elem.start_char - last.end_char # Distance between current and last element.
            if lastDistance == 0:
                return Constants.PUNCT_RIGHT
        else:
            lastDistance = elem.start_char - last.end_char
            nextDistance = next.start_char - elem.end_char

            # Current element is in-between two elements.
            if lastDistance == 0 and nextDistance == 0:
                return Constants.PUNCT_IN
            # Current element is attached to last element from right.
            elif lastDistance == 0:
                return Constants.PUNCT_RIGHT
            # Current element is attached to next element from left.
            elif nextDistance == 0:
                return Constants.PUNCT_LEFT
        return Constants.PUNCT_OUT
    
    def __getQuoteType(
            self,
            elem: TaggedToken, # Current element.
            last: SubtitleElement | None, # Last added subtitle element.
            next: TaggedToken | None # Next comming subtitle element.
        ) -> str:
            if last == None:
                return Constants.WORD_OPEN
            if next == None:
                return Constants.WORD_CLOSE
            
            lastDistance = elem.start_char - last.end_char
            
            if lastDistance == 0:
                return Constants.WORD_CLOSE
            return Constants.WORD_OPEN

    # Method to get technical information about token.
    def __getSubtitleType(
            self,
            elem: TaggedToken, # Current element
            last: SubtitleElement | None, # Last added subtitle element
            next: TaggedToken | None, # Next comming subtitle element
            needSpeaker: bool, # Checks if it is necessary to check if element is speaker identifier.
            isEffect: bool # Checks if text is in square brackets.
        ) -> str:
        result: str = '' # Resulting subtitle type.
        # Subtitle element has speaker type.
        if self.__isSpeaker(elem,last,next,needSpeaker):
            result = Constants.SPEAKER
        # Subtitle element is opening bracket.
        elif elem.value in brackets.keys():
            result = Constants.EFFECT_OPEN
        # Subtitle element is closing bracket.
        elif elem.value in brackets.values():
            result = Constants.EFFECT_CLOSE
        # Subtitle element is in brackets.
        elif isEffect:
            result = Constants.EFFECT
        # Subtitle element is opening quote.
        elif elem.value in quotes.keys():
            result = Constants.WORD_OPEN
        # Subtitle element is closing quote.
        elif elem.value in quotes.values():
            result = Constants.WORD_CLOSE
        # Subtitle element is quote or apostrophe. Checks if it opens or closes text.
        elif elem.value == '"' or elem.value == "'":
            result = self.__getQuoteType(elem,last,next)
        # Subtitle element has text punctuation type.
        elif elem.value in punctuations or elem.upos == 'PUNCT':
            result = self.__getPunctuationType(elem,last,next)
        # Subtitle element has word type.
        else:
            result = Constants.WORD
        return result

    # Method that checks if subtitle element has speaker type.
    # Three formats supported:
    # 1) dash at the beggining of line
    # 2) speaker name in uppercase with a proceding colon
    # 3) (1) followed by (2)
    def __isSpeaker(
            self,
            elem: TaggedToken, # Current element
            last: SubtitleElement | None, # Last added subtitle element
            next: TaggedToken | None, # Next comming subtitle element
            needSpeaker: bool # Checks if it is necessary to check if element is speaker identifier.
        ) -> bool:
        if needSpeaker:
            if re.match(r'(-+|–+)',elem.value): 
                if last == None: return True
                if last.subType == Constants.NEWLINE: return True
                return False
            if not(next == None):
                if elem.value.isupper() and next.value == ':': return True
            if not(last == None):
                if elem.value == ':' and last.value.isupper(): return True
        return False
    
    # Method that checks if subtitle element has symbol type.
    def __isSymbol(
            self,
            upos: str, # element POS tag
            value: str # element value
        ) -> bool:
        # 'SYM' tag is automatically a symbol
        if upos == 'SYM':
            return True
        # 'X' tag needs to be checked for alphanumerics
        if upos == 'X':
            for char in value:
                if str(char).isalnum() or char in dashes:
                    return False
            return True
        if re.match(r'(♪+)',value):
            return True
        return False

if __name__ == '__main__':
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', download_method=None)
    # texten = "- Valence's comms data?\n<i>- <u>XANDER<b>:</b></u> His # password #</i>"
    # textlv = "- Valences sakaru dati<b>?</b>\n<i>- <u>KSENDERS<b>:</b></u> Viņa # parole #2.</i>"
    # test = '[punch] [hit] [kick]'
    texten = "Mr. Blight , what are you-- I need an orphan! Now!"

    tokens = TaggedTextTokenizer(texten,nlp)
    result = []
    for word in tokens.tokens:
        result.append(word.value)
    print(result)
    subtitle = SubtitleElementTokenizer(tokens.tokens,1)
    for part in subtitle.parts:
        print(part.id,part.value,part.subType)
