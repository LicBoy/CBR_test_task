# Окружение и запуск

Для написания автотестов использовал Python версии 3.13.0, все зависимости в `requirements.txt`. Рекомендуется запускать командой `pytest -s --html=pytest_report.html` (`-s` - для более детального вывода в консоль, `--html` - для генерации html репорта). Также поддерживается аругмент `--config=<PATH_TO_CONF>` если используется не дефолтный путь к конфигу.

## Задание 1. BalancesXML (`main.exe`)
### Комментарии к запуску:
Для запуска используется конфиг, путь к которому можно указать в параметрах запуска `pytest --config=<PATH>`, по умолчанию, берется конфиг из корневой папки `config.json`.

**Важно**: нужно заполнить путь к сформированному `Balances.xml` по пути в конфиге `balances_xml.path`, а также, для того чтобы автотесты корректно считали поля из окна приложения "Зачислено" и "Списано", и разницу из "Осталось", заполнить поля конфига `application_amounts`: `debit_total` для `Зачислено`, `credit_total` для `Списано` и `difference` для `Осталось`, т.к. взять эти данные из .exe-файла автоматически думаю не входит в список задач.

Есть возможность сгенерировать более читаемый репорт, для простоты использовал `pytest-html`. Пример уже готового репорта в [pytest-report.html](https://github.com/LicBoy/CBR_test_task/blob/main/pytest_report.html) (папка `assets` тоже относится к репорту).

Опишу кратко структуру автотестов: написаны в файле `test_balance.py` - логически разделены на 2 группы: 1-ая проверяет структуру XML файла и выводит ошибки по нему; 2-ая проверяет бизнес логику операций, например что не происходит дебета или кредита самого себя, проверка валидности сумм и т.д.

### Баги, ошибки
Много ошибок по описанию и формированию XML-файла:
1. "Документ состоит из Узла Balance": в документе ошибка `Ballance`
2. " и его детей Operation": в документе все дети находятся в нодах `Oper`
3. "-date": в документе ошибка `data` во всех элементах
4. "dbt или cdt": должен быть только 1 аттрибут из указанных, но в некоторых нодах оба.
5. "corAcc": должен быть аттрибутом, но в некоторых нодах является подэлементом.
6. Вышеуказанные проверки написаны в автотестах, касающихся XML-части, также автотесты проверяют бизнес логику, и найдены следующие проблемы: некоторые операции в качестве корреспондирующего счета указывают изначальный счет; разные даты в операциях, хотя насколько я понимаю, дата должна быть одна; и сумма выолненных операций не сходится с указанной в окне - ни дебетовая, ни кредитовая, ни итоговая разница.
7. Ошибка в окне приложения "Итогог"
