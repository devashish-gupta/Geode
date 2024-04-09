
from typing import List, Optional
from transformers import pipeline

def elaborate_expert(question: str, answer: str, context: Optional[List[str]] = None) -> str:
    '''
    Impute missing values in a patch using interpolation.

    Parameters:
        question (str): The query that was asked by the user
        answer (str): The final answer obtained as a result of code generation and execution
        context (): Any intermediate results obtained during code execution, important for explaining the thought process behind the query solution

    Returns:
        str: Elaborate answer explaining the computation steps and final answer
    '''
    # if requesting an online LLM
    # openai.api_key = 'YOUR_OPENAI_API_KEY'

    # # Prepare prompt
    # prompt = f'Question: {question}\nAnswer: {answer}\n'

    # if context:
    #     context_text = '\n'.join(context)
    #     prompt += f'Context: {context_text}\n'

    # # Generate explanation
    # response = openai.Completion.create(
    #     engine='text-davinci-003',  # Choose a suitable language model
    #     prompt=prompt,
    #     max_tokens=150  # Adjust based on the desired length of the explanation
    # )

    # return response.choices[0].text.strip()

    # local LLM
    text_generator = pipeline('text-generation', model='mtgv/MobileLLaMA-1.4B-Chat') # choose a better model

    # preparing input prompt
    prompt = 'Draft an elaborate answer based on the question provided below. Do not change the provided facts and stay relevant to the question.\n'
    prompt += f'Question: {question}\n'
    prompt += f'Answer: {answer}\n'

    if context:
        context_text = ', '.join(context)
        prompt += f'Intermediate results: {context_text}\n'
        # prompt += 'Feel free to cite these results to prove your answer.'

    print(f'\nprompt: {prompt}\n')

    # generate explanation using the pipeline
    explanation = text_generator(prompt, max_length=200, 
                                 return_full_text=False, 
                                 num_return_sequences=1, 
                                 no_repeat_ngram_size=2)[0]['generated_text']

    return explanation
    
    