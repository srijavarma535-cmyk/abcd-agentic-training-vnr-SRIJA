def ngram_tokenizer(text, n):
    words = text.split()
    ngrams = []
    
    for i in range(len(words) - n + 1):
        ngrams.append(" ".join(words[i:i+n]))
    
    return ngrams

# Example
text = "I love learning NLP"
bigrams = ngram_tokenizer(text, 2)

print(bigrams)
