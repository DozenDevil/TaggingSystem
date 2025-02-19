from abc import ABC, abstractmethod
from os import remove

from docx import Document
from pdfminer.high_level import extract_pages
from striprtf.striprtf import rtf_to_text
from doc2docx import convert
import PyPDF2
from itertools import chain


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, doc_path: str) -> str:
        """
        Абстрактный метод для извлечения текста из документа.
        """
        pass


class DocAndDocxExtractor(BaseExtractor):
    def extract(self, doc_path: str) -> str:
        """
        Функция парсинга .doc и .docx файлов
        * doc_path - путь к файлу
        """
        # Проверяем, если это .doc файл, конвертируем в .docx
        if doc_path[-3:] == 'doc':
            convert(doc_path)
            remove(doc_path)  # Удаляем исходный .doc файл после конвертации
            doc_path += 'x'  # Изменяем путь на .docx

        # Загружаем .docx файл с помощью python-docx
        doc = Document(doc_path)
        # Извлекаем текст из всех параграфов
        text_parts = [[run.text for run in paragraph.runs] for paragraph in doc.paragraphs]
        text_parts = list(chain.from_iterable(text_parts))  # Преобразуем вложенные списки в один
        return ''.join(text_parts)  # Объединяем все части текста в одну строку


class RtfExtractor(BaseExtractor):
    def extract(self, doc_path: str) -> str:
        """
        Функция парсинга .rtf файлов
        * doc_path - путь к файлу
        """
        with open(doc_path, 'r') as file:
            text = file.read()
            text = rtf_to_text(text)
            return text


class PdfExtractor(BaseExtractor):
    def extract(self, doc_path: str) -> str:
        """
        Функция парсинга .pdf файлов
        * doc_path - путь к файлу
        """
        # создаём объект файла PDF
        pdfFileObj = open(doc_path, 'rb')
        pdfReaded = PyPDF2.PdfReader(pdfFileObj)

        text_per_page = {}
        for pagenum, page in enumerate(extract_pages(doc_path)):
            page_text = []
            # Здесь ваш код для извлечения текста из PDF
            # Например:
            pageObj = pdfReaded.pages[pagenum]
            page_text.append(pageObj.extract_text())
            text_per_page[f"Page_{pagenum}"] = page_text

        pdfFileObj.close()
        return ' '.join([t for page in text_per_page.values() for t in page])  # Возвращаем весь текст


class TextExtractor:
    def __init__(self):
        self.extractors = {
            'doc': DocAndDocxExtractor(),
            'docx': DocAndDocxExtractor(),
            'rtf': RtfExtractor(),
            'pdf': PdfExtractor()
        }

    def extract(self, doc_path: str) -> str | None:
        """
        Основной метод, который вызывает соответствующий экстрактор в зависимости от типа файла.
        """
        file_extension = doc_path.split('.')[-1].lower()

        if file_extension in self.extractors:
            extractor = self.extractors[file_extension]
            return extractor.extract(doc_path)

        return None
