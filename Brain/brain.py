from webscout import PhindSearch as brain
from rich import print
from webscout.AIutel import RawDog

rawdog = RawDog()
intro_prompt = rawdog.intro_prompt

ai = brain(
    is_conversation=True,
    max_tokens=800,
    timeout=30,
    intro=intro_prompt,
    filepath=r"C:\Users\chatu\OneDrive\Desktop\Jarvis\chat_hystory.txt",
    update_file=True,
    proxies={},
    history_offset=10250,
    act=None,
)

def Main_Brain(text):
    response = ai.chat(text)
    rawdog_feedback = rawdog.main(response)
    if rawdog_feedback:
        print(rawdog_feedback)
        ai.chat(rawdog_feedback)
    return response

