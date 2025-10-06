import random

user_agents = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.0.9895 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.4; Nexus 7 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.84 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.2.2; QMV7B Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; MASMJS; rv:11.0) like Gecko",
    "Opera/9.64 (Windows NT 5.1; U; en) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; pl) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; hr) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; en-GB) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; en) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; de) Presto/2.1.1",
    "Opera/9.64 (X11; Linux x86_64; U; cs) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; tr) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; sv) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; pl) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; nb) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; Linux Mint; nb) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; Linux Mint; it) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; en) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; de) Presto/2.1.1",
    "Opera/9.64 (X11; Linux i686; U; da) Presto/2.1.1",
    "Opera/9.64 (Windows NT 6.1; U; MRA 5.5 (build 02842); ru) Presto/2.1.1",
    "Opera/9.64 (Windows NT 6.1; U; de) Presto/2.1.1"
]

def random_user_agent() -> str:
    return random.choice(user_agents)
