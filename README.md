# Матчинг описания вакансий и резюме


## Цель проекта:

Создать прототип сервиса для платформы по поиску работы и сотрудников. **Код в проекте приведен к формату pep8 с помощью black**

### DoD:
Модель выдает численную оценку, насколько конкретный соискатель отвечает требованиям вакансии

## Датасет

Для релизации сервиса использоваля [IT вакансии Москва + Питер](https://www.kaggle.com/datasets/vyacheslavpanteleev1/hhru-it-vacancies-from-20211025-to-20211202) состоящий из вакансий. Также использовали [датасет с резюме](https://drive.google.com/file/d/1ikA_Ht45fXD2w5dWZ9sGTSRl-UNeCVub/view). Оба датасета включают в себя данные сервиса [HH.ru](https://hh.ru)


## Реализация сервиса

Изначально проект строился на [ElasticSearch](https://www.elastic.co/elasticsearch) и определения косинусного расстояния резюме к вакансии. Однако уже на этапе интеграции модели с докером столкнулись с тем, что ElasticSearch при версии 8.9 и выше не пинговался нормально, при более ранних версиях отказывались работать библиотеки Python. 

Поэтому было принято решение реализовывать проект с помощью [MongoDB](https://www.mongodb.com). 

### Логика работы:

Создаются эмбеддинги для входных данных с помощью SentenceTransformer. Затем выравниваются размеры векторов, добавляя нулевые значения, если вектор короче. Далее подключается база данных MongoDB, где происходит поиск наиболее подходящих резюме для вакансии. База данных прошла преобработку и содержит поле с векторами. 

Наиболее подходящие вакансии оцениваются по критерию скора косинусного расстояния. То есть вычисляется сходство между двумя векторами в многомерном пространстве. Скор считается от -1 до 1, где значение 1 означает полное совпадение (векторы указывают в одном направлении), 0 — ортогональность (векторы не связаны), а -1 — полное несовпадение (векторы указывают в противоположных направлениях). Для поиска реализованы 2 фильтра: город и готовность/не готовность к переезду 

### Сравнение моделей

[Модели](https://www.sbert.net/docs/pretrained_models.html)
Паттерны:

1) Название: Django разработчик
     Описание: написание кода
2) Название: Системный администратор
     Описание: настройка компьютерных сетей
3) Название: Технический писатель
     Описание: написание документации

Для всех случаев будем замерять косинусное расстояние.

Модель 1: all-mpnet-base-v2
Размер: 420 MB

1) 0.8946419178300312
2) 0.9609616678217091
3) 0.9419467191450088
Ответы полностью релевантны

Модель 2: all-distilroberta-v1
Размер: 290 MB

1) 0.3617517716770905
2) 0.3941240003543734
3) 0.3815626490814553
Ответы полностью нерелвантны

Модель 3: all-MiniLM-L12-v2
Размер: 120 MB

1) 0.39832232464168377
2) 0.44007692035031337
3)  0.4188687973843902

Ответы не релевантны

Резюме: 1 модель показывает отличное качество работы.

### Демо

![Demo](https://drive.google.com/drive/u/0/my-drive)


## Установка и запуск

1. Скачать и установить на компьютер [Docker](https://www.docker.com/products/docker-desktop/)


2. Скачать на компьютер проект с GitHub

3. Скачать файл [dump](https://drive.google.com/file/d/1jOjQZRiV8aXmGtO6YbqDdEedNeJAbA2T/view?usp=sharing) переместить его в папку проекта


3. Запустить Docker


4. Открыть терминал и прописать путь до папки где лежит скачанный с Github проект cd ../resume_finder


5. Прописать docker-compose up --build


6. Зайти на http://127.0.0.1:5001/

