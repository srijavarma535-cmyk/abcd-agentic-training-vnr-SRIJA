import re

def regex_tokenizer(text):
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

# Example
text = "Tokenization is the first step in NLP."
tokens = regex_tokenizer(text)

print(tokens)
