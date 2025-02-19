import math
import string
import pandas as pd

from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize


class TextPreprocessing:
    def __init__(self, stemmer, stop_words):
        """
        Инициализация класса предобработки текста.
        :param stemmer: объект стеммера для приведения слов к их основе.
        :param stop_words: список стоп-слов, которые будут удаляться из текста.
        """
        self.stemmer = stemmer
        self.stop_words = set(stop_words)  # Преобразуем список в множество для быстрого поиска

    def tokenize(self, text) -> list:
        """
        Токенизация текста (разбиение на слова).
        :param text: входной текст.
        :return: список токенов.
        """
        self.tokens = word_tokenize(text)
        return self.tokens

    def clean_text(self, text) -> list:
        """
        Очистка текста:
        - Приведение к нижнему регистру.
        - Удаление знаков пунктуации.
        - Удаление стоп-слов.

        :param text: исходный текст.
        :return: список очищенных слов.
        """
        text = text.lower()  # Приведение к нижнему регистру
        text = text.translate(str.maketrans('', '', string.punctuation))  # Удаление пунктуации
        words = self.tokenize(text)  # Разбиение текста на слова
        self.clean = [word for word in words if word not in self.stop_words]  # Удаление стоп-слов
        return self.clean

    def stem_text(self, words) -> list:
        """
        Применение стемминга к списку слов (приведение к основе).
        :param words: список очищенных слов.
        :return: список стеммированных слов.
        """
        self.stemmed = [self.stemmer.stem(word) for word in words]
        return self.stemmed

    def preprocess(self, text) -> str:
        """
        Полная предобработка текста: очистка + стемминг.
        :param text: исходный текст.
        :return: предобработанный текст в виде строки.
        """
        self.text = text
        clean = self.clean_text(self.text)  # Очистка текста
        stemmed = self.stem_text(clean)  # Применение стемминга
        return ' '.join(stemmed)  # Возвращаем текст в виде строки

    def freqs(self) -> dict:
        """
        Частотный анализ последнего обработанного текста.
        Вычисляет взвешенную частоту слов по формуле:
            (частота слова в тексте) * log(длина текста / частота слова).

        :return: словарь {слово: частота}.
        """
        fdist = FreqDist(self.stemmed)  # Частотное распределение стеммированных слов
        return {word: fdist[word] / len(self.stemmed) * math.log(len(self.text) / fdist[word]) for word in fdist}


if __name__ == '__main__':
    # Читаем CSV-файл с данными (предполагается, что в нём есть колонка "text")
    df = pd.read_csv('../data.csv')
    print(df.head(5))  # Вывод первых 5 строк

    # Получаем тексты из колонки "text"
    texts = df.text

    # Инициализируем обработчик текста для русского языка
    lang = 'russian'
    tp = TextPreprocessing(SnowballStemmer(lang), stopwords.words(lang))

    # Применяем предобработку ко всем текстам
    processed_texts = list(map(tp.preprocess, texts))

    # Выводим частотный анализ последнего обработанного текста
    print(tp.freqs())
