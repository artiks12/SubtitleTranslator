import re

class CustomToken():
    def __init__(
            self,
            value: str, # Token text value.
            start: int, # Token starting index in tagged text (inclusive).
            end: int, # Token ending index in tagged text (exclusive).
            upos: str, # Token universal part-of-speach tag.
        ) -> None:
        self.value: str = value
        self.start: int = start
        self.end: int = end
        self.upos: str = upos
        self.id: int = -1

    # Method for inserting token id.
    def InsertIndex(
            self,
            id: int # Token id.
        ) -> None:
        self.id: int = id

    # Method for adding a string to token value.
    def AddToken(
            self,
            value: int # String value to add
        ):
        self.value += value
        self.end += len(value)

class CustomTokenizer():
    """
        Custom tokenizer class.

        Reworked the stanza tokenizer so that ellipses are tokenized seperately and bracket constructoins
        are divided from full sentences.
    """
    def __init__(
            self,
            nlp
        ):
        self.nlp = nlp

    def __seperateBracketText(self,text):
        result = []
        regex = re.search(r'(\[.*?\]|\(.*?\))',text)
        while regex:
            if not(regex.start() == 0):
                value = text[0:regex.start()]
                result.append(value)
            value = text[regex.start():regex.end()]
            result.append(value)
            text = text[regex.end():]
            regex = re.search(r'(\[.*?\]|\(.*?\))',text)
        if len(text) > 0:
            result.append(text)
        return result
    
    # Method for getting punctuation tokens.
    def __getPunctuationTokens(
            self,
            word, # Current token.
            offset
        ):
        result = []
        text = word.text
        start = word.start_char+offset
        regex = re.search(r'(\.\.+|…|‥|-|–)',text)
        while regex:
            # The start of the string is not a punctuation but a word.
            if not(regex.start() == 0):
                value = text[0:regex.start()]
                result.append(CustomToken(value,start,start+len(value),word.upos))
                start = result[-1].end
            value = text[regex.start():regex.end()]
            result.append(CustomToken(value,start,start+len(value),'PUNCT'))
            text = text[regex.end():]
            start = result[-1].end
            regex = re.search(r'(\.\.+|…|‥|-|–)',text)
        # The word string is still in text variable.
        if len(text) > 0:
            result.append(CustomToken(text,start,start+len(text),word.upos))
        return result 

    # Method that tokenizes text.
    def Tokenize(
            self,
            text: str, # Texts that needs to be tokenized
            insertTokenIds: bool = False # Boolean that tells if token ids need to be added or not.
        ):
        self.tokens: list[CustomToken] = []
        self.sentences: list[list[CustomToken]] = []
        fragments = self.__seperateBracketText(text)
        offset = 0
        for fragment in fragments:
            doc = self.nlp(fragment)
            for sentence in doc.sentences:
                tempSentence = []
                for word in sentence.words:
                    # Token starts with punctuations
                    if re.search(r'(\.\.+|…|-|–)',word.text):
                        temp: list[CustomToken] = self.__getPunctuationTokens(word,offset)
                        for t in temp:
                            if len(tempSentence) > 0:
                                if tempSentence[-1].end == t.start:
                                    if re.fullmatch(r'[-|–]',tempSentence[-1].value) and re.fullmatch(r'[-|–]',t.value):
                                        tempSentence[-1].end = t.end
                                        tempSentence[-1].value += t.value
                                    else:
                                        tempSentence.append(t)
                                else:
                                    tempSentence.append(t)
                            else:           
                                tempSentence.append(t)
                    else:
                        temp = CustomToken(word.text,word.start_char+offset,word.end_char+offset,word.upos)
                        tempSentence.append(temp)
                if len(tempSentence) > 0:
                    self.tokens.extend(tempSentence)
                    self.sentences.append(tempSentence)
            offset += len(fragment)

        if insertTokenIds: self.GiveNewIds(list(range(len(self.tokens))))

    # Method to insert token ids. Lenght for list of ids needs to match token count.
    def GiveNewIds(
            self,
            ids: list[int]
        ):
        if len(ids) == len(self.tokens):
            for x in range(len(ids)):
                self.tokens[x].InsertIndex(ids[x])

    def GetTokenValues(
            self,
            tokens: list[CustomToken]
        ):
        return [t.value for t in tokens]