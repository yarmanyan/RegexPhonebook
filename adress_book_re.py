
# читаем адресную книгу в формате CSV в список contacts_list
import csv
import re

with open("phonebook_raw.csv", encoding="utf-8-sig") as f:
  rows = csv.reader(f, delimiter=",")
  contacts_list = list(rows)

# 1. Поместить Фамилию, Имя и Отчество человека в поля lastname, firstname и surname
  for row in contacts_list[1:]:  # пропускаем заголовок
    # Объединяем первые три поля и разбиваем по пробелам
    name_parts = ' '.join(row[:3]).split()

    # Распределяем части по полям
    row[0] = name_parts[0] if len(name_parts) > 0 else ''
    row[1] = name_parts[1] if len(name_parts) > 1 else ''
    row[2] = name_parts[2] if len(name_parts) > 2 else ''

# 2. Привести все телефоны в формат +7(999)999-99-99.
# Если есть добавочный номер, формат будет такой: +7(999)999-99-99 доб.9999.
  for row in contacts_list[1:]:
    phones_text = row[5]

    # Шаблон: ищем 10 цифр после кода страны
    phone_pattern = r'(\+7|8)?[\s\(\)\-]*(\d{3})[\s\(\)\-]*(\d{3})[\s\(\)\-]*(\d{2})[\s\(\)\-]*(\d{2})'
    format_func = lambda m: f"+7({m.group(2)}){m.group(3)}-{m.group(4)}-{m.group(5)}"

    # Форматируем
    result = re.sub(phone_pattern, format_func, phones_text)
    result = re.sub(r'доб\.?\s*(\d{3,5})', r' доб.\1', result, flags=re.IGNORECASE)
    result = re.sub(r'\(\s*доб\.?\s*(\d{3,5})\s*\)', r' доб.\1', result, flags=re.IGNORECASE)
    row[5] = result

# 3. Объединение дублирующихся записей по Имени и Фамилии
unique_contacts = {}

for row in contacts_list[1:]:
    # Ключ для группировки: только фамилия и имя (первые две колонки)
    key = (row[0].lower(), row[1].lower())

    if key not in unique_contacts:
        # Если записи нет, сохраняем копию
        unique_contacts[key] = row.copy()
    else:
        # Если запись уже существует, объединяем поля
        existing = unique_contacts[key]
        for i in range(len(row)):
            if existing[i] and row[i] and existing[i] != row[i]:
                # Если оба значения существуют и разные - объединяем через ";"
                existing[i] = existing[i] + ";" + row[i]
            elif not existing[i] and row[i]:
                # Если в существующей пусто, а в новой есть - заполняем
                existing[i] = row[i]
            # Если existing[i] есть, а row[i] пустой - ничего не делаем

# Формируем итоговый список (заголовок + данные)
result_contacts = [contacts_list[0]] + list(unique_contacts.values())

# 4. Удаление дублей внутри объединённых полей (если одинаковые email или телефоны)
for row in result_contacts[1:]:
    for i in range(len(row)):
        if row[i] and ';' in row[i]:
            # Разбиваем по ";", убираем дубли и пустые строки
            items = [item.strip() for item in row[i].split(';') if item.strip()]
            # Убираем дубли (сохраняя порядок)
            seen = set()
            unique_items = []
            for item in items:
                if item not in seen:
                    seen.add(item)
                    unique_items.append(item)
            # Собираем обратно через ";"
            row[i] = ';'.join(unique_items)


# Сохраняем результат
with open("phonebook.csv", "w", encoding="utf-8-sig", newline='') as f:
  datawriter = csv.writer(f, delimiter=',')
  datawriter.writerows(result_contacts)
