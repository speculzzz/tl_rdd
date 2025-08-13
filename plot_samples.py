import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import torch
import torchvision.transforms as transforms


def plot_random_samples(dataset, class_name, num_samples=5):
    # Выбираем случайные индексы
    indices = random.sample(range(len(dataset)), num_samples)
    
    # Создаем сетку для отображения
    fig, axes = plt.subplots(1, num_samples, figsize=(20, 5))
    if num_samples == 1:
        axes = [axes]
    
    for idx, ax in zip(indices, axes):
        # Получаем изображение и аннотации
        image, annotation = dataset[idx]
        img_name = dataset.image_files[idx]
        
        # Конвертируем тензор обратно в PIL для отображения
        if isinstance(image, torch.Tensor):
            image = transforms.ToPILImage()(image)
        
        # Отображаем изображение
        ax.imshow(image)
        ax.axis('off')
        
        # Проверяем наличие повреждений
        if annotation[0]['class'] == 0:
            ax.set_title(f"{img_name}\nNormal", color='green')
        else:
            ax.set_title(f"{img_name}\nDamaged", color='red')
            
            # Рисуем bounding boxes и подписи
            for obj in annotation:
                if obj['bbox'] is not None:
                    xmin, ymin, xmax, ymax = obj['bbox']
                    width = xmax - xmin
                    height = ymax - ymin
                    
                    # Создаем прямоугольник
                    rect = patches.Rectangle(
                        (xmin, ymin), width, height,
                        linewidth=2, edgecolor='r', facecolor='none'
                    )
                    ax.add_patch(rect)
                    
                    # Добавляем подпись класса
                    ax.text(
                        xmin, ymin - 10, class_name[obj['class']],
                        color='white', fontsize=10, bbox=dict(facecolor='red', alpha=0.8)
                    )
    
    plt.tight_layout()
    plt.show()
