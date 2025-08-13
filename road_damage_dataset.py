import os
import torch
import xml.etree.ElementTree as ET

from collections import Counter
from pygments.token import Escape
from torch.utils.data import Dataset
from PIL import Image


class RoadDamageDataset(Dataset):
    def __init__(self, root_dir, target_size=(600, 600), transform=None, is_test=False):
        """
        Датасет с повреждениями дорожного покрытия
        :param root_dir (string): Путь к исходным данным
        :param target_size (tuple(int, int)): Требуемый размер изображений (ширина, высота)
        :param transform (callable, optional): Трансформация изображений
        :param is_test (bool): Флаг тестового набора (без аннотаций)
        """
        self.root_dir = root_dir
        self.target_size = target_size
        self.transform = transform
        self.is_test = is_test
        self.image_dir = os.path.join(root_dir, 'images')
        self.annotation_dir = os.path.join(root_dir, 'annotations', 'xmls')

        self.class_map = {'normal': 0, 'D00': 1, 'D10': 2, 'D20': 3, 'D40': 4}
        self.class_name = list(self.class_map.keys())  # Для визуализации


        self.image_files = []
        self.annotations = {}

        if is_test:
            self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.endswith('.jpg')])
            return

        xml_files = sorted([f for f in os.listdir(self.annotation_dir) if f.endswith('.xml')])
        for xml_file in xml_files:
            try:
                img_file, objects = self._parse_xml(os.path.join(self.annotation_dir, xml_file))
                self.annotations[img_file] = objects
                self.image_files.append(img_file)
            except Exception as e:
                print(f"Error parsing {xml_file}: {e}")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.image_dir, img_name)
        image = Image.open(img_path).convert('RGB')
        annotation = self.annotations[img_name]

        if self.transform:
            image = self.transform(image)

        return image, annotation

    def _parse_xml(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Имя файла из аннотации
        filename = root.find('filename').text
        img_file = os.path.basename(filename) # Если вдруг полный путь указан

        # Получаем оригинальные размеры изображения
        size = root.find('size')
        orig_width = int(size.find('width').text)
        orig_height = int(size.find('height').text)

        # Коэффициенты масштабирования
        width_scale = self.target_size[0] / orig_width
        height_scale = self.target_size[1] / orig_height

        objects = []
        for obj in root.findall('object'):
            label_name = obj.find('name').text  # 'D00', 'D10', и т.д.
            bbox = [
                float(obj.find('bndbox/xmin').text) * width_scale,
                float(obj.find('bndbox/ymin').text) * height_scale,
                float(obj.find('bndbox/xmax').text) * width_scale,
                float(obj.find('bndbox/ymax').text) * height_scale
            ]
            class_id = self.class_map[label_name]
            objects.append({'class':torch.tensor(class_id), 'bbox': torch.tensor(bbox)})

        if not objects:
            class_id = 0
            bbox = [0, 0, self.target_size[0], self.target_size[1]]
            objects.append({'class':torch.tensor(class_id), 'bbox': torch.tensor(bbox)})

        return img_file, objects

    def get_class_distribution(self):
        class_counts = Counter()

        for annotation in self.annotations.values():
            for obj in annotation:
                class_name = self.class_name[obj['class']]
                class_counts[class_name] += 1

        return class_counts
