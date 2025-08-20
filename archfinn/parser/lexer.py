# archfinn/parser/lexer.py
from lark import Lark, Token

def custom_lexer(data: str):
    tokens = []
    for line in data.splitlines():
        if line.strip() and not line.strip().startswith('#'):
            # Token hóa đơn giản – chỉ để minh họa
            tokens.append(Token('LINE', line))
    return tokens