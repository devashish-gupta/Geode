from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class Generator():
    def __init__(self):
        self.name = "TheBloke/WizardCoder-Python-13B-V1.0-GPTQ"
        self.model = AutoModelForCausalLM.from_pretrained(self.name,
                                             device_map="auto",
                                             trust_remote_code=False,
                                             revision="main")
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
        
        with open('base_prompt.txt', 'r') as f:
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
        # return f'{base_prompt}'
        pass


    

