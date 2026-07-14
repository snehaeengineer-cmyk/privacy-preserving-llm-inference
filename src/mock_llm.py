def mock_llm(masked_prompt):
    """
    Fake LLM used for testing the proxy pipeline.
    It returns controlled responses based on preserved clinical terms.
    """

    prompt_lower = masked_prompt.lower()

    if "diabetes" in prompt_lower or "metformin" in prompt_lower or "insulin" in prompt_lower:
        return (
            "The patient should monitor blood glucose, follow dietary advice, "
            "take medication as prescribed, and attend regular follow-up appointments."
        )

    if "hypertension" in prompt_lower:
        return (
            "The patient should monitor blood pressure, reduce salt intake, "
            "follow medication instructions, and consult a clinician regularly."
        )

    if "asthma" in prompt_lower or "inhaler" in prompt_lower:
        return (
            "The patient should use the inhaler as prescribed, monitor breathing symptoms, "
            "and seek medical help if breathing becomes difficult."
        )

    if "chest pain" in prompt_lower:
        return (
            "The patient should be evaluated by a healthcare professional, "
            "especially if chest pain is severe, sudden, or associated with shortness of breath."
        )

    if "hba1c" in prompt_lower:
        return (
            "HbA1c shows average blood sugar levels over recent months. "
            "The patient should discuss whether the result is within the target range with a clinician."
        )

    if "high cholesterol" in prompt_lower:
        return (
            "The patient may benefit from lifestyle changes such as a balanced diet, "
            "regular physical activity, and follow-up lipid monitoring."
        )

    if "migraine" in prompt_lower:
        return (
            "The patient should track migraine triggers, use prescribed treatment correctly, "
            "and seek care if headaches become sudden, severe, or unusual."
        )

    if "parkinson" in prompt_lower:
        return (
            "Parkinson's disease affects movement and may cause tremor, stiffness, "
            "and slower movements. The patient should follow up with a clinician."
        )

    if "pneumonia" in prompt_lower:
        return (
            "Suspected pneumonia requires clinical assessment, especially if fever, cough, "
            "shortness of breath, or worsening symptoms are present."
        )

    if "low hemoglobin" in prompt_lower:
        return (
            "Low hemoglobin may indicate anemia. The patient should discuss possible causes "
            "such as iron deficiency or blood loss with a clinician."
        )

    if "knee pain" in prompt_lower:
        return (
            "The appointment summary should mention knee pain, symptom duration, severity, "
            "mobility limitations, and any previous injury."
        )

    if "dizziness" in prompt_lower:
        return (
            "The referral summary should include dizziness onset, triggers, associated symptoms, "
            "medications, and whether fainting or neurological symptoms occurred."
        )

    return (
        "The patient should consult a healthcare professional for further guidance."
    )