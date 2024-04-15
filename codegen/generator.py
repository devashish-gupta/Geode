from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class Generator():
    def __init__(self):
        # self.name = "TheBloke/WizardCoder-Python-13B-V1.0-GPTQ"
        self.name = "WizardLM/WizardLM-13B-V1.2"
        print(torch.cuda.get_device_name(0))
        self.model = AutoModelForCausalLM.from_pretrained(self.name,
                                             device_map="cpu",
                                            #  device=0,
                                             trust_remote_code=False,
                                             revision="main")
        # self.model.to(torch.device('cpu'))
        self.model.to('cpu').float()
        self.tokenizer = AutoTokenizer.from_pretrained(self.name, use_fast=True)
        self.pipeline = pipeline(
                            "text-generation",
                            model=self.model,
                            tokenizer=self.tokenizer,
                            max_new_tokens=512,
                            do_sample=True,
                            temperature=0.7,
                            top_p=0.95,
                            top_k=40,
                            repetition_penalty=1.1
                        )
        
        with open('codegen/base_prompt.txt', 'r') as f:
            self.base_prompt = f.read()
        
    def generate(self, user_query: str):
        '''
        Generate python code based on provided user query
        '''
        prompt = self.get_prompt(user_query)
        return self.pipeline(prompt)[0]['generated_text']

    def get_prompt(self, user_query: str) -> str:
        '''
        Incorporate user query into the prompt template
        '''
        prompt = self.base_prompt
        prompt = prompt.replace('QUERY_TAG', user_query)
        return prompt


    

