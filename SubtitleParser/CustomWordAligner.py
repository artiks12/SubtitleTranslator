def CoverAlignmentHoles(alignments):
    result = alignments['mwmf'].copy()
    fwd = alignments['fwd'].copy()
    rev = alignments['rev'].copy()

    srcInInter:set = set({})
    trgInInter:set = set({})

    for i in result:
        srcInInter.add(i[0])
        trgInInter.add(i[1])

    fwd = [item for item in fwd if item[0] not in srcInInter]
    rev = [item for item in rev if item[1] not in trgInInter]

    result += fwd + rev
    
    result = sorted(result, key=lambda x: x)
    return result

def GetCustomAlignments(simAlign,sourceTokens,targetTokens):
    alignments = simAlign.get_word_aligns(sourceTokens , targetTokens)

    result = {
        'confidentWordAlignment':alignments['mwmf'],
        'wordAlignment':CoverAlignmentHoles(alignments)
    }

    return result