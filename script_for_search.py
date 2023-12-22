import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient


def embedding_function(text):
    embedder = SentenceTransformer("all-mpnet-base-v2", device="cpu")
    embeddings = embedder.encode(text, convert_to_tensor=True)
    return embeddings.tolist()


def find_similar_documents(wanna_job, expa, top_k=10, city=None, relocation_ready=None):
    # Создаем эмбеддинги для входных данных
    wanna_job_embedding = embedding_function(wanna_job)
    expa_embedding = embedding_function(expa)
    filter_criteria = {}

    if city is not None:
        filter_criteria["Город, переезд, командировки"] = {
            "$regex": f".*{city}.*",
            "$options": "i",
        }

    if relocation_ready is not None:
        filter_criteria["relocation_ready"] = relocation_ready
    # Выравниваем размеры векторов, добавляя нулевые значения, если вектор короче
    max_len = max(len(wanna_job_embedding), len(expa_embedding))
    wanna_job_embedding += [0] * (max_len - len(wanna_job_embedding))
    expa_embedding += [0] * (max_len - len(expa_embedding))

    # Усредняем векторы
    input_embedding = [(x + y) / 2 for x, y in zip(wanna_job_embedding, expa_embedding)]

    # Подключение к MongoDB
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["find_resume"]
    resumes_collection = db["resumes"]
    document_count = resumes_collection.count_documents({})

    # Вывод результата
    print(f"Количество документов в коллекции: {document_count}", flush=True)
    # Поиск близких документов по косинусному расстоянию
    similar_documents = resumes_collection.find(
        filter_criteria,
        {
            "sum_embeddings": 1,
            "Пол, возраст": 1,
            "ЗП": 1,
            "Ищет работу на должность:": 1,
            "Город, переезд, командировки": 1,
            "Занятость": 1,
            "График": 1,
            "Опыт работы": 1,
            "Последнее/нынешнее место работы": 1,
            "Последняя/нынешняя должность": 1,
            "Образование и ВУЗ": 1,
            "Обновление резюме": 1,
            "Авто": 1,
            "city": 1,
        },
    )

    results = []
    for document in similar_documents:
        sum_embeddings = json.loads(
            document["sum_embeddings"]
        )  # Преобразование из строки JSON в список
        sum_embeddings += [0] * (
            max_len - len(sum_embeddings)
        )  # Выравниваем размеры векторов
        sum_embeddings = [
            (x + y) / 2 for x, y in zip(sum_embeddings, input_embedding)
        ]  # Усредняем векторы
        cosine_similarity = np.dot(input_embedding, sum_embeddings) / (
            np.linalg.norm(input_embedding) * np.linalg.norm(sum_embeddings)
        )
        result_document = {
            field: document.get(field, "")
            for field in [
                "Пол, возраст",
                "ЗП",
                "Ищет работу на должность:",
                "Город, переезд, командировки",
                "Занятость",
                "График",
                "Опыт работы",
                "Последнее/нынешнее место работы",
                "Последняя/нынешняя должность",
                "Образование и ВУЗ",
                "Обновление резюме",
                "Авто",
            ]
        }
        results.append(
            {"cosine_similarity": cosine_similarity, "document": result_document}
        )

    # Сортировка по убыванию сходства и возврат топовых результатов
    results = sorted(results, key=lambda x: x["cosine_similarity"], reverse=True)[
        :top_k
    ]

    return results


if __name__ == "__main__":
    # Пример использования
    wanna_job_input = "Системный администратор"
    expa_input = "Настройка сети, администрирование сети"

    similar_documents = find_similar_documents(
        wanna_job_input, expa_input, city="Москва ", relocation_ready=True
    )

    print("Top 10 схожих документов:")
    for result in similar_documents:
        print(f"Cosine Similarity: {result['cosine_similarity']}", flush=True)
        print(result["document"], flush=True)
        print("-" * 50, flush=True)
