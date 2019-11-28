import normalisierung

satzzeichen = ',.?!:;<>()/\{}#"\'´`‚’‘_→[]-~«»'

exlude_zeichen = '*/=→[]."'

def normalize(nlp, sentence_text, filter_satzzeichen=True, filter_exlude_zeichen=True, do_lower_case_first=True, resplit_whitespace=True):            
    if resplit_whitespace:
        sentence_text = sentence_text.replace('\t',' ')
        sentence_text = sentence_text.replace('\xa0',' ')
        sentence_text = ' '.join(sentence_text.split())
    
    normalized_sentence = normalisierung.text_normalization(sentence_text, tries=8)

    #if disable_pipeline:
    #    text_tokens = nlp(normalized_sentence, disable=["parser", "sentencizer", "lemmatizer"])
    #else:
    #    text_tokens = nlp(normalized_sentence)

    text_tokens = nlp(normalized_sentence, disable=["parser", "sentencizer", "lemmatizer"])

    # NE PROPN       proper noun
    # NNE PROPN       proper noun
    # NN  NOUN        noun, singular or mass

    lower_case_first = False
    
    if len(text_tokens) == 0:
        return ''

    try:
        if text_tokens[0].tag_ not in ["NE", "NNE", "NN"]:
            lower_case_first = True
    except:
        print("Warning could not retrieve tag!")

    if filter_satzzeichen:
        tokens = [token.text for token in text_tokens if token.text not in satzzeichen] #if (token.text != '\n' and token.text != ' ')]
        tokens = [token[:-1] if token[-1] == '-' else token for token in tokens]
        tokens = [token[1:] if token[0] == '-' else token for token in tokens]
    else:
        tokens = [token.text for token in text_tokens]

    #if len(tokens) < min_token_len:
    #    lines_dropped += 1
    #    continue

    rejoined_text = ' '.join(tokens).strip()

    #if filter_exlude_zeichen and any(character in exlude_zeichen for character in rejoined_text):
    #    lines_dropped += 1
    #    continue

    # replace all double white space
    while '  ' in rejoined_text:
        rejoined_text = rejoined_text.replace('  ',' ')

    if do_lower_case_first and lower_case_first:
        rejoined_text = rejoined_text[0].lower() + rejoined_text[1:]

    return rejoined_text


