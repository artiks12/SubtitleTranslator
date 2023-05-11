class SubtitleGuidelineMetrics():
    def __setParameters(
        self,
        rowCount,
        symbolCount,
        charactersPerSecond 
    ):
        self.rows = rowCount
        self.symbols = symbolCount
        self.speed = charactersPerSecond
        return self
    
    def GetCustom(
        self,
        rowCount,
        symbolCount,
        charactersPerSecond
    ):
        return self.__setParameters(rowCount,symbolCount,charactersPerSecond)

    def GetPredefined(self,value):
        result = None
        if value == 'BBC_EN': result = self.__setParameters(2,37,17)
        if value == 'BBC_LV': result = self.__setParameters(2,37,17)
        return result