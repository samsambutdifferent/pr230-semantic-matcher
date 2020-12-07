import random


def log_match(original, matched, match_type):
    """ouput the original, matched and match type with a randomly generated id to log file
        params:
            orignal
                type: string
            matched
                type: string
            match_type
                type: string
        return:
            randomId
                type: int
    """
    randomId=random.randint(9999,99999)

    print({
        "id": randomId,
        "ingredient": original,
        "matched": matched,
        "match_type": match_type
    })

    return randomId
