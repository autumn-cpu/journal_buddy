# src/rules.py
def mood_rule(mood: str) -> str:
    if mood == "happy":
        return "Play upbeat music"
    return "Play something neutral"
