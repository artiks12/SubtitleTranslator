from Caption import Caption
import Configurations.Constants as Constants

class Sentences():
    """
        Sentences class.
        Class for storing caption groups that, when combining their content,
        gets full sentences only.
    """
    def __init__(
            self, 
            subtitle: Caption, 
            SourceNLP, 
            TargetNLP,
            PretokenizeNLP, 
            multiple: bool = False
        ) -> None:
        self._captions: list[Caption] = [subtitle]
        self.multiple = multiple
        self.unfinished = False
        self.SourceNLP = SourceNLP
        self.TargetNLP = TargetNLP
        self.PretokenizeNLP = PretokenizeNLP
    
    # Method to get speaking text from all captions stored.
    def GetSpeakingTextFromCaptions(self) -> str:
        result = ''
        for c in self._captions:
            result += c.SpeakingTextAsStringOneline() + ' '
        return result
    
    # Method to check if last caption ended with quotation mark or apostrophe.
    def IsLastInWrapping(self):
        return self._captions[-1].GetTextEndState() == Constants.WRAPPING
    
    # Method to check if last caption has all text uppercased.
    def IsLastUppercased(self):
        return self._captions[-1].IsIsolated()[1]

    # Method that adds a caption to caption list.
    def AddCaption(self,newCaption: Caption) -> None:
        self._captions.append(newCaption)

    # Method that tries to add a caption to caption list.
    # Uses stanzas sentence divider to check if new caption text adds to existing text or is seperate.
    # If is seperate then caption is not added and method returns False, othervise returns True.
    def TryAddCaption(self,newCaption: Caption) -> bool:
        # Get existing text and potencial text
        oldText = self.GetSpeakingTextFromCaptions()
        newText = oldText + newCaption.SpeakingTextAsStringOneline()
        oldDoc = self.SourceNLP(oldText)
        newDoc = self.SourceNLP(newText)

        # Checks if new text adds to existing text.
        for x in range(len(oldDoc.sentences)):
            oldWordsCount = len(oldDoc.sentences[x].words)
            newWordsCount = len(newDoc.sentences[x].words)
            if not(oldWordsCount == newWordsCount):
                self._captions.append(newCaption)
                return True
        return False
    
    # Method to get caption indexes.
    def GetIndexes(self):
        result = []
        for c in self._captions:
            result.append(c.index)
        return result