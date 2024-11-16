import os
import csv


class PriceMachine:
    def __init__(self):
        self.data = []

    def load_prices(self, dir_path=''):
        '''
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        Допустимые названия для столбца с товаром:
            товар
            название
            наименование
            продукт

        Допустимые названия для столбца с ценой:
            розница
            цена

        Допустимые названия для столбца с весом (в кг.):
            вес
            масса
            фасовка
        '''
        for filename in os.listdir(dir_path):
            if "price" in filename.lower() and filename.endswith('.csv'):
                with open(os.path.join(dir_path, filename), 'r', encoding='utf-8') as file:
                    reader = csv.reader(file, delimiter=',')
                    headers = next(reader)

                    try:
                        product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)
                    except StopIteration:
                        print(f"Ошибка: Не удалось найти необходимые столбцы в файле {filename}")
                        continue

                    for row in reader:
                        try:
                            product_name = row[product_idx]
                            price = float(row[price_idx])
                            weight = float(row[weight_idx])

                            price_per_kg = price / weight if weight > 0 else 0
                            self.data.append((product_name, price, weight, filename, price_per_kg))
                        except (ValueError, IndexError) as e:
                            print(f"Ошибка при обработке строки в файле {filename}: {e}")
                            continue  # Игнорировать строки с некорректными данными

    def _search_product_price_weight(self, headers):
        '''Возвращает номера столбцов для продукта, цены и веса.'''
        product_names = ['название', 'продукт', 'товар', 'наименование']
        price_names = ['цена', 'розница']
        weight_names = ['фасовка', 'масса', 'вес']

        product_idx = next(i for i, h in enumerate(headers) if h.lower() in product_names)
        price_idx = next(i for i, h in enumerate(headers) if h.lower() in price_names)
        weight_idx = next(i for i, h in enumerate(headers) if h.lower() in weight_names)

        return product_idx, price_idx, weight_idx

    def export_to_html(self, fname='output.html'):
        '''Экспортирует данные в HTML формат.'''
        sorted_data = sorted(self.data, key=lambda x: x[4])  # Сортировка по цене за кг

        result = '''<!DOCTYPE html>
    <html>
    <head>
        <title>Позиции продуктов</title>
        <style>
            body {
                margin: 0;
                padding: 7px;
            }
            table {
                border-collapse: collapse;
                width: auto;
                max-width: 800px;
                margin: 0;
            }
            th, td {
                border: 1px solid #dddddd;
                padding: 2px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Номер</th>
                <th>Название</th>
                <th>Цена</th>
                <th>Фасовка</th>
                <th>Файл</th>
                <th>Цена за кг.</th>
            </tr>'''

        for number, item in enumerate(sorted_data):
            product_name, price, weight, file_name, price_per_kg = item

            # Форматируем строки
            price_str = f"{int(price)}" if price.is_integer() else f"{price:.2f}"
            weight_str = f"{int(weight)}" if weight.is_integer() else f"{weight:.2f}"
            price_per_kg_str = self._format_price_per_kg(price_per_kg)

            result += f'<tr><td>{number + 1}</td><td>{product_name}</td><td>{price_str}</td><td>{weight_str}</td><td>{file_name}</td><td>{price_per_kg_str}</td></tr>\n'

        result += '''    </table>
    </body>
    </html>'''

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)

    def _format_price_per_kg(self, price_per_kg):
        '''Форматирует цену за килограмм.'''
        if price_per_kg.is_integer():
            return f"{int(price_per_kg):.1f}"
        elif (price_per_kg * 10) % 1 == 0:
            return f"{price_per_kg:.1f}"
        else:
            return f"{price_per_kg:.2f}"

    def find_text(self, text):
        '''Ищет текст в названиях продуктов.'''
        results = [item for item in self.data if text.lower() in item[0].lower()]
        return sorted(results, key=lambda x: x[4])  # Сортировка по цене за кг


def main():
    price_machine = PriceMachine()
    price_machine.load_prices('prices')  # Укажите путь к директории с прайсами
    price_machine.export_to_html('output.html')

    while True:
        user_input = input("Введите название товара для поиска (или 'exit' для выхода): ")
        if user_input.lower() == 'exit':
            print("Работа завершена.")
            break

        results = price_machine.find_text(user_input)

        if results:
            print(f"{'№':<3} {'Наименование':<30} {'Цена':<10} {'Вес':<5} {'Файл':<15} {'Цена за кг.':<10}")
            for number, item in enumerate(results):
                product_name, price, weight, file_name, price_per_kg = item

                price_str = f"{int(price)}" if price.is_integer() else f"{price:.2f}"
                weight_str = f"{int(weight)}" if weight.is_integer() else f"{weight:.2f}"
                price_per_kg_str = price_machine._format_price_per_kg(price_per_kg)

                print(
                    f"{number + 1:<3} {product_name:<30} {price_str:<10} {weight_str:<5} {file_name:<15} {price_per_kg_str:<10}")
        else:
            print("Товары не найдены.")


if __name__ == "__main__":
    main()
