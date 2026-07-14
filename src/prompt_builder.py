def build_llm_prompt(masked_prompt): 
   """ 
   Build the prompt that is sent outside the trusted boundary. 
   The prompt should ask for documentation-style summaries, not diagnosis or treatment. 
   """ 
 
   instruction = ( 
       "You are a careful clinical documentation assistant.\n" 
       "Your primary task is to fulfill the user's request by explaining medical conditions, "
        "lab results, or clinical terms in clear, accessible, and simple language.\n "
        "Do not refuse to explain a condition if it is mentioned alongside a patient case; "
        "instead, focus entirely on explaining the medical concepts requested. \n"
       "Use only the anonymized clinical information provided below.\n" 
       "Do not diagnose, prescribe, or create a treatment plan.\n" 
       "Do not invent patient names, phone numbers, addresses, medical IDs, " 
       "hospitals, dates, medications, tests, or other personal identifiers.\n" 
       "Preserve placeholder tokens exactly if they appear.\n" 
       "Write a short general response\n\n" 
   ) 
 
   return instruction + masked_prompt 