import os 
from mock_llm import mock_llm 
 
 
def send_to_llm(masked_prompt): 
   """ 
   LLM Gateway. 
 
   Modes: 
   - mock: local mock LLM for reproducible evaluation 
   - groq: Groq public API for optional real LLM demo 
   - openai: OpenAI public API if quota/billing is available 
   """ 
 
   llm_mode = os.getenv("LLM_MODE", "mock").lower() 
 
   if llm_mode == "groq": 
       return send_to_groq(masked_prompt) 
 
   if llm_mode == "openai": 
       return send_to_openai(masked_prompt) 
 
   return mock_llm(masked_prompt) 
 
 
def send_to_groq(masked_prompt): 
   """ 
   Send masked prompt to Groq API. 
   """ 
   try: 
       from groq import Groq 
       import os
 
       client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
 
       chat_completion = client.chat.completions.create( 
           model="llama-3.1-8b-instant", 
           messages=[ 
               { 
                   "role": "system",  
                    "content": ( 
                        "You are an expert clinical communication assistant. Your task is to fulfill the user's request "
                        "by either summarizing or explaining the provided clinical text in clear, simple language.\n\n"
                        "Follow these absolute constraints:\n"
                        "1. If the task is 'summarization', 'referral', or 'appointment', describe ONLY the explicit facts written "
                        "in the text. If instructions or timelines are missing, state that they were not provided.\n"
                        "2. If the task is an 'explanation', 'lab_explanation', or 'patient_explanation', define the medical term or clinical result "
                        "conceptually (e.g., explain what hypertension, HbA1c, or high cholesterol means).\n"
                        "3. Do not assume, guess, or invent details. You must NEVER list unprompted treatment plans, drug names, "
                        "or generalized lifestyle/diet/exercise recommendations (such as 150 minutes of exercise, sleep hours, or specific food lists) "
                        "unless those specific steps or numbers were explicitly written inside the user's prompt text.\n"
                        "4. Output ONLY the clinical response. Do not include introductory or concluding meta-commentary "
                        "(e.g., do not say 'Here is a summary' or 'Based on the text').\n"
                        "5. Never invent personal identifiers and preserve placeholder tokens exactly as they appear."
                    ),

                    
               }, 
               { 
                    "role": "user", 
                    "content": masked_prompt, 
               }, 
           ], 
           temperature=0.2, 
           max_tokens=250, 
       ) 
 
       return chat_completion.choices[0].message.content 

   except Exception as error:
       return f"Groq API call failed. Error: {str(error)}"
 
def send_to_openai(masked_prompt): 
   """ 
   Send masked prompt to OpenAI API. 
   """ 
 
   try: 
       from openai import OpenAI 
 
       client = OpenAI() 
 
       response = client.responses.create( 
           model="gpt-4.1-mini", 
           input=masked_prompt, 
           temperature=0.2, 
       ) 
 
       return response.output_text 
 
   except Exception as error: 
       return f"OpenAI API call failed. Error: {str(error)}" 