import srt
import sys, os
from sacrebleu.metrics import BLEU, CHRF, TER
from math import exp, log
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),''))

referenceFiles = [
    'City.on.Fire.S01E03.WEB.x264-TORRENTGALAXY.Latvian.LAV.srt',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.Latvian.LAV.srt',
    'silo.s01e03.720p.web.h264-ggez.Latvian.LAV.srt',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA.LAV.srt',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.Latvian.LAV.srt',
]

hypothesesFiles = [
    'City.on.Fire.S01E03.1080p.WEB.H264-GGWP.',
    'Schmigadoon.S02E06.720p.WEBRip.2CH.x265.HEVC-PSA.English [SDH].ENG.',
    'silo.s01e03.720p.web.h264-ggez.English [SDH].ENG.',
    'Ted.Lasso.S03E08.720p.10bit.WEBRip.2CH.x265.HEVC-PSA_ENG.',
    'The.Big.Door.Prize.S01E09.WEB.x264-TORRENTGALAXY.English [SDH].ENG.',
]

variant = {
    'tilde.SimAlign.srt':'TildeSimAlign\\',
    'tilde.tilde.srt':'TildeTilde\\',
    'srt':'TildeDocument\\',
    'tilde.Sentences.srt':'TildeSentences\\',
}

import re

"""
    All code is taken from EvalSubtitle.
    Available here: 
"""
def hms_to_hmsf(hms):
    """
    Converts a timecode from hms to hmsf format.

    :param hms: timecode at format hh:mm:ss,sss
    :return: timecode at format hh:mm:ss:ff
    """
    h, m, s = hms.split(':')
    s, ms = s.split(',')
    
    f = int(ms)/40  # frame (from 0 to 24)
    
    return '%s:%s:%s:%02d' % (h, m, s, f)

class SrtCaption:
    def __init__(self, file_lines):
        self.index = int(file_lines[0])
        begin, end = file_lines[1].split(' --> ')
        self.begin = hms_to_hmsf(begin)
        self.end = hms_to_hmsf(end)
        self.lines = file_lines[2:]

class SrtReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'r', encoding='utf-8-sig')
        self.caption = None
    
    def reinit(self):
        self.file.close()
        self.file = open(self.file_path, 'r', encoding='utf-8-sig')
        self.caption = None
    
    def close(self):
        self.file.close()
    
    def read_caption(self):
        file_lines = list()
        file_line = self.file.readline().rstrip()
        
        while file_line:
            if file_line[0] != '#':
                file_lines.append(file_line)
            
            file_line = self.file.readline().rstrip()
        
        if len(file_lines) < 3:
            return False
        else:
            self.caption = SrtCaption(file_lines)
            return True

    def read_all(self):
        captions = list()
        while self.read_caption():
            caption = self.current_lines()
            captions.append(caption)

        return captions
    
    def current_index(self):
        return self.caption.index
    
    def current_time_span(self):
        return self.caption.begin, self.caption.end
    
    def current_lines(self):
        return  self.caption.lines

def find_eos(tagged_str):
    return [m.end() for m in re.finditer(r'((?<![(\[ -])\.|[!?]|--|…)( )?(["”\])])?( )?(%s)' % ('<eob>'), tagged_str)]

def srt_to_tagged_str(srt_file_path, line_tag='<eol>', caption_tag='<eob>'):
    srt_reader = SrtReader(srt_file_path)

    captions = list()
    time_spans = list()
    while srt_reader.read_caption():
        caption = srt_reader.current_lines()
        captions.append(caption)
        time_span = '%s %s' % srt_reader.current_time_span()
        time_spans.append(time_span)

    tagged_str = caption_tag.join([line_tag.join(caption) for caption in captions]) + caption_tag
    tagged_str = re.sub(r"(%s|%s)" % (line_tag, caption_tag), r" \1 ", tagged_str).strip()

    srt_reader.close()

    return tagged_str, time_spans

def srt_to_tagged_sents(srt_file_path, line_tag='<eol>', caption_tag='<eob>'):
    tagged_str, time_spans = srt_to_tagged_str(srt_file_path, line_tag=line_tag, caption_tag=caption_tag)
    eos_positions = find_eos(tagged_str)

    tagged_sents = list()
    start_pos = 0
    for end_pos in eos_positions:
        tagged_sent = tagged_str[start_pos:end_pos]
        tagged_sent = tagged_sent.strip()
        tagged_sents.append(tagged_sent)
        start_pos = end_pos

    return tagged_sents, time_spans

def preprocess(input_file_path, line_tag='<eol>', caption_tag='<eob>', line_holder='µ', caption_holder='§', srt=True):
    r"""
    Preprocess the text from a tagged txt or srt file.

    Removing potential multiple spaces.
    Removing potential spaces in the beginning of file lines.
    Removing spaces around boundaries.
    Replacing boundaries with 1-char placeholders.

    Exple:

    INPUT - "The cat <eol> is black. <eob>\\nHe's sleeping. <eob>\\n"
    OUTPUT - "The catµis black.§\\nHe's sleeping.§\\n"

    :param input_file_path: input file
    :param line_tag: end-of-line tag
    :param caption_tag: end-of-bloc/caption tag
    :param line_holder: placeholder for end-of-line tag
    :param caption_holder: placeholder for end-of-bloc/caption tag
    :param srt: wether the input file is in srt format
    :return: Preprocessed string
    """
    if srt:
        tagged_sents, _ = srt_to_tagged_sents(input_file_path, line_tag=line_tag, caption_tag=caption_tag)
        tagged_str = '\n'.join(tagged_sents)
    else:
        tagged_str = open(input_file_path).read()

    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)
    # Removing potential spaces in the beginning of file lines
    tagged_str = re.sub(r"\n ", r"\n", tagged_str)
    # Removing spaces around boundaries
    tagged_str = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", tagged_str)
    # Replacing boundaries with 1-char placeholders
    tagged_str = re.sub(line_tag, line_holder, tagged_str)
    tagged_str = re.sub(caption_tag, caption_holder, tagged_str)

    return tagged_str

def sigma_preprocess(file_path, line_holder='µ', caption_holder='§', srt=True):
    tagged_str = preprocess(file_path, srt=srt)
    n_boundaries = len(list(re.finditer(r"%s|%s" % (line_holder,caption_holder), tagged_str)))
    n_words = len(list(re.finditer(r"[^ %s%s\r\n]+" % (line_holder,caption_holder), tagged_str)))

    alpha = n_boundaries / n_words

    # Removing boundaries
    string = re.sub(r"%s|%s" % (line_holder, caption_holder), r" ", tagged_str)
    # Removing potential multiple spaces
    string = re.sub(r" {2,}", r" ", string)

    sents = string.splitlines()
    sents = [sent.strip() for sent in sents]

    # Inserting spaces around boundaries
    tagged_str = re.sub(r"(%s|%s)" % (line_holder, caption_holder), r" \1 ", tagged_str)
    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)

    tagged_sents = tagged_str.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]

    assert len(sents) == len(tagged_sents)

    return alpha, sents, tagged_sents

def GetSubtitleIds(tagged_sents):
    ids = []
    id = 1
    for x in range(len(tagged_sents)):
        temp = []
        temp.append(id)
        id += 1
        
        count = len(re.findall(r'§',tagged_sents[x])) - 1
        if count > 0:
            for x in range(count):
                temp.append(id)
                id += 1
        
        ids.append(temp)
    return ids

def GetEvenSentences(ref_sents, sys_sents, ref_tagged_sents, sys_tagged_sents):
    new_ref_sents = []
    new_sys_sents = []
    new_ref_tagged_sents = []
    new_sys_tagged_sents = []

    temp_ref_sents = ''
    temp_sys_sents = ''
    temp_ref_tagged_sents = ''
    temp_sys_tagged_sents = ''

    ref_id = 0
    sys_id = 0

    while ref_id < len(ref_sents) and sys_id < len(sys_sents):
        if ref_id == 0 and sys_id == 0:
            temp_ref_sents = ref_sents[ref_id]
            temp_sys_sents = sys_sents[sys_id]
            temp_ref_tagged_sents = ref_tagged_sents[ref_id]
            temp_sys_tagged_sents = sys_tagged_sents[sys_id]
            ref_id += 1
            sys_id += 1
        else:
            ref_bounds = len(re.findall(r'§',temp_ref_tagged_sents))
            sys_bounds = len(re.findall(r'§',temp_sys_tagged_sents))

            if ref_bounds == sys_bounds:
                new_ref_sents.append(temp_ref_sents)
                new_sys_sents.append(temp_sys_sents)
                new_ref_tagged_sents.append(temp_ref_tagged_sents)
                new_sys_tagged_sents.append(temp_sys_tagged_sents)
                temp_ref_sents = ref_sents[ref_id]
                temp_sys_sents = sys_sents[sys_id]
                temp_ref_tagged_sents = ref_tagged_sents[ref_id]
                temp_sys_tagged_sents = sys_tagged_sents[sys_id]
                ref_id += 1
                sys_id += 1
            else:
                if ref_bounds < sys_bounds:
                    temp_ref_sents += ' ' + ref_sents[ref_id]
                    temp_ref_tagged_sents += ' ' + ref_tagged_sents[ref_id]
                    ref_id += 1
                else:
                    temp_sys_sents += ' ' + sys_sents[sys_id]
                    temp_sys_tagged_sents += ' ' + sys_tagged_sents[sys_id]
                    sys_id += 1
    
    if len(temp_ref_sents) > 0 and len(temp_sys_sents):
        new_ref_sents.append(temp_ref_sents)
        new_sys_sents.append(temp_sys_sents)
        new_ref_tagged_sents.append(temp_ref_tagged_sents)
        new_sys_tagged_sents.append(temp_sys_tagged_sents)
    
    return new_ref_sents, new_sys_sents, new_ref_tagged_sents, new_sys_tagged_sents

def CheckSegmentationEquality(sys_file_path, ref_file_path, srt=True):
    bleu = BLEU()
    chrf = CHRF()
    ter = TER()

    ref_alpha, ref_sents, ref_tagged_sents = sigma_preprocess(ref_file_path, srt=srt)
    sys_alpha, sys_sents, sys_tagged_sents = sigma_preprocess(sys_file_path, srt=srt)

    ref_sents, sys_sents, ref_tagged_sents, sys_tagged_sents = GetEvenSentences(ref_sents, sys_sents, ref_tagged_sents, sys_tagged_sents)

    sys_ids = GetSubtitleIds(sys_tagged_sents)
    ref_ids = GetSubtitleIds(ref_tagged_sents)

    count = len(sys_ids) if len(sys_ids) < len(ref_ids) else len(ref_ids)

    for x in range(count):
        if not(sys_ids[x] == ref_ids[x]):
            message = 'Not equal at id '+str(x)+': sys('+str(sys_ids[x])+') ref('+str(ref_ids[x])+')'
            text = 'sys('+str(sys_tagged_sents[x])+')\nref('+str(ref_tagged_sents[x])+')'
            return message+'\n'+text

    if not(len(sys_ids) == len(ref_ids)):
        print(sys_ids[count-1],ref_ids[count-1])
        return
    
    # else:
    #     for x in range(len(sys_ids)):
    #         if not(sys_sents[x] == ref_sents[x]):
    #             print(sys_sents[x])
    #             print(ref_sents[x])
    #             print('-----------------------------------------------')

    bleu_nb_score = bleu.corpus_score(sys_sents, [ref_sents])
    bleu_br_score = bleu.corpus_score(sys_tagged_sents, [ref_tagged_sents])

    alpha = sys_alpha
    p1, p2, p3, p4 = bleu_nb_score.precisions
    bleu_br = bleu_br_score.score
    bpp = bleu_br_score.bp

    pp1_ub = (p1 + alpha * 100) / (1 + alpha)
    pp2_ub = ((1 - alpha) * p2 + 2 * alpha * p1) / (1 + alpha)
    pp3_ub = ((1 - 2 * alpha) * p3 + 3 * alpha * p2) / (1 + alpha)
    pp4_ub = ((1 - 3 * alpha) * p4 + 4 * alpha * p3) / (1 + alpha)
    bleu_br_ub = bpp * exp((log(pp1_ub) + log(pp2_ub) + log(pp3_ub) + log(pp4_ub)) / 4)

    sigma = 100 * bleu_br / bleu_br_ub

    chrf_score = chrf.corpus_score(sys_sents, [ref_sents])
    ter_score = ter.corpus_score(sys_sents, [ref_sents])

    # sigma_score = { 'Sigma': sigma,
    #             'alpha': alpha,
    #             'BLEU_br+': bleu_br_ub,
    #             "p'1+": pp1_ub,
    #             "p'2+": pp2_ub,
    #             "p'3+": pp3_ub,
    #             "p'4+": pp4_ub,
    #             'BLEU_nb': bleu_nb_score,
    #             'BLEU_br': bleu_br_score}

    sigma_score = { 'Sigma': float("{:.3f}".format(sigma)),
                    'BLEU': float("{:.3f}".format(bleu_nb_score.score)),
                    'chrF++':chrf_score,
                    'TER':ter_score,
                }

    return sigma_score

def MainQualityEvaluator():
    pathHyp = sys.path[-1]+'DataPreparator\\TranslatedOriginalToParalel\\'
    pathRef = sys.path[-1]+'DataPreparator\\Paralel\\'
        
    for file in variant:
        result = open(sys.path[-1]+'SubtitleEvaluator\\QualityScores\\'+file+'.txt', mode='w', encoding='utf-8-sig')
        folder = variant[file]
        for x in range(5):
            hypFile = pathHyp+folder+hypothesesFiles[x]+file
            refFile = pathRef+referenceFiles[x]

            result.write(hypothesesFiles[x]+'\n')
            result.write(str(CheckSegmentationEquality(hypFile,refFile))+'\n')
        result.close()

def WordAlignerCompare():
    path = sys.path[-1]+'DataPreparator\\TranslatedParalel\\'
        
    folderTilde = 'TildeTilde\\'
    folderSimAlign = 'TildeSimAlign\\'
    for x in range(5):
        hypFile = path+folderSimAlign+hypothesesFiles[x]+'tilde.SimAlign.srt'
        refFile = path+folderTilde+hypothesesFiles[x]+'tilde.tilde.srt'

        print(hypothesesFiles[x]+'\n')
        print(CheckSegmentationEquality(hypFile,refFile))

if __name__ == "__main__":
    MainQualityEvaluator()
    # WordAlignerCompare()
    