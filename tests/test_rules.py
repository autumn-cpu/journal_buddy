from src.rules import mood_rule

def test_happy_mood():
    assert mood_rule("happy") == "Play upbeat music"

def test_unknown_mood():
    assert mood_rule("angry") == "Play something neutral"