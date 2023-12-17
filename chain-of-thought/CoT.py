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
def addition_prompt():
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
    Problem: 572+484=?\n
    Explanation: Let's think step by step. 572+484=572+400+80+4=972+80+4=1052+4=1056.\n
    Answer: 1056\n==\n
    Problem: 237+478=?\n
    Explanation: Let's think step by step. 237+400+70+8=637+70+8=707+8=715.\n
    Answer: 715\n==\n
    Problem: 194+274=?\n
    Explanation: Let's think step by step. 194+274=194+200+70+4=394+70+4=464+4=468.\n
    Answer: 468\n==\n
    Problem: 123+379=?\n
    Explanation: Let's think step by step. 123+379=123+300+70+9=423+70+9=493+9=502.\n
    Answer: 502\n==\n
    Problem: 734+235=?\n
    Explanation: Let's think step by step. 734+235=734+200+30+5=934+30+5=964+5=969.\n
    Answer: 969\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_addition_prompt():
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
    Problem: 572@484=?\n
    Explanation: Let's think step by step. 572@484=572@400@80@4=972@80@4=1052@4=1056.\n
    Answer: 1056\n==\n
    Problem: 237@478=?\n
    Explanation: Let's think step by step. 237@400@70@8=637@70@8=707@8=715.\n
    Answer: 715\n==\n
    Problem: 194@274=?\n
    Explanation: Let's think step by step. 194@274=194@200@70@4=394@70@4=464@4=468.\n
    Answer: 468\n==\n
    Problem: 123@379=?\n
    Explanation: Let's think step by step. 123@379=123@300@70@9=423@70@9=493@9=502.\n
    Answer: 502\n==\n
    Problem: 734@235=?\n
    Explanation: Let's think step by step. 734@235=734@200@30@5=934@30@5=964@5=969.\n
    Answer: 969\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def subtraction_prompt():
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
    Problem: 572-484=?\n
    Explanation: Let's think step by step. 572-484=572-400-80-4=172-80-4=92-4=88.\n
    Answer: 88\n==\n
    Problem: 478-237=?\n
    Explanation: Let's think step by step. 478-237=478-200-30-7=278-30-7=248-7=241.\n
    Answer: 241\n==\n
    Problem: 274-194=?\n
    Explanation: Let's think step by step. 274-194=274-100-90-4=174-90-4=84-4=80.\n
    Answer: 80\n==\n
    Problem: 379-123=?\n
    Explanation: Let's think step by step. 379-123=379-100-20-3=279-20-3=259-3=256.\n
    Answer: 256\n==\n
    Problem: 734-235=?\n
    Explanation: Let's think step by step. 734-235=734-200-30-5=534-30-5=504-5=499.\n
    Answer: 499\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_subtraction_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 483#389=?\n
    Explanation: Let's think step by step. 483#389=483#300#80#9=183#80#9=103#9=94.\n
    Answer: 94\n==\n
    Problem: 802#310=?\n
    Explanation: Let's think step by step. 802#310=802#300#10=502#10=492.\n
    Answer: 492\n==\n
    Problem: 298#573=?\n
    Explanation: Let's think step by step. 298#573=298#500#70#3=-202#70#3=-272#3=-275.\n
    Answer: -275\n==\n
    Problem: 749#254=?\n
    Explanation: Let's think step by step. 749#254=749#200#50#4=549#50#4=499#4=495.\n
    Answer: 495\n==\n
    Problem: 723#850=?\n
    Explanation: Let's think step by step. 723#800#50=-77#50=-127.\n
    Answer: -127\n==\n
    Problem: 572#484=?\n
    Explanation: Let's think step by step. 572#484=572#400#80#4=172#80#4=92#4=88.\n
    Answer: 88\n==\n
    Problem: 478#237=?\n
    Explanation: Let's think step by step. 478#237=478#200#30#7=278#30#7=248#7=241.\n
    Answer: 241\n==\n
    Problem: 274#194=?\n
    Explanation: Let's think step by step. 274#194=274#100#90#4=174#90#4=84#4=80.\n
    Answer: 80\n==\n
    Problem: 379#123=?\n
    Explanation: Let's think step by step. 379#123=379#100#20#3=279#20#3=259#3=256.\n
    Answer: 256\n==\n
    Problem: 734#235=?\n
    Explanation: Let's think step by step. 734#235=734#200#30#5=534#30#5=504#5=499.\n
    Answer: 499\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def multiplication_prompt():
    """Returns a prompt to add to "[PREFIX]a+b[SUFFIX]", where a,b are integers
    Returns:
        A string.
    Example: a=1111, b=2222, prefix='Input: ', suffix='\nOutput: '
    """
    prefix = '''Problem: 483*3=?\n
    Explanation: Let's think step by step. 483*3=(400+80+3)*3=400*3+80*3+3*3=1200+240+9=1449.\n
    Answer: 1449\n==\n
    Problem: 802*1=?\n
    Explanation: Let's think step by step. 802*1=(800+2)*1=800*1+2*1=800+2=802.\n
    Answer: 802\n==\n
    Problem: 298*5=?\n
    Explanation: Let's think step by step. 298*5=(200+90+8)*5=200*5+90*5+8*5=1000+450+40=1490.\n
    Answer: 1490\n==\n
    Problem: 749*2=?\n
    Explanation: Let's think step by step. 749*2=(700+40+9)*2=700*2+40*2+9*2=1400+80+18=1498.\n
    Answer: 1498\n==\n
    Problem: 723*8=?\n
    Explanation: Let's think step by step. 723*8=(700+20+3)*8=700*8+20*8+3*8=5600+160+24=5784.\n
    Answer: 5784\n==\n
    Problem: 572*4=?\n
    Explanation: Let's think step by step. 572*4=(500+70+2)*4=500*4+70*4+2*4=2000+280+8=2288.\n
    Answer: 2288\n==\n
    Problem: 478*2=?\n
    Explanation: Let's think step by step. 478*2=(400+70+8)*2=400*2+70*2+8*2=956.\n
    Answer: 956\n==\n
    Problem: 274*9=?\n
    Explanation: Let's think step by step. 274*9=(200+70+4)*9=200*9+70*9+4*9=1800+630+36=2466.\n
    Answer: 2466\n==\n
    Problem: 379*3=?\n
    Explanation: Let's think step by step. 379*3=(300+70+9)*3=300*3+70*3+9*3=900+210+27=1137.\n
    Answer: 1137\n==\n
    Problem: 734*5=?\n
    Explanation: Let's think step by step. 734*5=(700+30+4)*5=700*5+30*5+4*5=3500+150+20=3670.\n
    Answer: 3670\n==\n
    Problem: '''

    suffix = '=?\nExplanation: '

    return prefix, suffix

def masked_multiplication_prompt():
    prefix = '''Problem: 483$3=?\n
    Explanation: Let's think step by step. 483$3=(400+80+3)$3=400$3+80$3+3$3=1200+240+9=1449.\n
    Answer: 1449\n==\n
    Problem: 802$1=?\n
    Explanation: Let's think step by step. 802$1=(800+2)$1=800$1+2$1=800+2=802.\n
    Answer: 802\n==\n
    Problem: 298$5=?\n
    Explanation: Let's think step by step. 298$5=(200+90+8)$5=200$5+90$5+8$5=1000+450+40=1490.\n
    Answer: 1490\n==\n
    Problem: 749$2=?\n
    Explanation: Let's think step by step. 749$2=(700+40+9)$2=700$2+40$2+9$2=1400+80+18=1498.\n
    Answer: 1498\n==\n
    Problem: 723$8=?\n
    Explanation: Let's think step by step. 723$8=(700+20+3)$8=700$8+20$8+3$8=5600+160+24=5784.\n
    Answer: 5784\n==\n
    Problem: 572$4=?\n
    Explanation: Let's think step by step. 572$4=(500+70+2)$4=500$4+70$4+2$4=2000+280+8=2288.\n
    Answer: 2288\n==\n
    Problem: 478$2=?\n
    Explanation: Let's think step by step. 478$2=(400+70+8)$2=400$2+70$2+8$2=956.\n
    Answer: 956\n==\n
    Problem: 274$9=?\n
    Explanation: Let's think step by step. 274$9=(200+70+4)$9=200$9+70$9+4$9=1800+630+36=2466.\n
    Answer: 2466\n==\n
    Problem: 379$3=?\n
    Explanation: Let's think step by step. 379$3=(300+70+9)$3=300$3+70$3+9$3=900+210+27=1137.\n
    Answer: 1137\n==\n
    Problem: 734$5=?\n
    Explanation: Let's think step by step. 734$5=(700+30+4)$5=700$5+30$5+4$5=3500+150+20=3670.\n
    Answer: 3670\n==\n
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

