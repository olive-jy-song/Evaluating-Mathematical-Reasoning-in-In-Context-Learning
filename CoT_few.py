import json
import collections
import argparse
import random
import numpy as np
import requests
import re

# api key for query. see https://docs.together.ai/docs/get-started
def your_api_key():
    YOUR_API_KEY = '8d54526738ff0bc9a8144834a682925bdde27b13a6efab699103486cf70c49c1'
    return YOUR_API_KEY


# for adding small numbers (1-6 digits) and large numbers (7 digits), write prompt prefix and prompt suffix separately.
def addition_prompt_few():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 128+367=?\n
    Explanation: Let's think step by step. 128+367=128+300+60+7=428+60+7=488+7=495.\n
    Answer: 495\n==\n
    Problem: 980+929=?\n
    Explanation: Let's think step by step. 980+929=980+900+20+9=1880+20+9=1900+9=1909.\n
    Answer: 1909\n==\n
    Problem: 802+145=?\n
    Explanation: Let's think step by step. 802+145=802+100+40+5=902+40+5=942+5=947.\n
    Answer: 947\n==\n
    Problem: 254+749=?\n
    Explanation: Let's think step by step. 254+749=254+700+40+9=954+40+9=994+9=1003.\n
    Answer: 1003\n==\n
    Problem: 723+850=?\n
    Explanation: Let's think step by step. 723+850=723+800+50=1523+50=1573.\n
    Answer: 1573\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_addition_prompt_few():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 128@367=?\n
    Explanation: Let's think step by step. 128@367=128@300@60@7=428@60@7=488@7=495.\n
    Answer: 495\n==\n
    Problem: 980@929=?\n
    Explanation: Let's think step by step. 980@929=980@900@20@9=1880@20@9=1900@9=1909.\n
    Answer: 1909\n==\n
    Problem: 802@145=?\n
    Explanation: Let's think step by step. 802@145=802@100@40@5=902@40@5=942@5=947.\n
    Answer: 947\n==\n
    Problem: 254@749=?\n
    Explanation: Let's think step by step. 254@749=254@700@40@9=954@40@9=994@9=1003.\n
    Answer: 1003\n==\n
    Problem: 723@850=?\n
    Explanation: Let's think step by step. 723@850=723@800@50=1523@50=1573.\n
    Answer: 1573\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def subtraction_prompt_few():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 483-389=?\n
    Explanation: Let's think step by step. 483-389=483-300-80-9=183-80-9=103-9=94.\n
    Answer: 94\n==\n
    Problem: 802-310=?\n
    Explanation: Let's think step by step. 802-310=802-300-10=502-10=492.\n
    Answer: 492\n==\n
    Problem: 298-573=?\n
    Explanation: Let's think step by step. 298-573=298-500-70-3=-202-70-3=-272-3=-275.\n
    Answer: -275\n==\n
    Problem: 749-254=?\n
    Explanation: Let's think step by step. 749-254=749-200-50-4=549-50-4=499-4=495.\n
    Answer: 495\n==\n
    Problem: 723-850=?\n
    Explanation: Let's think step by step. 723-800-50=-77-50=-127.\n
    Answer: -127\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_subtraction_prompt_few():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 482#369=?\n
    Explanation: Let's think step by step. 482#369=482#300#60#9=182#60#9=122#9=113.\n
    Answer: 113\n==\n
    Problem: 802#310=?\n
    Explanation: Let's think step by step. 802#310=802#300#10=502#10=492.\n
    Answer: 492\n==\n
    Problem: 268#575=?\n
    Explanation: Let's think step by step. 268#575=268#500#70#5=-232#70#5=-302#3=-305.\n
    Answer: -305\n==\n
    Problem: 349#256=?\n
    Explanation: Let's think step by step. 349#256=349#200#50#6=149#50#6=99#6=93.\n
    Answer: 93\n==\n
    Problem: 783#854=?\n
    Explanation: Let's think step by step. 783#854=783#800#50#4=-17#50#4=-67#4=-71.\n
    Answer: -71\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def multiplication_prompt_few():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 443*3=?\n
    Explanation: Let's think step by step. 443*3=(400+40+3)*3=400*3+40*3+3*3=1200+120+9=1329.\n
    Answer: 1329\n==\n
    Problem: 872*1=?\n
    Explanation: Let's think step by step. 872*1=(800+70+2)*1=800*1+70*1+2*1=800+70+2=872.\n
    Answer: 872\n==\n
    Problem: 268*5=?\n
    Explanation: Let's think step by step. 268*5=(200+60+8)*5=200*5+60*5+8*5=1000+300+40=1340.\n
    Answer: 1340\n==\n
    Problem: 743*2=?\n
    Explanation: Let's think step by step. 743*2=(700+40+3)*2=700*2+40*2+3*2=1400+80+6=1486.\n
    Answer: 1498\n==\n
    Problem: 523*8=?\n
    Explanation: Let's think step by step. 523*8=(500+20+3)*8=500*8+20*8+3*8=4000+160+24=4184.\n
    Answer: 4184\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_multiplication_prompt_few():
    prefix = '''Problem: 443$3=?\n
    Explanation: Let's think step by step. 443$3=(400+40+3)$3=400$3+40$3+3$3=1200+120+9=1329.\n
    Answer: 1329\n==\n
    Problem: 872$1=?\n
    Explanation: Let's think step by step. 872$1=(800+70+2)$1=800$1+70$1+2$1=800+70+2=872.\n
    Answer: 872\n==\n
    Problem: 268$5=?\n
    Explanation: Let's think step by step. 268$5=(200+60+8)$5=200$5+60$5+8$5=1000+300+40=1340.\n
    Answer: 1340\n==\n
    Problem: 743$2=?\n
    Explanation: Let's think step by step. 743$2=(700+40+3)$2=700$2+40$2+3$2=1400+80+6=1486.\n
    Answer: 1486\n==\n
    Problem: 523$8=?\n
    Explanation: Let's think step by step. 523$8=(500+20+3)$8=500$8+20$8+3$8=4000+160+24=4184.\n
    Answer: 4184\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

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
    """Returns the post processing function to extract the answer for addition
    Returns:
        For: the function returns extracted result
    Note:
        do not attempt to "hack" the post processing function
        by extracting the two given numbers and adding them.
        the autograder will check whether the post processing function contains arithmetic additiona and the graders might also manually check.
    """
    if len(output_string.splitlines()) < 2:
        return 0
    first_line = output_string.splitlines()[2]
    only_digits = re.sub(r"\D", "", first_line)
    try:
        res = int(only_digits)
    except:
        res = 0
    return res

