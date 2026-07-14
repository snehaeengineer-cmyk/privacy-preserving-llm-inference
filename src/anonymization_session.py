import uuid 

from datetime import datetime 

  

  

def create_session(prompt_id, task_type, demasking_mode="generic"): 

    """ 

    Create one request-scoped anonymization session. 

  

    This represents the AnonymizationSession object from the report. 

    Each prompt gets one session ID so mappings and processing results 

    can be linked to one request only. 

    """ 

  

    session = { 

        "session_id": str(uuid.uuid4()), 

        "prompt_id": prompt_id, 

        "task_type": task_type, 

        "created_at": datetime.now().isoformat(timespec="seconds"), 

        "demasking_mode": demasking_mode, 

        "status": "created" 

    } 

  

    return session 