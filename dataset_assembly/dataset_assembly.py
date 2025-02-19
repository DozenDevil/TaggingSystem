import csv
from text_extractor import TextExtractor
from os import listdir
from os.path import isfile, join, exists


class DatasetAssembly:
    """
    Класс для обработки документов в указанной директории и их сохранения в CSV-файл.
    """

    def __init__(self, dir_path: str, extractor: TextExtractor):
        """
        Инициализация объекта.

        :param dir_path: Путь к директории с файлами
        :param extractor: Экземпляр класса TextExtractor для обработки документов
        """
        self.dir = dir_path
        self.extractor = extractor  # Экземпляр класса TextExtractor

    def extract(self, doc_path: str) -> str | None:
        """
        Извлекает текст из указанного документа.

        :param doc_path: Путь к файлу
        :return: Извлечённый текст или None, если файл не существует
        """
        if not exists(doc_path):  # Проверяем, существует ли файл
            return None
        return self.extractor.extract(doc_path)  # Извлекаем текст с помощью TextExtractor

    def extract_from_list(self, file_paths: list) -> list:
        """
        Извлекает текст из списка файлов.

        :param file_paths: Список путей к файлам
        :return: Список текстов, извлечённых из файлов
        """
        return [self.extract(file_path) for file_path in file_paths]

    def generate_csv(self, dir_path: str, csv_name: str = 'data.csv'):
        """
        Генерирует CSV-файл из текстов документов, расположенных в указанной директории.

        :param dir_path: Путь к директории с документами
        :param csv_name: Имя CSV-файла (по умолчанию 'data.csv')
        """

        # Получаем список всех файлов в директории, оставляя только файлы (без папок)
        all_files = listdir(dir_path)
        only_files = [f for f in all_files if isfile(join(dir_path, f))]

        # Определяем категории документов (имена файлов без расширения)
        categories = [filename.rsplit('.', 1)[0] for filename in only_files]

        # Формируем полные пути к файлам
        full_paths = [join(dir_path, filename) for filename in only_files]

        # Извлекаем текст из каждого файла
        extracted_texts = self.extract_from_list(full_paths)

        # Формируем список словарей, где каждому тексту соответствует его категория
        csv_data = []
        for text, category in zip(extracted_texts, categories):
            csv_data.append({'text': text, 'category': category})

        # Определяем заголовки CSV-файла
        fields = ['text', 'category']

        # Записываем данные в CSV-файл
        with open(csv_name, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()  # Записываем заголовки
            writer.writerows(csv_data)  # Записываем строки данных


if __name__ == '__main__':
    # Создаём экземпляр DatasetAssembly с пустой директорией и экземпляром TextExtractor
    da = DatasetAssembly('', TextExtractor())

    # Генерируем CSV-файл на основе файлов в директории 'data'
    da.generate_csv('data')
