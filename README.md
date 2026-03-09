# IDailyx

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-1F6AA5?style=flat-square&logo=python&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-4B5563?style=flat-square&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)

**IDailyx** — десктопное приложение на **Python** для хранения, сортировки и редактирования игровых идей.  
Интерфейс разработан с помощью **CustomTkinter**, данные сохраняются в **JSON**.

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

## Структура проекта

```text
IDailyx/
├── .gitattributes
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
├── core/
│   ├── constants.py
│   ├── idea_manager.py
│   └── storage.py
├── data/
│   ├── ideas.json
└── ui/
    ├── dialogs.py
    ├── main_window.py
    └── styles.py
```

## Возможности

- добавление, редактирование и удаление идей;
- поиск по названию;
- фильтрация по жанру, статусу, проработке и механике;
- добавление идей в избранное;
- сортировка по дате создания и изменения;
- выбор случайной идеи;
- сохранение и загрузка данных из JSON-файла.

## Категории

### Жанры

- Шутеры
- Платформеры
- Головоломки
- Хорроры
- Рогалики
- Приключения
- Стратегии
- Симуляторы
- Мультиплеер
- Неотсортированные

### Дополнительные параметры

- **Основная механика**: стрельба, паркур, скрытность, исследование, выживание, менеджмент, выборы и последствия, строительство, коллекционирование, кооперация
- **Масштаб**: маленькая, средняя, большая
- **Перспектива**: 2D, 3D, от первого лица, от третьего лица, изометрия, top-down, текстовая
- **Платформа**: PC, mobile, console, browser
- **Проработка**: черновая идея, готово к прототипу
- **Статус**: новая, в работе, заморожена, завершена

## Поля идеи

Каждая идея содержит:

- название;
- ключевую фишку;
- краткое описание;
- жанр;
- основную механику;
- масштаб;
- перспективу;
- платформу;
- степень проработки;
- статус;
- теги;
- даты создания и изменения;
- заметки;
- отметку «избранное».

##

Постоянная ссылка на GitHub проекта: https://github.com/Treenixie/IDailyx
