from chatbot import detect_risk_level, get_bot_response


def test_detect_risk_level_high():
    assert detect_risk_level("I want to kill myself tonight") == "high"



def test_detect_risk_level_low():
    assert detect_risk_level("I had a rough day at work") == "low"



def test_crisis_response_contains_hotline():
    response = get_bot_response("I feel like suicide is the only option", "sadness")
    assert "988" in response
    assert "Tele-MANAS" in response



def test_short_message_prompts_for_more():
    response = get_bot_response("sad", "sadness")
    assert "I am here with you" in response
