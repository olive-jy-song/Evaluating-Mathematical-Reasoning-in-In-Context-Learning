import json
import collections
import argparse
import random
import numpy as np
import requests
import re

# api key for query. see https://docs.together.ai/docs/get-started
def your_api_key():
    YOUR_API_KEY = '9f94810cb560b176a4235d9d4b64b0fbdc4de3effc22646a43613eb976bfe52a' # cindy
    # YOUR_API_KEY = '8d54526738ff0bc9a8144834a682925bdde27b13a6efab699103486cf70c49c1' # vivian
    return YOUR_API_KEY


# for adding small numbers (1-6 digits) and large numbers (7 digits), write prompt prefix and prompt suffix separately.
def addition_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''
    Q: 128+367=?\n
    A: 495.\n
    Q: 980+929=?\n
    A: 1909.\n
    Q: 802+145=?\n
    A: 947.\n
    Q: 254+749=?\n
    A: 1003.\n
    Q: 723+850=?\n
    A: 1573.\n
    Q: 572+484=?\n
    A: 1056.\n
    Q: 237+478=?\n
    A: 715.\n
    Q: 194+274=?\n
    A: 468.\n
    Q: 123+379=?\n
    A: 502.\n
    Q: 734+235=?\n
    A: 969.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def masked_addition_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''
    Q: 128@367=?\n
    A: 495.\n
    Q: 980@929=?\n
    A: 1909.\n
    Q: 802@145=?\n
    A: 947.\n
    Q: 254@749=?\n
    A: 1003.\n
    Q: 723@850=?\n
    A: 1573.\n
    Q: 572@484=?\n
    A: 1056.\n
    Q: 237@478=?\n
    A: 715.\n
    Q: 194@274=?\n
    A: 468.\n
    Q: 123@379=?\n
    A: 502.\n
    Q: 734@235=?\n
    A: 969.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def subtraction_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''
    Q: 483-389=?\n
    A: 94.\n
    Q: 802-310=?\n
    A: 492.\n
    Q: 298-573=?\n
    A: -275.\n
    Q: 749-254=?\n
    A: 495.\n
    Q: 723-850=?\n
    A: -127.\n
    Q: 572-484=?\n
    A: 88.\n
    Q: 478-237=?\n
    A: 241.\n
    Q: 274-194=?\n
    A: 80.\n
    Q: 379-123=?\n
    A: 256.\n
    Q: 734-235=?\n
    A: 499.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def masked_subtraction_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''
    Q: 483#389=?\n
    A: 94.\n
    Q: 802#310=?\n
    A: 492.\n
    Q: 298#573=?\n
    A: -275.\n
    Q: 749#254=?\n
    A: 495.\n
    Q: 723#850=?\n
    A: -127.\n
    Q: 572#484=?\n
    A: 88.\n
    Q: 478#237=?\n
    A: 241.\n
    Q: 274#194=?\n
    A: 80.\n
    Q: 379#123=?\n
    A: 256.\n
    Q: 734#235=?\n
    A: 499.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def multiplication_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''
    Q: 483*3=?\n
    A: 1449.\n
    Q: 802*1=?\n
    A: 802.\n
    Q: 298*5=?\n
    A: 1490.\n
    Q: 749*2=?\n
    A: 1498.\n
    Q: 723*8=?\n
    A: 5784.\n
    Q: 572*4=?\n
    A: 2288.\n
    Q: 478*2=?\n
    A: 956.\n
    Q: 274*9=?\n
    A: 2466.\n
    Q: 379*3=?\n
    A: 1137.\n
    Q: 734*5=?\n
    A: 3670.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def masked_multiplication_prompt():
    prefix = '''
    Q: 483$3=?\n
    A: 1449.\n
    Q: 802$1=?\n
    A: 802.\n
    Q: 298$5=?\n
    A: 1490.\n
    Q: 749$2=?\n
    A: 1498.\n
    Q: 723$8=?\n
    A: 5784.\n
    Q: 572$4=?\n
    A: 2288.\n
    Q: 478$2=?\n
    A: 956.\n
    Q: 274$9=?\n
    A: 2466.\n
    Q: 379$3=?\n
    A: 1137.\n
    Q: 734$5=?\n
    A: 3670.\n
    Q: '''

    suffix = '=?\nA: '

    return prefix, suffix

def your_config():
    """Returns a config for prompting api
    Returns:
        For both short/medium, long: a dictionary with fixed string keys.
    Note:
        do not add additional keys. 
        The autograder will check whether additional keys are present.
        Adding additional keys will result in error.
    """
    config = {
        'max_tokens': 70, # max_tokens must be >= 50 because we don't always have prior on output length 
        'temperature': 0.2,
        'top_k': 50,
        'top_p': 0.7,
        'repetition_penalty': 1,
        'stop': []}
    
    return config


def your_pre_processing(s):
    return s

    
def your_post_processing(output_string):
    """Returns the post processing function to extract the A for addition
    Returns:
        For: the function returns extracted result
    Note:
        do not attempt to "hack" the post processing function
        by extracting the two given numbers and adding them.
        the autograder will check whether the post processing function contains arithmetic additiona and the graders might also manually check.
    """
    # if len(output_string.splitlines()) < 2:
    #     return 0
    # first_line = output_string.splitlines()[0]
    # only_digits = re.sub(r"\D", "", first_line)
    # try:
    #     res = int(only_digits)
    # except:
    #     res = 0
    # return res
    # Regular expression to find all numbers (including negative) followed by a period
    matches = re.findall(r'-?\d+\.', output_string)

    if matches:
        # Extract the first match and remove the period
        first_number = matches[0].rstrip('.')

        try:
            res = int(first_number)
        except ValueError:
            res = 0
        return res
    else:
        return 0

