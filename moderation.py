"""
moderation.py
Keyword-based helpers used by the group handlers in bot.py:
  - is_spam(): flags messages with disallowed links or banned words
  - faq_reply(): simple keyword -> canned-answer matching for common questions
  - detect_category_request(): detects "<category> chahiye" style deal requests
"""

import re

# Links from these domains are allowed (your own affiliate/shortener domains).
# Add more as needed.
ALLOWED_DOMAINS = [
    "earnkaro.com",
    "amzn.to",
    "fkrt.it",
    "t.me",
]

BAD_WORDS = [
    # keep this list to genuinely abusive/spam terms relevant to your group
    "escort", "porn", "sex chat", "betting", "casino", "loan approval",
    "crypto guaranteed", "forex signal", "join fast earn",
]

URL_RE = re.compile(r"https?://[^\s]+")


def is_spam(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()

    for bad in BAD_WORDS:
        if bad in lowered:
            return True

    for url in URL_RE.findall(text):
        if not any(domain in url for domain in ALLOWED_DOMAINS):
            return True

    return False


FAQ_KEYWORDS = {
    ("genuine", "fake", "asli", "nakli"): (
        "Haan ye 100% genuine deals hain, EarnKaro/Amazon/Flipkart ke official "
        "affiliate links se aati hain ✅"
    ),
    ("delivery", "kab aayega", "shipping"): (
        "Delivery time product/platform pe depend karta hai — Amazon/Flipkart "
        "checkout page par exact date dikh jayegi 📦"
    ),
    ("kaise kharide", "how to buy", "order kaise"): (
        "Deal ke link par click karo → seedha Amazon/Flipkart khulega → "
        "normal order jaise checkout karo 🛒"
    ),
    ("refund", "return"): (
        "Return/refund policy Amazon/Flipkart ki apni hoti hai — order ke "
        "'Returns' section mein check kar lo."
    ),
}


def faq_reply(text: str):
    if not text:
        return None
    lowered = text.lower()
    for keywords, reply in FAQ_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return reply
    return None


CATEGORY_KEYWORDS = {
    "mobile": ["mobile", "phone", "smartphone"],
    "fashion": ["fashion", "clothes", "shoes", "kapde"],
    "electronics": ["electronics", "gadget", "laptop", "earbuds", "headphone"],
    "home": ["home", "kitchen", "furniture"],
    "beauty": ["beauty", "makeup", "skincare"],
}


def detect_category_request(text: str):
    """
    Returns the category name if the message looks like a deal-request,
    e.g. 'mobile deals chahiye', 'kapde ka koi deal hai?'
    """
    if not text:
        return None
    lowered = text.lower()
    if not any(trigger in lowered for trigger in ["chahiye", "deal hai", "koi deal", "milega"]):
        return None

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return category
    return None
