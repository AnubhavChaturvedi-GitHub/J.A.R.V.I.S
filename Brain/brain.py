# from webscout import PhindSearch as brain


# ai = brain(
#     is_conversation=True,
#     max_tokens=800,
#     timeout=30,
#     intro='J.A.R.V.I.S',
#     filepath=r"C:\Users\chatu\Desktop\J.A.R.V.I.S\chat_hystory.txt",
#     update_file=True,
#     proxies={},
#     history_offset=10250,
#     act=None,
# )

# def Main_Brain(text):
#     r = ai.chat(text)
#     return r 

from webscout import PhindSearch

def Main_Brain(text):
    ai = PhindSearch(quiet=True, filepath=r"C:\Users\chatu\Desktop\J.A.R.V.I.S\chat_hystory.txt", is_conversation=None)

    res = ai.chat(text) # internel stream is not available for this Privider

    return res

