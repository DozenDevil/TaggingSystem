import string, math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.probability import FreqDist

class TextPreprocessing:
    def __init__(self, stemmer, stop_words):
        self.stemmer = stemmer
        self.stop_words = set(stop_words)
        
    def tokenize(self, text) -> list:
        self.tokens = word_tokenize(text)
        return self.tokens

    def clean_text(self, text) -> list:
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = self.tokenize(text)
        self.clean = [word for word in words if word not in self.stop_words]
        return self.clean

    def stem_text(self, words) -> list:
        self.stemmed = [self.stemmer.stem(word) for word in words]
        return self.stemmed
    
    def preprocess(self, text) -> str:
        self.text = text
        clean = self.clean_text(self.text)
        stemmed = self.stem_text(clean)
        return ' '.join(stemmed)
    
    def freqs(self) -> dict:
        '''
            Частотный анализ последнего текста
        '''
        fdist = FreqDist(self.stemmed)
        return {word: fdist[word] / len(self.stemmed)  *  math.log(len(self.text)/fdist[word]) for word in fdist}
    
if __name__ == '__main__':
    import pandas as pd
    
    df = pd.read_csv('data.csv')
    print(df.head(5))
    
    texts = df.text
    
    lang = 'russian'
    tp = TextPreprocessing(SnowballStemmer(lang), stopwords.words(lang))
    
    processed_texts = list(map(tp.preprocess, texts))
    print(tp.freqs())