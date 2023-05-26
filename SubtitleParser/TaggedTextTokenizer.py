from html.parser import HTMLParser
import stanza
from srt import make_legal_content
import re

import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.CustomTokenizer import CustomTokenizer
from SubtitleParser.Configurations.Punctuations import wrappingSymbols, endings
from SubtitleParser.Configurations.Tags import *

class TaggedToken():
    """
        Tagged token class.
        It adds to existing nlp tokenizers by counting HTML tags
        as tokens and it saves information about line breaks
        and subtitle specific constructions.
        New part-of-speach tags include:
            1) OTAG - opening HTML tag;
            2) CTAG - closing HTML tag;
            3) ALIGN - subtitle file construction in curly brackets. 
                    Limited for SRT subtitles and common for SubstationAlpha subtitles.
            4) NLINE - newline symbol.
    """
    def __init__(
            self, value: str,
            start: int, end: int,
            upos: str,
            start_char: int = -1, end_char: int = -1,
            tag: str | None = None, dep: int = -2
        ) -> None:
        """
        param value: Token text value.
        param start: Token starting index in tagged text (inclusive).
        param end: Token ending index in tagged text (exclusive).
        param upos: Token universal part-of-speach tag.
        param start_char: Token starting index in non tagged text (inclusive).
        param end_char: Token ending index in non tagged text (exclusive).
        param tag: HTML tag name. None if not an HTML tag.
        param dep: Token, to which it depends on, id.
        """
        self.value: str = value
        self.start: int = start
        self.end: int = end
        self.start_char: int = start_char
        self.end_char: int = end_char
        self.upos: str = upos
        self.tag: str | None = tag
        self.dep: int = dep

    def InsertIndex(self, id: int) -> None:
        """
        Method for inserting token id.
        
        param id: Token id.
        """
        self.id: int = id

    def InsertDep(self, ids: list[int]) -> None:
        """
        Method for inserting dependency token id.
        
        param ids: List with token ids for tokens that are not tags and curly bracket elements. 
        """
        id = self.dep-1
        if id == -1: self.dep = id
        else: self.dep = ids[id]

class TaggedTextTokenizer():
    """
        Tagged text tokenizer class.
        Uses nlp tokenizers (in this case, stanza) and an HTML parser
        to tokenize text. All tokens are stored as TaggedToken class
        instances. It also removes unnecessary whitespaces that are
        surrounding non tagged text.
    """
    class Parser(HTMLParser):
        """
            Parser class that implements HTMLParser class. Is used
            to seperate HTML tags, curly bracket constructions
            and newline symbols from other text.
        """
        def __init__(self, *, convert_charrefs: bool = True ) -> None:
            super().__init__(convert_charrefs=convert_charrefs)
            self.extra: list[TaggedToken] = [] # Stores HTML tags and newline symbols
            self.text: list[str] = [] # Stores text data
            self.position: int = 0 # Current text character position

        def handle_starttag(self, tag: str, attrs: list[tuple[str,str]]) -> None:
            """
            Method to handle HTML opening tags.

            param tag: Tag name
            param attrs: Tag attribute pairs (name,value).
            """
            text: str = '<'+tag
            if len(attrs)>0:
                for attr in attrs:
                    text += ' ' + attr[0] + '="' + attr[1] + '"'
            text += '>'
            
            self.extra.append(TaggedToken(text,self.position,self.position+len(text),'OTAG',tag=tag))
            self.position += len(text)
            
        def handle_endtag(self, tag: str) -> None:
            """
            Method to handle HTML closing tags.

            param tag: Tag name
            """
            text: str = '</'+tag+'>'

            self.extra.append(TaggedToken(text,self.position,self.position+len(text),'CTAG',tag=tag))
            self.position += len(text)

        def handle_data(self, text: str) -> None:
            """
            Method to handle text data. Seperates curly bracket constructions from text.

            param text: Text data
            """
            elem = re.search(r'\{.*?\}',text)
            while elem:
                if not(elem.start() == 0):
                    self.__insertText(text[0:elem.start()])
                value = text[elem.start():elem.end()]
                self.extra.append(TaggedToken(value,self.position,self.position+len(value),'ALIGN'))
                self.position += len(value)
                text = text[elem.end():]
                elem = re.search(r'\{.*?\}',text)
            if len(text) > 0:
                self.__insertText(text)

        def __insertText(self, text: str) -> None:
            """
            Method to insert text elements.

            param text: Text data
            """
            textParts: list[str] = text.split('\n') # Split text seperated by newline sybols
            count: int = 0 # Amount of text parts added to list of text data
            for t in textParts:
                self.text.append(t)
                self.position += len(t)
                count += 1
                
                # Add newline symbol to extra symbol list if necessary.
                if count < len(textParts):
                    self.extra.append(TaggedToken('\n',self.position,self.position+len('\n'),'NLINE'))
                    self.position += len('\n')
                    self.text[-1] += ' '

    # Initializes the tokenizer and aquires tagged tokens.
    def __init__(
            self,
            text: str, # text that needs to be tokenized
            nlp, # tokenizer function that also aquires part-of-speach tags
            getDependencies: bool = False # Checks if dependency parsing is needed
        ) -> None:
        # text: str = self.__prepareText(text)

        # Creates HTML parser instance and parses the text.
        parser = self.Parser()
        parser.feed(text)
        
        if getDependencies: self.__tokenizeWithDependencies(parser.extra,parser.text,nlp)
        else: self.__tokenizeWithoutDependencies(parser.extra,parser.text,nlp)

        del parser

    # Method that prepares the text for tokenization.
    # TODO make the code faster and readable.
    def __prepareText(
            self,
            text: str # Text data.
        ) -> str:
        result = []
        legal = make_legal_content(text) # Removes lines with no text.
        
        # Removes unnecessary whitespaces that are surrounding non tagged text.
        regex = re.findall(r'(<.*?>|\{.*?\}|\S(.|\n)*[^\s])',legal)
        result.extend([item[0] for item in regex[:-1]])
        reverse = re.findall(r'(>.*?<|\}.*?\{|\S(.|\n)*[^\s])',regex[-1][0][::-1])
        result.extend([item[0][::-1] for item in reversed(reverse)])

        return ''.join(result)

    # Method that creates a list of tagged tokens without dependencies.
    def __tokenizeWithoutDependencies(
            self,
            tags: list[TaggedToken], # List of HTML tags and newline sybols.
            parts: list[str], # List of non HTML tag text parts that need to be tokenized.
            nlp
        ) -> list[TaggedToken]:
        text: str = ''.join(parts) # Non HTML text in string format. Needs to be tokenized.
        tokenizer = CustomTokenizer(nlp)
        tokenizer.Tokenize(text)
        self.tokens: list[TaggedToken] = [] # List of tokens.
        index: int = 0 # Current HTML tag list element index.
        offset: int = 0 # Text position offset. Shows how many symbols in text are taken by tags.

        # Go through every token in text and add it to result list.
        for sentence in tokenizer.sentences:
            for token in sentence:
                # If there are any HTML tags to be added before text token, add them to result list.
                while index < len(tags) and tags[index].start <= token.start+offset:
                    tags[index].InsertIndex(len(self.tokens))
                    self.tokens.append(tags[index])
                    # Update text offset if an HTML tag was added to result list.
                    if not(tags[index].upos == 'NLINE'):
                        offset += len(tags[index].value)
                    index += 1
                temp = TaggedToken(
                    token.value,token.start+offset,token.end+offset,
                    token.upos,token.start,token.end)
                temp.InsertIndex(len(self.tokens))
                self.tokens.append(temp)

        # If there are any HTML tags to be added, add them to result list.
        while index < len(tags):
            tags[index].InsertIndex(len(self.tokens))
            self.tokens.append(tags[index])
            index += 1

    # Method that creates a list of tagged tokens without dependencies.
    def __tokenizeWithDependencies(
            self,
            tags: list[TaggedToken], # List of HTML tags and newline sybols.
            parts: list[str], # List of non HTML tag text parts that need to be tokenized.
            nlp
        ) -> list[TaggedToken]:
        text: str = ''.join(parts) # Non HTML text in string format. Needs to be tokenized.
        tokenizer = nlp(text)
        self.tokens: list[TaggedToken] = [] # List of tokens.
        index: int = 0 # Current HTML tag list element index.
        offset: int = 0 # Text position offset. Shows how many symbols in text are taken by tags.  

        # Go through every token in text and add it to result list.
        for sentence in tokenizer.sentences:
            nonTagIds = []
            for token in sentence.words:
                # If there are any HTML tags to be added before text token, add them to result list.
                while index < len(tags) and tags[index].start <= token.start_char+offset:
                    tags[index].InsertIndex(len(self.tokens))
                    self.tokens.append(tags[index])
                    # Update text offset if an HTML tag was added to result list.
                    if not(tags[index].upos == 'NLINE'):
                        offset += len(tags[index].value)
                    index += 1
                temp = TaggedToken(
                    token.text,token.start_char+offset,token.end_char+offset,
                    token.upos,token.start_char,token.end_char,dep=token.head)
                temp.InsertIndex(len(self.tokens))
                nonTagIds.append(len(self.tokens))
                self.tokens.append(temp)
            for elem in nonTagIds:
                self.tokens[elem].InsertDep(nonTagIds)

        # If there are any HTML tags to be added, add them to result list.
        while index < len(tags):
            tags[index].InsertIndex(len(self.tokens))
            self.tokens.append(tags[index])
            index += 1

def GoThroughTree(tree,id,tokenIds):
    result = []
    temp = []
    if len(tree.children) == 0:
        result = tokenIds[id]
        id += 1
        return (result,id)
    else:
        for node in tree.children:
            (value,id) = GoThroughTree(node,id,tokenIds)
            temp.append(value)
        result.extend(temp)
    if len(result) == 1: return (result[0],id)
    return (result,id)


# Test Field
if __name__ == "__main__":
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', use_gpu=True)
    text = '- [Dusty] Oh.\n- [cries]'
    test1 = TaggedTextTokenizer(text,nlp,False)

    result = []
    for word in test1.tokens:
        result.append(word.value)
    print(result)
    

    # const = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse,mwt,constituency', use_gpu=True, tokenize_pretokenized=True)
    
    # texts = [text1,text2,text3,text4,text5]
    # texts = [text1]
    # docs = [const(item) for item in texts]
    # for doc in docs:
    #     id = 0
    #     for sentence in doc.sentences:
    #         tree = sentence.constituency
    #         print(tree)
    #         (result,newId) = GoThroughTree(tree,0,list(range(id,len(sentence.words)+id)))
    #         id = newId
    #         print(result)

# config = {
#     'use_gpu': True,
#     'processors': 'tokenize,pos,lemma',
#     'tokenize_pretokenized': True,
#     'lang': 'lv',
#     'pos_batch_size': BATCH_SIZE,
#     'lemma_batch_size': BATCH_SIZE
# }

# [[[[1]], [[2], [[3], [4]]], [5]]]
#  [[[1]], [[2], [[3], [4]]], [5]]
#   [[1]], [[2], [[3], [4]]], [5]