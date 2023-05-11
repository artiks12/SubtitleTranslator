brackets={
    '(':')',
    '[':']',
}
quotes = {
    '“':'”'
}
citationOneWay = ['"',"'"]

endings = ['.','!','?']
beginnings = ['¿','¡']
ellipses = ['…','..','...']
inSentence = [':',';',',']
'‥' 
wrappingSymbols = ['♪']
dashes = ['–','-']

punctuations = endings + beginnings + ellipses + inSentence + dashes
closings = brackets | quotes
wrapping = list(brackets.keys()) + list(brackets.values()) + list(quotes.keys()) + list(quotes.values()) + citationOneWay