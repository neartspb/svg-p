import svgwrite
from svgpathtools import svg2paths, Path, Line
import numpy as np

def add_nodes_to_path(path, interval=1.0):
    new_path = []
    for segment in path:
        length = segment.length()
        if np.isinf(length) or length == 0:
            continue  # Пропускаем сегменты с бесконечной или нулевой длиной
        num_points = int(length / interval)
        for i in range(num_points + 1):
            t = i / num_points
            point = segment.point(t)
            new_path.append(point)
    return new_path

# Загрузка SVG-файла
paths, attributes = svg2paths('input.svg')

# Создание нового SVG-файла
dwg = svgwrite.Drawing('output.svg', profile='tiny')

# Добавление узловых точек к каждому пути
for path in paths:
    new_path = add_nodes_to_path(path)
    if new_path:
        points = [(p.real, p.imag) for p in new_path]
        dwg.add(dwg.polyline(points, stroke='black', fill='none'))

# это полурабочий вариант, он сохраняет новый файл с добавленными узлами, но удаляет остальные данные