#!/bin/bash

# URL архива
ARCHIVE_URL="https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/Country_Specific_Data_CRDDC2022/RDD2022_Czech.zip"
# Имя файла для сохранения
ZIP_FILE="${ARCHIVE_URL##*/}"

echo "Начинаем загрузку архива..."
echo "URL: $ARCHIVE_URL"

wget "$ARCHIVE_URL" -O "$ZIP_FILE"
if [ $? -ne 0 ]; then
    echo -e "\nОшибка при загрузке файла"
    exit 1
fi

echo -e "\nЗагрузка завершена. Файл сохранен как: $ZIP_FILE"

echo "Распаковываем архив..."

unzip -o "$ZIP_FILE"
if [ $? -ne 0 ]; then
    echo "Ошибка при распаковке архива"
    exit 1
fi

echo "Архив успешно распакован в текущую директорию"

# echo "Удаляем ZIP-файл..."
# rm "$ZIP_FILE"
