import csv 

import os 

from datetime import datetime 

  

  

def log_event(session_id, prompt_id, event_type, details): 

    """ 

    Audit Logger. 

  

    Writes metadata-only audit events. 

    It does not store raw prompts or original PII values. 

    """ 

  

    output_path = "outputs/audit_log.csv" 

    os.makedirs("outputs", exist_ok=True) 

  

    file_exists = os.path.exists(output_path) 

  

    with open(output_path, mode="a", newline="", encoding="utf-8") as file: 

        writer = csv.writer(file) 

  

        if not file_exists: 

            writer.writerow([ 

                "timestamp", 

                "session_id", 

                "prompt_id", 

                "event_type", 

                "details" 

            ]) 

  

        writer.writerow([ 

            datetime.now().isoformat(timespec="seconds"), 

            session_id, 

            prompt_id, 

            event_type, 

            details 

        ]) 