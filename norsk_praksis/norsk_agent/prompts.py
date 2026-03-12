def build_instruction(scenario: dict, state: dict) -> str:
    """
    Builds a dynamic system instruction based on the scenario and the user's progress.
    """
    persona = scenario.get("persona", "")
    vocabulary = scenario.get("vocabulary", [])
    
    words_practiced = state.get("words_practiced", [])
    exchange_count = state.get("exchange_count", 0)
    
    # Base setup
    instruction = f"{persona}\n\nDu må kun snakke NORSK til enhver tid.\n"
    instruction += "Svarene dine må være svært korte (1-2 små setninger).\n"
    instruction += "Dersom brukeren gjør feil, rett dem raskt og vennlig på norsk.\n\n"
    
    # Inject state awareness if vocabulary exists
    if vocabulary:
        instruction += "Brukeren prøver å lære følgende vokabular:\n"
        for v in vocabulary:
            status = " [LÆRT]" if v["no"] in words_practiced else ""
            instruction += f"- {v['no']} ({v['en']}){status}\n"
        
        instruction += "\nPrøv å styre samtalen slik at brukeren får bruk for ordene som IKKE er lært ennå.\n"
        
        if exchange_count > 0:
            instruction += f"Dere har snakket sammen i {exchange_count} utvekslinger. Fortsett naturlig.\n"
            
    return instruction
