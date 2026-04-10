def simple_subword_tokenizer(word):
    subwords = []
    for i in range(len(word)):
        subwords.append(word[:i+1])
    return subwords

print(simple_subword_tokenizer("token"))
