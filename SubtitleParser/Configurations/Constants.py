### Subtitle Element types (SRT only)
# Content types
WORD = 'word'                               # Part of speaking text.
EFFECT = 'effect'                           # Part of effect text.
NEWLINE = 'newline'                         # Newline.

# Formatting types
SPEAKER = 'speaker'                         # Speaker identifier.
SYMBOL = 'symbol'                           # Symbol wrapped around text.
ALIGN = 'align'                             # Text alignment element.

# Wrapping types
TAG_OPEN = 'tag open'                       # Opening HTML tag.
TAG_CLOSE = 'tag close'                     # Closing HTML tag.
WORD_CLOSE = 'word_close'                   # Clsoing bracket/quote.
WORD_OPEN = 'word_open'                     # Opening bracket/quote.
EFFECT_CLOSE = 'effect_close'               # Clsoing square bracket.
EFFECT_OPEN = 'effect_open'                 # Opening square bracket.

# Punctuation types
PUNCT_LEFT = 'punct_left'                   # Punctuation attached to the left of a word.
PUNCT_RIGHT = 'punct_right'                 # Punctuation attached to the right end of a word.
PUNCT_IN = 'punct_in'                       # Punctuation attached between tokens.
PUNCT_OUT = 'punct_out'                     # Punctuation detached from tokens.
PUNCT = 'punct'                             # Punctuation.

# Sentence constants
FINISHED = 'finished'
UNFINISHED = 'unfinished'
CONTINUE = 'continue'
WRAPPING = 'wrapping'

RESTART = 'restart'
TEXT = 'text'

# Type groups
speakingText = [PUNCT_LEFT,PUNCT_RIGHT,PUNCT_IN,PUNCT_OUT,WORD,WORD_CLOSE,WORD_OPEN]
effectText = [EFFECT,EFFECT_CLOSE,EFFECT_OPEN]
styleFormatting = [TAG_CLOSE,TAG_OPEN,ALIGN]
contentFormatting = [SPEAKER,SYMBOL]
formatting = styleFormatting + contentFormatting + effectText
punctuations = [PUNCT_LEFT,PUNCT_RIGHT,PUNCT_IN,PUNCT_OUT]