# TaggingSystem
### Система тегирования цифровых документов в электронных хранилищах  

## Установка необходимых компонентов  
Перед запуском загрузите и установите следующие зависимости:  

1. **Tesseract OCR** – для распознавания текста:  
   [Скачать Tesseract 5.4.0 (Windows, x64)](https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe)  

2. **Poppler** – для обработки PDF:  
   [Скачать Poppler 24.02.0 (Windows, x64)](https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip)  

После установки убедитесь, что пути к этим компонентам корректно указаны в файле конфигурации. 

## Запуск  
Для корректной работы необходимо обновить ссылки в файле:  
```
dataset_assembly/assembly_config.py
```