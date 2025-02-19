import unittest
from unittest.mock import patch, mock_open, MagicMock
from dataset_assembly.text_extractor import DocAndDocxExtractor, RtfExtractor, PdfExtractor, TextExtractor
import PyPDF2
from docx import Document


class TestDocAndDocxExtractor(unittest.TestCase):
    @patch("text_extractor.Document")
    def test_extract_docx(self, mock_document):
        """Тест парсинга .docx файла"""
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.runs = [MagicMock(text="Hello"), MagicMock(text=" World")]
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc

        extractor = DocAndDocxExtractor()
        result = extractor.extract("test.docx")

        self.assertEqual(result, "Hello World")

    @patch("text_extractor.convert")
    @patch("text_extractor.remove")
    @patch("text_extractor.Document")
    def test_extract_doc(self, mock_document, mock_remove, mock_convert):
        """Тест парсинга .doc файла (конвертация в .docx)"""
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.runs = [MagicMock(text="Converted"), MagicMock(text=" Document")]
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc

        extractor = DocAndDocxExtractor()
        result = extractor.extract("test.doc")

        mock_convert.assert_called_once_with("test.doc")
        mock_remove.assert_called_once_with("test.doc")
        self.assertEqual(result, "Converted Document")


class TestRtfExtractor(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="{\\rtf1\\ansi This is RTF}")
    @patch("text_extractor.rtf_to_text", return_value="This is RTF")
    def test_extract_rtf(self, mock_rtf_to_text, mock_file):
        """Тест парсинга .rtf файла"""
        extractor = RtfExtractor()
        result = extractor.extract("test.rtf")

        mock_file.assert_called_once_with("test.rtf", "r")
        mock_rtf_to_text.assert_called_once_with("{\\rtf1\\ansi This is RTF}")
        self.assertEqual(result, "This is RTF")


class TestPdfExtractor(unittest.TestCase):
    @patch("text_extractor.extract_pages", return_value=[MagicMock()])
    @patch("PyPDF2.PdfReader")
    def test_extract_pdf(self, mock_pdf_reader, mock_extract_pages):
        """Тест парсинга .pdf файла"""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF Content"
        mock_pdf.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf

        extractor = PdfExtractor()
        result = extractor.extract("test.pdf")

        self.assertIn("PDF Content", result)
        mock_pdf_reader.assert_called_once()


class TestTextExtractor(unittest.TestCase):
    @patch.object(DocAndDocxExtractor, "extract", return_value="Extracted DOCX")
    def test_extract_docx(self, mock_extract):
        """Тест выбора экстрактора для .docx"""
        extractor = TextExtractor()
        result = extractor.extract("test.docx")

        self.assertEqual(result, "Extracted DOCX")
        mock_extract.assert_called_once_with("test.docx")

    @patch.object(RtfExtractor, "extract", return_value="Extracted RTF")
    def test_extract_rtf(self, mock_extract):
        """Тест выбора экстрактора для .rtf"""
        extractor = TextExtractor()
        result = extractor.extract("test.rtf")

        self.assertEqual(result, "Extracted RTF")
        mock_extract.assert_called_once_with("test.rtf")

    @patch.object(PdfExtractor, "extract", return_value="Extracted PDF")
    def test_extract_pdf(self, mock_extract):
        """Тест выбора экстрактора для .pdf"""
        extractor = TextExtractor()
        result = extractor.extract("test.pdf")

        self.assertEqual(result, "Extracted PDF")
        mock_extract.assert_called_once_with("test.pdf")

    def test_extract_unknown_format(self):
        """Тест на случай неизвестного расширения"""
        extractor = TextExtractor()
        result = extractor.extract("test.unknown")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
