from google.adk.agents import Context
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

def select_scenario(tool_context: Context, scenario_id: str) -> dict:
    """
    Selects a scenario by ID and returns its context, triggering a persona switch.

    Args:
        tool_context: The ADK context object containing session state.
        scenario_id: The ID of the scenario to switch to.

    Returns:
        A dictionary with the scenario details (id, title_no, title_en, persona, opening_line)
        or an error message in Norwegian if the ID is invalid.
    """
    if scenario_id not in SCENARIOS:
        return {"error": f"Beklager, jeg kjenner ikke til scenarioet '{scenario_id}'."}
    
    # Initialize state
    tool_context.state["active_scenario_id"] = scenario_id
    tool_context.state["words_practiced"] = []
    tool_context.state["exchange_count"] = 0
    
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

def mark_word_practiced(tool_context: Context, word: str, correct: bool) -> str:
    """
    Marks a vocabulary word as practiced by the user.
    
    Args:
        tool_context: The ADK context.
        word: The Norwegian vocabulary word that was practiced.
        correct: True if the user used it correctly, False otherwise.
    
    Returns:
        A confirmation string.
    """
    practiced = tool_context.state.get("words_practiced", [])
    if correct and word not in practiced:
        practiced.append(word)
        tool_context.state["words_practiced"] = practiced
        return f"Flott! '{word}' er markert som lært."
    elif not correct:
        return f"Notert at '{word}' trenger mer øving."
    return f"'{word}' er allerede lært."

def get_progress(tool_context: Context) -> dict:
    """
    Returns the user's progress in the current scenario.
    
    Args:
        tool_context: The ADK context.
    
    Returns:
        A dictionary with the progress statistics.
    """
    active_scenario_id = tool_context.state.get("active_scenario_id")
    if not active_scenario_id or active_scenario_id not in SCENARIOS:
        return {"error": "Ingen aktivt scenario for å vise fremgang."}
        
    scenario = SCENARIOS[active_scenario_id]
    total_words = len(scenario.get("vocabulary", []))
    practiced = tool_context.state.get("words_practiced", [])
    practiced_count = len(practiced)
    
    return {
        "scenario_id": active_scenario_id,
        "words_practiced": practiced,
        "practiced_count": practiced_count,
        "total_words": total_words,
        "completion_percentage": (practiced_count / total_words) * 100 if total_words > 0 else 0
    }

def end_scenario(tool_context: Context) -> str:
    """
    Ends the current practice scenario, calculating accuracy and saving progress to the user's profile.
    
    Args:
        tool_context: The ADK context.
        
    Returns:
        A string summarizing the user's performance and returning to menu mode.
    """
    active_scenario_id = tool_context.state.get("active_scenario_id")
    if not active_scenario_id or active_scenario_id not in SCENARIOS:
        return "Bruk 'select_scenario' for å velge et scenario først."
        
    scenario = SCENARIOS[active_scenario_id]
    vocab = scenario.get("vocabulary", [])
    words_practiced = tool_context.state.get("words_practiced", [])
    
    target_words = {item["norwegian"] for item in vocab}
    practiced_set = set(words_practiced)
    weak_words = target_words - practiced_set
    
    completed = tool_context.state.get("user:completed_scenarios", 0)
    tool_context.state["user:completed_scenarios"] = completed + 1
    
    all_weak_words = set(tool_context.state.get("user:weak_words", []))
    all_weak_words.update(weak_words)
    tool_context.state["user:weak_words"] = list(all_weak_words)
    
    tool_context.state["active_scenario_id"] = None
    tool_context.state["words_practiced"] = []
    
    weak_str = ', '.join(weak_words) if weak_words else 'Ingen'
    return f"Scenario fullført! Du klarte {len(practiced_set)} av {len(target_words)} ord. Ord for ekstra øving: {weak_str}. Du er nå i meny-modus."

def get_user_profile(tool_context: Context) -> dict:
    """
    Retrieves the user's cross-session practice profile and statistics.
    
    Args:
        tool_context: The ADK context.
        
    Returns:
        A dictionary containing the user's statistics across all sessions.
    """
    return {
        "completed_scenarios": tool_context.state.get("user:completed_scenarios", 0),
        "weak_words": tool_context.state.get("user:weak_words", [])
    }

