from Caption import Caption
from TranslationSentences import TranslationSentences
import Configurations.Constants as Constants

class CombiningState():
    def __init__(self):
        self.combined = []                 # List with combined captions
        self.combinedLast = -1             # Last sentence checked
        self.lastUnfinished = -1           # Last unfinished sentence (ends with 3 dots)
        self.count = 0                     # Amount of caption groups
        self.speakingAdded = False         # Check if speaking text (non-isolated) is added.

# Main combined function for combining captions.
def addToCombined(t: Caption,SourceNLP,TargetNLP,PretokenizeNLP,combinerInfo: CombiningState):
    # Aquire caption states

    CaptionIsIsolated = t.IsIsolated()

    if not(combinerInfo.speakingAdded):
        combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
        combinerInfo.count += 1
    else:
        if True in CaptionIsIsolated:
            if combinerInfo.combined[combinerInfo.combinedLast].IsLastUppercased() and CaptionIsIsolated[1]:
                if combinerInfo.combined[combinerInfo.combinedLast].TryAddCaption(t) == False:
                    combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                    combinerInfo.count += 1
                else:
                    combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                    combinerInfo.count += 1
            else:
                combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                combinerInfo.count += 1
        else:
            CaptionEndState = t.GetTextEndState()
            CaptionStartState = t.GetTextStartState()
            # Last caption continues in this caption.
            # If last caption ends with quote/bracket, then try to add current caption.
            if combinerInfo.combinedLast > -1:
                lastInWrapping = combinerInfo.combined[combinerInfo.combinedLast].IsLastInWrapping()
                if lastInWrapping:
                    if combinerInfo.combined[combinerInfo.combinedLast].TryAddCaption(t) == False:
                        combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                        combinerInfo.count += 1
                else:
                    combinerInfo.combined[combinerInfo.combinedLast].AddCaption(t)
            # Current caption starts without ellipses.
            elif CaptionStartState == Constants.TEXT:
                # Last caption has ellipses.
                if combinerInfo.lastUnfinished == combinerInfo.count-1:
                    if combinerInfo.combined[combinerInfo.lastUnfinished].TryAddCaption(t) == False:
                        combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                        combinerInfo.count += 1
                # Last caption ends a sentence.
                else:
                    combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                    combinerInfo.count += 1
            # Current caption starts with ellipses.
            else:
                if combinerInfo.lastUnfinished > -1:
                    combinerInfo.combined[combinerInfo.lastUnfinished].AddCaption(t)
                    if not(CaptionEndState == Constants.UNFINISHED):
                        combinerInfo.lastUnfinished = -1
                else:
                    combinerInfo.combined.append(TranslationSentences(t,SourceNLP,TargetNLP,PretokenizeNLP))
                    combinerInfo.count += 1
                    
    
    if not(True in CaptionIsIsolated):
        CaptionEndState = t.GetTextEndState()
        CaptionStartState = t.GetTextStartState()
        combinerInfo.speakingAdded = True
        if CaptionEndState == Constants.FINISHED:
            combinerInfo.combinedLast = -1
        elif CaptionEndState == Constants.CONTINUE or CaptionEndState == Constants.WRAPPING:
            combinerInfo.combinedLast = combinerInfo.count-1
        if CaptionEndState == Constants.UNFINISHED:
            combinerInfo.lastUnfinished = combinerInfo.count-1
            combinerInfo.combinedLast = -1

# Starts combining captions
def combiner(subtitles,SourceNLP,TargetNLP,PretokenizeNLP):
    combinerInfo = CombiningState()
    
    captions = []
    for s in subtitles:
        t = Caption().NewCaption(s.content,s.index,SourceNLP)
        captions.append(t)
        # Caption has wrappingSymbols or no speaking text.
        if True in t.IsIsolated():
            addToCombined(t,SourceNLP,TargetNLP,PretokenizeNLP,combinerInfo)
        # Caption has one speaker
        elif not(t.HasMultipleSpeakers()):
            addToCombined(t,SourceNLP,TargetNLP,PretokenizeNLP,combinerInfo)
        # Caption has multiple speakers
        else:
            for i in range(t.GetSpeakerCount()):
                newCaption = t.GetCopyWithOneSpeaker(i)
                addToCombined(newCaption,SourceNLP,TargetNLP,PretokenizeNLP,combinerInfo)
    
    return combinerInfo.combined