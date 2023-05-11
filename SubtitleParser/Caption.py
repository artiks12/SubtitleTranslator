import stanza
import Configurations.Constants as Constants
from Configurations.Punctuations import *
from Configurations.Tags import *
from TaggedTextTokenizer import TaggedTextTokenizer, TaggedToken
from SubtitleElementTokenizer import SubtitleElementTokenizer, SubtitleElement
from typing import TypeVar
import re

CaptionType = TypeVar("CaptionType", bound="Caption")

class Caption():
    """
        Caption class.
        Stores information about a single subtitle. Subtitle text is first
        parsed and tokenized by HTMLParser and Stanza tokenizer respectively
        and then subtitle elements are aquired and stored here.
    """
    ##########                CONSTRUCTORS                ##########
    # Constructor method for creating a new Caption instance
    def NewCaption(
            self: CaptionType,
            text: str,  # Subtitle text content
            index: int, # Subtitle index in subtitle file
            nlp,    # nlp tool (Stanza)
        ) -> CaptionType:
        tokens: list[TaggedToken] = TaggedTextTokenizer(text,nlp).tokens
        SubtitleTokenizer: SubtitleElementTokenizer  = SubtitleElementTokenizer(tokens,index)
        self.parts: list[SubtitleElement] = SubtitleTokenizer.parts
        self.index: int = index
        self.IsSubCaption = False

        self.__getRangesForParts()
        
        del tokens
        del SubtitleTokenizer

        return self
    
    # Constructor method for creating a subcaption from existing Caption instance.
    def SubCaption(
            self: CaptionType,
            parts: list[SubtitleElement], # Subparts of the caption
            superCaption: CaptionType # Supercaption of the caption
        ) -> CaptionType:
        self.parts: list[SubtitleElement] = []
        for p in range(len(parts)):
            newId = str(parts[p].GetCaption())+'-'+str(p)
            self.parts.append(parts[p].copy(newId=newId))

        self.index: int = superCaption.index
        self.IsSubCaption = True

        self.__getRangesForParts()

        return self
    
    # Method for getting ranges for specific subtitle element groups.
    def __getRangesForParts(
            self,
        ):
        # Content that is either speaking text or sound effects.
        self.speakingStart: int = -1
        self.speakingEnd: int = -1
        for part in self.parts:
            if self.speakingStart == -1 and part.subType not in Constants.formatting + [Constants.NEWLINE]:
                self.speakingStart = part.GetIndex()
            if self.speakingStart > -1:
                break
        
        for part in reversed(self.parts):
            if self.speakingEnd == -1 and part.subType not in Constants.formatting + [Constants.NEWLINE]:
                self.speakingEnd = part.GetIndex()
            if self.speakingEnd > -1:
                break
    
    ##########                SUBTITLE CONTENT TO STRING                ##########
    # Main method for aquiring string from subtitle elements
    def __getString(
            self,
            elements: list[SubtitleElement], # list of subtitle elements
            newlines: bool # Should newlines be treated as new lines (True) or spaces (False).
        ) -> str:
        result = '' # Resulting string
        last = None # Last inserted element
        for elem in elements:
            if result == '': result += elem.value
            else:
                spaces = elem.start - last.end
                value = elem.value
                if not(newlines) and elem.subType == Constants.NEWLINE:
                    value = ' '
                result += (' '*spaces) + value
            last = elem
        return result
    
    # String representation of Caption class is caption content in subtitle file.
    def __str__(self) -> str:
        return self.__getString(self.parts,True)
    
    # Method for getting speaking text as string in one line.
    def SpeakingTextAsStringOneline(self) -> str:
        return self.__getString(self.GetSpeakingText(),False)
    
    ##########                SUBTITLE ELEMENT FILTERRING BASE                ##########
    # Main method for aquirring subtitle elements filterred by specified filters and function.
    def __filter(
            self,
            filters: list, # Filterring parameters
            filterFunction # Filterring function
        ) -> list[SubtitleElement]:
        result: list[SubtitleElement] = [] # Resulting list.
        last: SubtitleElement | None = None # Last checked element. Value is None if no elements in resulting list.
        spaces: int = 0 # Amount of spaces required between elements.
        position: int = 0 # Current position for next resulting element to start.
        for elem in self.parts:
            if filterFunction(elem,filters):
                if len(result) > 0: spaces += elem.start - last
                result.append(elem.copy(newStart = position+spaces))
                position = result[-1].end
                spaces = 0
            else:
                if not(last == None): spaces += elem.start - last
            if len(result) > 0: last = elem.end
        return result
    
    # Filter method for checking if element type is in filters list.
    def __elemInSubTypes(
            self: CaptionType,
            elem: SubtitleElement, # Subtitle element that is checked
            filters: list[str] # List of subtitle types
        ) -> bool:
        return elem.subType in filters
    
    # Filter method for checking if element type is in filters list.
    def __elemNotInSubTypes(
            self: CaptionType,
            elem: SubtitleElement, # Subtitle element that is checked
            filters: list[str] # List of subtitle types
        ) -> bool:
        return not(elem.subType in filters)
    
    # Filter method for checking if element index is not in filter list.
    def __elemNotInIndexes(
            self: CaptionType,
            elem: SubtitleElement, # Subtitle element that is checked
            filters: list[int]  # List of subtitle indexes
        ) -> bool:
        return not(elem.GetIndex() in filters)
    
    # Filter method for checking if element index is not in filter list.
    def __elemInIndexes(
            self: CaptionType,
            elem: SubtitleElement, # Subtitle element that is checked
            filters: list[int]  # List of subtitle indexes
        ) -> bool:
        return elem.GetIndex() in filters
    
    ##########                SUBTITLE ELEMENT FILTERRING BY ELEMENT TYPE                ##########
    # Method that gets speaking text parts.
    def GetSpeakingText(self: CaptionType) -> list[SubtitleElement]:
        filters: list[str] = Constants.speakingText
        return self.__filter(filters,self.__elemInSubTypes)
    
    def GetTextWithoutStyleFormating(self: CaptionType) -> list[SubtitleElement]:
        filters: list[str] = Constants.styleFormatting + Constants.effectText
        return self.__filter(filters,self.__elemNotInSubTypes)
    
    def GetWrappingSymbols(self: CaptionType) -> list[SubtitleElement]:
        filters: list[str] = [Constants.SYMBOL]
        return self.__filter(filters,self.__elemInSubTypes)

    ##########                SUBTITLE ELEMENT FILTERRING BY ELEMENT ID                ##########
    def GetTextWithoutEllipses(self: CaptionType, needStart = True, needEnd = True):
        ids = self.GetSpeakerWrappingSymbolIndexesWithEllipses(needStart,needEnd)
        return self.__filter(ids,self.__elemInIndexes)
    
    def GetSpeakerTextStartAndEnd(self: CaptionType, needStart = True, needEnd = True):
        ids = self.GetSpeakerWrappingSymbolIndexesWithEllipses(needStart,needEnd)
        parts = self.__filter(ids,self.__elemNotInIndexes)
        start = []
        end = []
        for part in parts:
            if len(start) == 0:
                if part.GetIndex() == 0: start.append(part)
                else: end.append(part)
            else:
                if start[-1].GetIndex() + 1 == part.GetIndex(): start.append(part)
                else: end.append(part)
        return (start,end)
    
    ##########                SUBTITLE LINE FUNCTIONS                ##########
    # Method to get subtitle elements as list of lists where every sublist is a text line.
    def _getLines(
            self: CaptionType,
            elements: list[SubtitleElement]
        ) -> list[list[SubtitleElement]]:
        rows: list[list[SubtitleElement]] = []
        row: list[SubtitleElement] = []
        for elem in elements:
            row.append(elem)
            if elem.subType == Constants.NEWLINE:
                rows.append(row)
                row = []
        if len(row) > 0:
            rows.append(row)
        return rows
    
    def GetLinesForAllText(self: CaptionType) -> list[list[SubtitleElement]]:
        return self._getLines(self.parts)
    
    ##########                SPEAKER FUNCTIONS                ##########
    # Method to check if caption has multiple speakers.
    def HasMultipleSpeakers(self) -> bool:
        return self.GetSpeakerCount() > 1
    
    # Method to check how many rows have speaker identifiers.
    def GetSpeakerCount(self) -> int:
        return len(self.GetSpeakerRowIndexes())
    
    # Method to get rows with speaker elements.
    def GetSpeakerRowIndexes(self) -> list[int]:
        rowId: int = 0
        speakers: list[int] = []
        rows: list[list[SubtitleElement]] = self.GetLinesForAllText()
        for row in rows:
            for elem in row:
                if elem.subType == Constants.SPEAKER: 
                    speakers.append(rowId)
                    break
            rowId += 1
        if len(speakers) > 0:
            if 0 not in speakers: speakers = [0] + speakers
        return speakers
    
    # Method to get text lines coresponding to single speaker.
    def GetSpeakerRows(self,start):
        speakers = self.GetSpeakerRowIndexes()
        rows = self.GetLinesForAllText()
        # Get all rows
        if len(speakers) == start + 1:
            rows = rows[speakers[start]:]
        else:
            rows = rows[speakers[start]:speakers[start+1]]
        # Put all elements in one list
        result = []
        for row in rows:
            result.extend(row)
        return result
    
    # Method to get subcaption with one speaker.
    def GetCopyWithOneSpeaker(self,speaker):
        parts = self.GetSpeakerRows(speaker)
        return Caption().SubCaption(parts,self)
    
    ##########                SUBTITLE STATE FUNCTIONS                ##########    
    # Method to check what is the last element in caption. 
    def GetTextEndState(self):
        parts = self.GetSpeakingText()
        lastElement: SubtitleElement = parts[-1] 

        if lastElement.subType.startswith(Constants.PUNCT):
            if re.match(r'(\.\.+|…)',lastElement.value): return Constants.UNFINISHED
            elif lastElement.value in endings: return Constants.FINISHED
        elif lastElement.subType == Constants.WORD_CLOSE:
            return Constants.WRAPPING
        return Constants.CONTINUE

    # Method to check what is the first element in caption.        
    def GetTextStartState(self):
        parts = self.GetSpeakingText()
        firstElement: SubtitleElement = parts[0] 

        if re.match(r'(\.\.+|…)',firstElement.value):
            return Constants.RESTART
        return Constants.TEXT
            
    # Method to check if speaking text is uppercased without punctuations.
    def IsIsolated(self):
        result = []
        result.append(self.HasWrappingSymbols())
        text = self.GetTextWithoutStyleFormating()
        for elem in text:
            if elem.subType == Constants.WORD and not(elem.value.isupper()):
                result.append(False)
                break
        if len(result)==2: return result
        result.append(True)
        return result

    ##########                SPEAKING TEXT ACQUISITION FUNCTIONS               ##########
    # Method to get inclusive interval for speaker content.
    def __getSpeakersStartAndEndIndexes(self,needBegining=True,needEnd=True) -> tuple[int,int]:
        start = self.speakingStart
        end = self.speakingEnd
        
        if not(needBegining):
            for i in range(start,end+1):
                if not(re.match(r'(…|\.\.+)',self.parts[i].value)):
                    start = self.parts[i].GetIndex()
                    break
        if not(needEnd):
            for i in reversed(range(start,end+1)):
                if not(re.match(r'(…|\.\.+)',self.parts[i].value)):
                    end = self.parts[i].GetIndex()
                    break
        
        return (start,end)

    def GetSpeakerWrappingSymbolIndexesWithEllipses(self,needStart,needEnd):
        (start,end) = self.__getSpeakersStartAndEndIndexes(needStart,needEnd)
        return list(range(start,end+1))
    
    ##########                WRAPPING SYMBOL FUNCTIONS                ##########
    # Methot to check if caption has multiple wrapping symbol content groups.
    def HasWrappingSymbols(self):
        return len(self.GetWrappingSymbols()) > 0

if __name__ == "__main__":
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')
    text = '<font color="#FFFFFF"># ARTIS: <i> Viņš iet uz "2. posmu"...\n<b>..nevēlējās</b> <u>izgāzties</u>. </i>#</font>'
    text = 'ROB: ♪ Oh-oh-oh ♪♪ Who... ♪'
    # text = '{\\an5\\t(0,5000,\\frz3600)}Sentence is aligned.'
    # text = '………sentence is aligned………………'
    test1 = Caption().NewCaption(text,0,nlp)
    # for p in test1.parts:
    #     print(p.id,p.value,p.subType)

