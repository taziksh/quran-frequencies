"""Buckwalter transliteration <-> Arabic Unicode conversion."""

BW_TO_AR = {
    "'": "\u0621",  # hamza
    "|": "\u0622",  # alif madda
    ">": "\u0623",  # alif hamza above
    "&": "\u0624",  # waw hamza
    "<": "\u0625",  # alif hamza below
    "}": "\u0626",  # ya hamza
    "A": "\u0627",  # alif
    "b": "\u0628",  # ba
    "p": "\u0629",  # ta marbuta
    "t": "\u062A",  # ta
    "v": "\u062B",  # tha
    "j": "\u062C",  # jim
    "H": "\u062D",  # ha
    "x": "\u062E",  # kha
    "d": "\u062F",  # dal
    "*": "\u0630",  # dhal
    "r": "\u0631",  # ra
    "z": "\u0632",  # zayn
    "s": "\u0633",  # sin
    "$": "\u0634",  # shin
    "S": "\u0635",  # sad
    "D": "\u0636",  # dad
    "T": "\u0637",  # ta (emphatic)
    "Z": "\u0638",  # za (emphatic)
    "E": "\u0639",  # ayn
    "g": "\u063A",  # ghayn
    "_": "\u0640",  # tatweel
    "f": "\u0641",  # fa
    "q": "\u0642",  # qaf
    "k": "\u0643",  # kaf
    "l": "\u0644",  # lam
    "m": "\u0645",  # mim
    "n": "\u0646",  # nun
    "h": "\u0647",  # ha
    "w": "\u0648",  # waw
    "Y": "\u0649",  # alif maqsura
    "y": "\u064A",  # ya
    "F": "\u064B",  # fathatan
    "N": "\u064C",  # dammatan
    "K": "\u064D",  # kasratan
    "a": "\u064E",  # fatha
    "u": "\u064F",  # damma
    "i": "\u0650",  # kasra
    "~": "\u0651",  # shadda
    "o": "\u0652",  # sukun
    "`": "\u0670",  # superscript alif
    "{": "\u0671",  # alif wasla
    # QAC extended Buckwalter: Uthmani orthography signs (matches JQuranTree's
    # BuckwalterEncoding; '|' above is standard Buckwalter but unused by QAC,
    # which writes alif+maddah as "A^")
    "^": "\u0653",  # maddah above
    "#": "\u0654",  # hamza above
    ":": "\u06dc",  # small high seen
    "@": "\u06df",  # small high rounded zero
    '"': "\u06e0",  # small high upright rectangular zero
    "[": "\u06e2",  # small high meem (isolated form)
    ";": "\u06e3",  # small low seen
    ",": "\u06e5",  # small waw
    ".": "\u06e6",  # small yeh
    "!": "\u06e8",  # small high noon
    "-": "\u06ea",  # empty centre low stop
    "+": "\u06eb",  # empty centre high stop
    "%": "\u06ec",  # rounded high stop with filled centre
    "]": "\u06ed",  # small low meem
}

AR_TO_BW = {v: k for k, v in BW_TO_AR.items()}


def bw_to_arabic(text: str) -> str:
    return "".join(BW_TO_AR.get(c, c) for c in text)


def arabic_to_bw(text: str) -> str:
    return "".join(AR_TO_BW.get(c, c) for c in text)
