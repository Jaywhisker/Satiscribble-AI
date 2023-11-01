def formatTextMinutes(text_minutes:str, topic_id:str):
    """
    Format text minutes where each bullet point is seperated by a \n

    Args:
        text_minutes (string): each bullet point is seperated by \n
        topic_id  (string): topic id of the text_minutes

    Return:
        dictionary in the format of {sentenceID: sentenceText}
    """
    minutes_dictionary = {}
    list_of_sentences = text_minutes.split("\n")
    
    for index, sentence in enumerate(list_of_sentences):
        minutes_dictionary[topic_id + str(index)] = sentence.strip()

    return minutes_dictionary


def formatMongoMinutes(mongo_minutes:list):
    """
    Format mongoDB minutes in the format of [{sentenceID:xx, sentenceText:yy}, ...]

    Args:
        mongo_minutes (list): each bullet point in a dictionary
    
    Return:
        dictionary in the format of {sentenceID: sentenceText}
    """
    minutes_dictionary = {}
    for bullet_point in mongo_minutes:
        minutes_dictionary[bullet_point['sentenceID']] = bullet_point['sentenceText']

    return minutes_dictionary
    