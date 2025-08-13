from modules.image_generator import ImageGenerator
import logging

logging.basicConfig(level=logging.INFO)

try:
    generator = ImageGenerator()
    engines = generator.get_available_engines()

    if engines:
        print("\n✅ Доступные движки:")
        for engine in engines:
            print(f"ID: {engine['id']}")
            print(f"Название: {engine['name']}")
            print(f"Описание: {engine.get('description', 'N/A')}")
            print("-" * 50)
    else:
        print("❌ Не удалось получить список движков")

except Exception as e:
    print(f"❌ Ошибка: {e}")
