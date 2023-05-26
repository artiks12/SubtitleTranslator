import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))
from SubtitleParser.Configurations.Punctuations import allPuncts

# Function that Gets Alignment groups in order.
def GetAlignmentOrders(
        sourceToTarget:list[list[list[int]]],
        targetToOriginal:list[list[list[int]]],
        targetRanges:list[list[int]],
        targetTokens
    ):
    order: list[list[list[int]]] = []
    for x in range(len(sourceToTarget)):
        if len(order) == 0:
            order.append([sourceToTarget[x][0].copy(),targetToOriginal[x][0].copy()])
        else:
            order.append([sourceToTarget[x][0].copy(),targetToOriginal[x][0].copy()])
    result = []
    offset = list(targetTokens.keys())[0]
    for group in order:
        if len(result) == 0:
            result.append(group.copy())
        else:
            token = group[1][0]
            first = token - offset
            last = result[-1][1][-1] - offset
            if targetRanges[last][1] == targetRanges[first][0] and targetTokens[token] in allPuncts:
                result[-1][0].extend(group[0].copy())
                result[-1][1].extend(group[1].copy())
            else:
                result.append(group.copy())
    return result

def GetCopyOfDictionary(dictionary:dict):
    newDict = {}
    for k in dictionary:
        newDict[k] = dictionary[k].copy()
    return newDict

# Function that gets potencial group members for every token.
def GetGroups(
        alignmentsFromSource:dict[int,list[int]],
        alignmentsFromTarget:dict[int,list[int]]
    ):
    source = GetCopyOfDictionary(alignmentsFromSource)
    target = GetCopyOfDictionary(alignmentsFromTarget)
    finish = False
    while not(finish):
        finish = True
        for s in source:
            first = source[s][0]
            last = source[s][-1]
            if source[s] == list(range(first,last+1)):
                continue
            finish = False
            missing = []
            for r in range(first,last+1):
                if r not in source[s]:
                    missing.append(r)
                    target[r].append(s)
                    target[r] = list(set(target[r]))
                    target[r] = list(sorted(target[r]))
            source[s].extend(missing)
            source[s] = list(set(source[s]))
            source[s] = list(sorted(source[s]))

        for s in target:
            first = target[s][0]
            last = target[s][-1]
            if target[s] == list(range(first,last+1)):
                continue
            finish = False
            missing = []
            for r in range(first,last+1):
                if r not in target[s]:
                    missing.append(r)
                    source[r].append(s)
                    source[r] = list(set(source[r]))
                    source[r] = list(sorted(source[r]))
            target[s].extend(missing)
            target[s] = list(set(target[s]))
            target[s] = list(sorted(target[s]))

    return (source,target)

# Function that gets alignment groups.
def GetAlignmentGroups(
        alignmentsFromSource:dict[int,list[int]],
        alignmentsFromTarget:dict[int,list[int]],
        first: int
    ):
    (source,target) = GetGroups(alignmentsFromSource,alignmentsFromTarget)
    result = []
    index = first
    lastTarget = source[index].copy()
    lastSource = [index]
    while index != len(source)+first:
        if not(lastTarget == list(range(lastTarget[0],lastTarget[-1]+1))):
            for x in range(lastTarget[0],lastTarget[-1]+1):
                if not(x in lastTarget):
                    missing = target[x].copy()
                    lastTarget.append(x)
                    lastSource.extend(missing)
            lastSource = list(set(lastSource))
            lastTarget = list(set(lastTarget))
            lastSource.sort()
            lastTarget.sort()

        elif not(lastSource == list(range(lastSource[0],lastSource[-1]+1))):
            for x in range(lastSource[0],lastSource[-1]+1):
                if not(x in lastSource):
                    missing = source[x].copy()
                    lastSource.append(x)
                    lastTarget.extend(missing)
            lastSource = list(set(lastSource))
            lastTarget = list(set(lastTarget))
            lastSource.sort()
            lastTarget.sort()
        
        else:
            tempSource = []
            for x in lastTarget:
                tempSource.extend(target[x].copy())

            tempTarget = []
            for x in tempSource:
                tempTarget.extend(source[x].copy())

            tempSource = list(set(tempSource))
            tempTarget = list(set(tempTarget))
            tempSource.sort()
            tempTarget.sort()

            
            if tempSource == lastSource and tempTarget == lastTarget:
                result.append([tempSource,tempTarget])
                index = tempSource[-1] + 1
                if index < len(source)+first:
                    lastTarget = source[index].copy()
                    lastSource = [index]
            else:
                lastTarget = tempTarget
                lastSource = tempSource

    return result   

# Function that gets alignments for all tokens.
def GetAlignmentsForTokens(alignments,isSource):
    result = {}
    source = 0 if isSource else 1
    target = 1 if isSource else 0
    for align in alignments:
        if not(align[source] in result.keys()):
            result[align[source]] = []
        result[align[source]].append(align[target])
    
    result = dict(sorted(result.items()))
    
    return result

# Function that gets alignment data.
def GetAlignment(MT,offsetSource=0,offsetTarget=0,startSource=0,startTarget=0):
    sourceWordRanges = []
    for r in MT['sourceWordRanges']:
        sourceWordRanges.append([r[0]+startSource,r[1]+startSource])

    targetWordRanges = []
    for r in MT['targetWordRanges']:
        targetWordRanges.append([r[0]+startTarget,r[1]+startTarget])

    wordAlignment = []
    for pair in MT['wordAlignment']:
        wordAlignment.append([pair[0]+offsetSource,pair[1]+offsetTarget])

    sourceAlignments = GetAlignmentsForTokens(wordAlignment,True)
    targetAlignments = GetAlignmentsForTokens(wordAlignment,False)

    sourceAlignmentGroups = GetAlignmentGroups(sourceAlignments,targetAlignments,offsetSource)
    targetAlignmentGroups = GetAlignmentGroups(targetAlignments,sourceAlignments,offsetTarget)

    groupAlignmentOrder = GetAlignmentOrders(sourceAlignmentGroups,targetAlignmentGroups,targetWordRanges,MT['targetTokens'])
    
    result = {
        'sourceAlignments':sourceAlignments,
        'targetAlignments':targetAlignments,
        'sourceAlignmentGroups':sourceAlignmentGroups,
        'targetAlignmentgroups':targetAlignmentGroups,
        'groupAlignmentOrder':groupAlignmentOrder,
        'targetWordRanges':targetWordRanges,
    }

    return result
