from .scenarios import SCENARIOS

def list_scenarios() -> list[dict[str, str]]:
    """
    Returns the list of available practice scenarios.
    
    Returns:
        A list of dictionaries, where each contains:
          - id: the internal scenario ID
          - title_no: the Norwegian title
          - title_en: the English title
    """
    return [
        {
            "id": s["id"],
            "title_no": s["title_no"],
            "title_en": s["title_en"]
        }
        for s in SCENARIOS.values()
    ]

def select_scenario(scenario_id: str) -> dict:
    """
    Selects a scenario by ID and returns its context, triggering a persona switch.

    Args:
        scenario_id: The ID of the scenario to switch to.

    Returns:
        A dictionary with the scenario details (id, title_no, title_en, persona, opening_line)
        or an error message in Norwegian if the ID is invalid.
    """
    if scenario_id not in SCENARIOS:
        return {"error": f"Beklager, jeg kjenner ikke til scenarioet '{scenario_id}'."}
    
    scenario = SCENARIOS[scenario_id]
    return {
        "id": scenario["id"],
        "title_no": scenario["title_no"],
        "title_en": scenario["title_en"],
        "persona": scenario["persona"],
        "opening_line": scenario["opening_line"]
    }

def get_vocabulary(scenario_id: str) -> dict:
    """
    Retrieves the vocabulary list for a given scenario.

    Args:
        scenario_id: The ID of the scenario.

    Returns:
        A dictionary containing the English-Norwegian vocabulary pairs, or an error.
    """
    if scenario_id not in SCENARIOS:
        return {"error": f"Beklager, jeg kan ikke finne vokabular for '{scenario_id}'."}
    return {"vocabulary": SCENARIOS[scenario_id]["vocabulary"]}
