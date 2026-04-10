def whitespace_tokenizer(text):
    tokens = text.split()
    return tokens

# Example
text = "Tokenization is the first step in NLP."
tokens = whitespace_tokenizer(text)

print(tokens)
