# Evaluating-Mathematical-Reasoning-in-In-Context-Learning 


This research examines the adaptability of Large Language Models (LLMs) in in-context learning, with a particular emphasis on mathematical reasoning involving both standard and novel notations. We explored whether LLMs can transcend pattern recognition to interpret and utilize unfamiliar symbols, linking them back to the common operations. To answer this question, we conducted a comprehensive evaluation with varying prompting methods and mathematical operations across models with different scales. Our findings reveal a significant and consistent decline in accuracy when LLMs encounter novel symbols in different prompting paradigms, underscoring the challenges they face with unfamiliar expressions.  


All experiments were performed under environment in requirements.txt. An installation with conda would be 
```
conda create -n llm-reason python=3.9.7
conda activate llm-reason
pip install -r requirements.txt
```
