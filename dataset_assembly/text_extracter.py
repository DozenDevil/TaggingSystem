import docx, PyPDF2, pdfplumber, pytesseract 
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
from PIL import Image
from pdf2image import convert_from_path
from doc2docx import convert
from os import remove
from itertools import chain
from striprtf.striprtf import rtf_to_text
from assembly_config import tesseract_path, poppler_path

pytesseract.pytesseract.tesseract_cmd = tesseract_path

class PdfExtracter:
    
    def __init__(self, cropped_name='cropped_image.pdf', image_name='PDF_image.png'):
        self.cropped_name = cropped_name
        self.image_name = image_name
    
    def text_extraction(self, element) -> tuple:
        # Извлекаем текст из вложенного текстового элемента
        line_text = element.get_text()
        
        # Находим форматы текста
        # Инициализируем список со всеми форматами, встречающимися в строке текста
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Итеративно обходим каждый символ в строке текста
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Добавляем к символу название шрифта
                        line_formats.append(character.fontname)
                        # Добавляем к символу размер шрифта
                        line_formats.append(character.size)
        # Находим уникальные размеры и названия шрифтов в строке
        format_per_line = list(set(line_formats))
        
        # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
        return (line_text, format_per_line)

    def crop_image(self, element, pageObj):
        # Получаем координаты для вырезания изображения из PDF
        [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
        # Обрезаем страницу по координатам (left, bottom, right, top)
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)
        # Сохраняем обрезанную страницу в новый PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(pageObj)
        # Сохраняем обрезанный PDF в новый файл
        with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

    def convert_to_images(self, input_file,):
        images = convert_from_path(input_file, poppler_path=poppler_path)
        image = images[0]
        output_file = "PDF_image.png"
        image.save(output_file, "PNG")

    def image_to_text(self, image_path) -> str:
        # Считываем изображение
        img = Image.open(image_path)
        # Извлекаем текст из изображения
        text = pytesseract.image_to_string(img)
        return text

    def extract_table(self, pdf_path, page_num, table_num):
        # Открываем файл pdf
        pdf = pdfplumber.open(pdf_path)
        # Находим исследуемую страницу
        table_page = pdf.pages[page_num]
        # Извлекаем соответствующую таблицу
        table = table_page.extract_tables()[table_num]
        return table

    def table_converter(self, table) -> str:
        table_string = ''
        # Итеративно обходим каждую строку в таблице
        for row_num in range(len(table)):
            row = table[row_num]
            # Удаляем разрыв строки из текста с переносом
            cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
            # Преобразуем таблицу в строку
            table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
        # Удаляем последний разрыв строки
        table_string = table_string[:-1]
        return table_string

    def extract(self, doc_path: str) -> str:
        '''
            Функция парсинга doc и docx файлов
            * doc_path - путь к файлу
        '''
        # Находим путь к PDF

        # создаём объект файла PDF
        pdfFileObj = open(doc_path, 'rb')
        # создаём объект считывателя PDF
        pdfReaded = PyPDF2.PdfReader(pdfFileObj)

        # Создаём словарь для извлечения текста из каждого изображения
        text_per_page = {}
        # Извлекаем страницы из PDF
        for pagenum, page in enumerate(extract_pages(doc_path)):
            
            # Инициализируем переменные, необходимые для извлечения текста со страницы
            pageObj = pdfReaded.pages[pagenum]
            page_text = []
            line_format = []
            text_from_images = []
            text_from_tables = []
            page_content = []
            # Инициализируем количество исследованных таблиц
            table_num = 0
            first_element= True
            table_extraction_flag= False
            # Открываем файл pdf
            pdf = pdfplumber.open(doc_path)
            # Находим исследуемую страницу
            page_tables = pdf.pages[pagenum]
            # Находим количество таблиц на странице
            tables = page_tables.find_tables()


            # Находим все элементы
            page_elements = [(element.y1, element) for element in page._objs]
            # Сортируем все элементы по порядку нахождения на странице
            page_elements.sort(key=lambda a: a[0], reverse=True)

            # Находим элементы, составляющие страницу
            for i,component in enumerate(page_elements):
                # Извлекаем положение верхнего края элемента в PDF
                pos=component[0]
                # Извлекаем элемент структуры страницы
                element = component[1]
                
                # Проверяем, является ли элемент текстовым
                if isinstance(element, LTTextContainer):
                    # Проверяем, находится ли текст в таблице
                    if table_extraction_flag == False:
                        # Используем функцию извлечения текста и формата для каждого текстового элемента
                        (line_text, format_per_line) = self.text_extraction(element)
                        # Добавляем текст каждой строки к тексту страницы
                        
                        try:
                            val = int(line_text)
                        except ValueError:
                            page_text.append(line_text)
                            # Добавляем формат каждой строки, содержащей текст
                            line_format.append(format_per_line)
                            page_content.append(line_text)
                            
                    else:
                        # Пропускаем текст, находящийся в таблице
                        pass

                # Проверяем элементы на наличие изображений
                if isinstance(element, LTFigure):
                    # Вырезаем изображение из PDF
                    self.crop_image(element, pageObj)
                    # Преобразуем обрезанный pdf в изображение
                    
                    self.convert_to_images(self.cropped_name)
                    # Извлекаем текст из изображения
                    
                    image_text = self.image_to_text(self.image_name)
                    text_from_images.append(image_text)
                    page_content.append(image_text)
                    # Добавляем условное обозначение в списки текста и формата
                    #page_text.append('image')
                    #line_format.append('image')

                # Проверяем элементы на наличие таблиц
                if isinstance(element, LTRect):
                    # Если первый прямоугольный элемент
                    if first_element == True and (table_num+1) <= len(tables):
                        # Находим ограничивающий прямоугольник таблицы
                        lower_side = page.bbox[3] - tables[table_num].bbox[3]
                        upper_side = element.y1 
                        # Извлекаем информацию из таблицы
                        table = self.extract_table(doc_path, pagenum, table_num)
                        # Преобразуем информацию таблицы в формат структурированной строки
                        table_string = self.table_converter(table)
                        # Добавляем строку таблицы в список
                        text_from_tables.append(table_string)
                        page_content.append(table_string)
                        # Устанавливаем флаг True, чтобы избежать повторения содержимого
                        table_extraction_flag = True
                        # Преобразуем в другой элемент
                        first_element = False
                        # Добавляем условное обозначение в списки текста и формата
                        #page_text.append('table')
                        #line_format.append('table')

                    # Проверяем, извлекли ли мы уже таблицы из этой страницы
                    if element.y0 >= lower_side and element.y1 <= upper_side:
                        pass
                    elif not isinstance(page_elements[i+1][1], LTRect):
                        table_extraction_flag = False
                        first_element = True
                        table_num+=1


            # Создаём ключ для словаря
            dctkey = 'Page_'+str(pagenum)
            # Добавляем список списков как значение ключа страницы
            text_per_page[dctkey]= page_text#[page_text, line_format, text_from_images,text_from_tables, page_content]

        # Закрываем объект файла pdf
        pdfFileObj.close()

        # Удаляем созданные дополнительные файлы
        remove(self.cropped_name)
        remove(self.image_name)

        # Удаляем содержимое страницы
        result_parts = []
        for v in text_per_page.values():
            text_parts = list(chain.from_iterable(v))
            print(text_parts)
            result_parts.append(''.join(text_parts))
            
        result = ''.join(result_parts)
        return result

class DocAndDocxExtracter:
    def extract(doc_path: str) -> str:
        '''
            Функция парсинга doc и docx файлов
            * doc_path - путь к файлу
        '''
        if doc_path[-3:] == 'doc':
            convert(doc_path)
            remove(doc_path)
            doc_path += 'x'
        
        doc = docx.Document(doc_path)
        text_parts = [[run.text for run in paragraph.runs] for paragraph in doc.paragraphs]
        text_parts = list(chain.from_iterable(text_parts))
        return ''.join(text_parts)

class RtfExtracter:
    def extract(doc_path: str) -> str:
        '''
            Функция парсинга doc и docx файлов
            * doc_path - путь к файлу
        '''
        with open(doc_path, 'r') as file:
            text = file.read()
            text = rtf_to_text(text)
            return text
        
class TextExtracter:
    def extract(doc_path: str) -> str|None:
        if doc_path[-3:] == 'doc' or doc_path[-4:] == 'docx':
            return DocAndDocxExtracter.extract(doc_path)
        elif doc_path[-3:] == 'rtf':
            return RtfExtracter.extract(doc_path)
        elif doc_path[-3:] == 'pdf':
            pe = PdfExtracter()
            return pe.extract(doc_path)
        return None
    
    