import svgwrite
from xml.dom import minidom
from tkinter import Tk, Button, filedialog, Label, simpledialog, colorchooser, Listbox, MULTIPLE, Scrollbar, Frame, Canvas

# Функция для анализа цветов в SVG файле
def analyze_colors(input_file):
    doc = minidom.parse(input_file)
    paths = doc.getElementsByTagName('path')
    colors = set()
    for path in paths:
        color = path.getAttribute('stroke')
        if color.startswith('rgb'):
            colors.add(color)
    return list(colors)

# Функция для определения яркости цвета
def color_brightness(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

# Функция для определения группы цвета
def get_color_group(rgb, color_ranges):
    for group, (min_rgb, max_rgb) in color_ranges.items():
        if all(min_rgb[i] <= rgb[i] for i in range(3)) and all(rgb[i] <= max_rgb[i] for i in range(3)):
            return group
    return None

# Функция для обработки SVG файла
def process_svg(input_file, color_ranges):
    doc = minidom.parse(input_file)
    paths = doc.getElementsByTagName('path')
    color_groups = {group: [] for group in color_ranges}

    for path in paths:
        color = path.getAttribute('stroke')
        if color.startswith('rgb'):
            rgb = tuple(map(int, color[4:-1].split(',')))
            group = get_color_group(rgb, color_ranges)
            if group:
                color_groups[group].append(path)

    for group, paths in color_groups.items():
        output_file = filedialog.asksaveasfilename(title=f"Сохранить {group} файл как", defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if output_file:
            dwg = svgwrite.Drawing(output_file)
            for path in paths:
                dwg.add(dwg.path(d=path.getAttribute('d'), stroke=path.getAttribute('stroke'), fill='none'))
            dwg.save()

    print("Файлы успешно сохранены!")

# Функция для настройки групп цветов
def configure_color_groups(colors, color_list_window):
    color_ranges = {}
    num_groups = simpledialog.askinteger("Группы цветов", "Введите количество групп (2-6)", minvalue=2, maxvalue=6, parent=color_list_window)
    
    for i in range(num_groups):
        group_name = simpledialog.askstring("Группа цветов", f"Введите название группы {i+1}", parent=color_list_window)
        if not group_name:
            break
        
        # Создаем окно для выбора цветов
        frame = Frame(color_list_window)
        frame.pack(fill="both", expand=True)
        
        scrollbar = Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        listbox = Listbox(frame, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
        for color in colors:
            listbox.insert("end", color)
        listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        def select_colors():
            selected_indices = listbox.curselection()
            selected_colors = [colors[i] for i in selected_indices]
            if selected_colors:
                min_color = colorchooser.askcolor(title=f"Выберите минимальный цвет для {group_name}", parent=color_list_window)[0]
                max_color = colorchooser.askcolor(title=f"Выберите максимальный цвет для {group_name}", parent=color_list_window)[0]
                if min_color and max_color:
                    color_ranges[group_name] = (tuple(map(int, min_color)), tuple(map(int, max_color)))
            frame.destroy()
        
        Button(frame, text="Выбрать", command=select_colors).pack(pady=5)
        color_list_window.wait_window(frame)
    
    return color_ranges

# Создаем графический интерфейс
def create_gui():
    root = Tk()
    root.title("SVG Color Splitter")

    def open_file():
        input_file = filedialog.askopenfilename(title="Выберите входной SVG файл", filetypes=[("SVG files", "*.svg")])
        if input_file:
            colors = analyze_colors(input_file)
            colors.sort(key=lambda color: color_brightness(tuple(map(int, color[4:-1].split(',')))))

            # Создаем окно для отображения всех найденных цветов и выбора групп
            color_list_window = Tk()
            color_list_window.title("Найденные цвета и настройка групп")
            
            frame = Frame(color_list_window)
            frame.pack(fill="both", expand=True)
            
            scrollbar = Scrollbar(frame, orient="vertical")
            scrollbar.pack(side="right", fill="y")
            
            listbox = Listbox(frame, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
            for color in colors:
                rgb = tuple(map(int, color[4:-1].split(',')))
                hex_color = '#%02x%02x%02x' % rgb
                listbox.insert("end", f"{color}    ")
                listbox.itemconfig("end", {'bg': hex_color, 'fg': 'white' if color_brightness(rgb) < 128 else 'black'})
            listbox.pack(side="left", fill="both", expand=True)
            
            scrollbar.config(command=listbox.yview)
            
            def proceed():
                color_ranges = configure_color_groups(colors, color_list_window)
                if color_ranges:
                    process_svg(input_file, color_ranges)
            
            Button(color_list_window, text="Продолжить", command=proceed).pack(pady=5)
            color_list_window.mainloop()

    Label(root, text="Выберите SVG файл для разделения по цветам").pack(pady=10)
    Button(root, text="Открыть файл", command=open_file).pack(pady=5)
    Button(root, text="Выход", command=root.quit).pack(pady=5)

    root.mainloop()

create_gui()
