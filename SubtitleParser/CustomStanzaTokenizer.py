import stanza
import re
from Configurations.Punctuations import brackets

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

    # Method for getting punctuation tokens.
    def __getPunctuationTokens(
            self,
            word # Current token.
        ):
        result = []
        text = word.text
        start = word.start_char
        regex = re.search(r'(\.\.+|…|‥)',text)
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
            regex = re.search(r'(\.\.+|…|‥)',text)
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
        doc = self.nlp(text)
        for sentence in doc.sentences:
            tempSentence = []
            for word in sentence.words:
                # Token starts with punctuations
                if re.search(r'(\.\.+|…)',word.text):
                    temp: list[CustomToken] = self.__getPunctuationTokens(word)
                    for t in temp:
                        tempSentence.append(t)
                else:
                    temp = CustomToken(word.text,word.start_char,word.end_char,word.upos)
                    tempSentence.append(temp)
                # Seperates bracket fragment at the end form sentence.
                if word.text in brackets.values() and word.id == len(sentence.words):
                    fragments = []
                    bracket = ''
                    for part in reversed(tempSentence):
                        if part.value in brackets.values():
                            fragments.append(part)
                            bracket = part.value
                        elif part.value in brackets.keys():
                            fragments.append(part)
                            if brackets[part.value] == bracket: break
                        else:
                            fragments.append(part)
                    fragments = list(reversed(fragments))
                    tempSentence = tempSentence[:-1*len(fragments)]
                    self.tokens.extend(tempSentence)
                    self.sentences.append(tempSentence)
                    tempSentence = []
                    self.tokens.extend(fragments)
                    self.sentences.append(fragments)
                # Seperates bracket fragment at the beggining form sentence.
                elif word.text in brackets.values() and word.id == len(tempSentence):
                    self.tokens.extend(tempSentence)
                    self.sentences.append(tempSentence)
                    tempSentence = []
            if len(tempSentence) > 0:
                self.tokens.extend(tempSentence)
                self.sentences.append(tempSentence)

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

if __name__ == "__main__":
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True,)
    # text = 'Uh, I mean, to be honest, Mrs. D, from the outside perspective, it kind of seems like something\'s going on.'
    # text = 'Šis teikums ir ļoti garš...?!'
    # text = 'Vai es...varu dejot...?'
    # text = "♪ Oh-oh-oh ♪♪ Who ♪"
    text = 'Did I hear that right? [stammers] What are we thinking?'
    test1 = CustomTokenizer(nlp)
    test1.Tokenize(text,True)
    
    # for token in test1.tokens:
    #     print(token.id,token.start,token.end,token.value,token.upos)

    for sentence in test1.sentences:
        print('-----------------------')
        for word in sentence:
            print(word.value,end=' ')
        print()
