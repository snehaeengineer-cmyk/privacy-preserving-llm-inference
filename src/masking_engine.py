from datetime import datetime 

  

  

def dob_to_age_band(dob_text): 

    """ 

    Convert exact date of birth into an approximate age band. 

    Example: 12.03.1980 -> age group 40s 

    """ 

  

    try: 

        dob = datetime.strptime(dob_text, "%d.%m.%Y") 

        current_year = datetime.now().year 

        age = current_year - dob.year 

        decade = (age // 10) * 10 

        return f"age group {decade}s" 

    except ValueError: 

        return "age group unknown" 

  

  

def mask_text(text, entities): 

    """ 

    Replace detected PII entities with placeholders or generalized values. 

  

    Special handling: 

    - Names, phones, emails, IDs, locations are replaced with placeholders. 

    - Date of birth is generalized to an age group. 

    - If the text says 'born on DATE' or 'born DATE', we replace the whole phrase 

      with the age group to avoid awkward grammar. 

    """ 

  

    mapping = {} 

    counters = {} 

    masked_text = text 

  

    # Sort from end to start, so character positions do not break 

    entities = sorted(entities, key=lambda x: x["start"], reverse=True) 

  

    for entity in entities: 

        entity_type = entity["type"] 

        original_value = entity["text"] 
        
        # Preserve only biomedical entities detected by SciSpaCy. 
        # Do NOT skip MEDICAL_RECORD_ID because that is direct PII. 
        if entity.get("source") == "scispacy_bc5cdr": 
            continue 
        # Preserve age as clinically relevant quasi-identifier. 
        # The Policy Engine will warn if age combines with other risk factors. 
        if entity_type == "AGE_QUASI": 
            continue 
        #So ages like 91-year-old and age 7 remain visible, and your quasi-identifier engine can detect them.

  

        if entity_type == "DATE_OF_BIRTH": 

            age_group = dob_to_age_band(original_value) 

  

            start = entity["start"] 

            end = entity["end"] 

  

            # Check text before the date to see if it contains "born on " or "born " 

            before_text = masked_text[max(0, start - 10):start].lower() 

  

            # Replace "born on 12.03.1980" with "age group 40s" 

            if before_text.endswith("born on "): 

                phrase_start = start - len("born on ") 

                replacement = age_group 

                mapping[replacement] = original_value 

  

                masked_text = ( 

                    masked_text[:phrase_start] 

                    + replacement 

                    + masked_text[end:] 

                ) 

  

            # Replace "born 12.03.1980" with "age group 40s" 

            elif before_text.endswith("born "): 

                phrase_start = start - len("born ") 

                replacement = age_group 

                mapping[replacement] = original_value 

  

                masked_text = ( 

                    masked_text[:phrase_start] 

                    + replacement 

                    + masked_text[end:] 

                ) 

  

            # Otherwise replace only the date itself 

            else: 

                replacement = age_group 

                mapping[replacement] = original_value 

  

                masked_text = ( 

                    masked_text[:start] 

                    + replacement 

                    + masked_text[end:] 

                ) 

  

        else: 

            counters[entity_type] = counters.get(entity_type, 0) + 1 

            replacement = f"[{entity_type}_{counters[entity_type]}]" 

            mapping[replacement] = original_value 

  

            masked_text = ( 

                masked_text[:entity["start"]] 

                + replacement 

                + masked_text[entity["end"]:] 

            ) 

  

    return masked_text, mapping 