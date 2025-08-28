# Модуль для генерации. АПИ, запросы, клиенты, etc.
*бэкенд проекта PHARAON*
***
## Ключевые библиотеки
* Click ([https://palletsprojects.com/p/click/](https://click.palletsprojects.com/en/8.1.x/))
* Jinja2 ([https://jinja.palletsprojects.com/](https://jinja.palletsprojects.com/en/3.1.x/))
* pydantic-settings ([https://pypi.org/project/pydantic-settings/](https://pypi.org/project/pydantic-settings/))
***
## Модуль для генерации новой ручки *generate_api*

#### Создаётся обработчик на основе шаблона с заданными параметрами:

  * :param private_type: Тип приватности (internal, public)

  * :param url: url нового хендлера. Не надо указывать префикс     /api/internal
  или /api/<service>/public, только то, что далее.

  * :param method: метод хендлера (get, post, etc).

  Так же создаётся файл для тестирования.
  * ***new_filepath*** - переменная, которая определяет путь к месту, где будет храниться новый обработчик.
    #### Она строится следующим образом:
        new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/web/api/{private_type}")
  * Пример запроса:
    ```shell
    python ./gen/generate.py api internal /test post
    ```
***
## Модуль для создания нового запроса *generate_query*
#### Создаётся обьект Environment для Jinja2 с указанием пути к шаблону
#### Создаётся обработчик с заданными параметрами для создания нового файла SQL - запроса:
  * :param client: Сервис, для которого генерить запрос.     service_db,
    antares_db, etc...     В папку с таким именем будет положен запрос.

  * :param filename: Имя запроса

  * :param return_type: none | fetchall | fetchone

  * ***new_filepath*** - переменная, которая определяет путь к месту, где будет храниться новый файл с запросом.
    #### Она строится следующим образом:
        new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/db/{client}")
  * Пример запроса:
    ```shell
    python ./gen/generate.py query service_db init_query fetchall
    ```
***
## Модуль для подключения сервиса в проект *generate_client_connect*
#### В модуле проверяется существует ли указанный сервис в словаре SERVICES_CONFIG, добавляются импорты и инициализация в файлы настроек и клиентов для конкретного сервиса, а также удаляются строки проверки типов из файла настроек.
  * :param service_name: Название сервиса.
  * Пример запроса:
    ```shell
    python ./gen/generate.py service_name
    ```
***
## Модуль для синхронизации values.yaml и settings *generate_values*
#### функция реализованная в модуле сравнивает существующие переменные окружения с переменными, определенными в настройках проекта. Если какие-либо переменные отсутствуют в values.yaml, они добавляются.
  * :param service_name: Название сервиса.
***
## Модуль для создания новой taskiq таски *generate_task*
#### Внутри функции task, создаётся новая задача (task) на основе шаблона. Также генерируется имя файла задачи, которое зависит от передаваемого task_name.
  * :param task_name: Название таски. Должно начинаться с task_*     Если не
     начинается, то автоматически добавится к названию.

#### В конце команда task вызывает функцию _generate_test для создания файла тестирования.
  * ***new_filepath*** - переменная, которая определяет путь к месту, где будет храниться новый файл с задачей.
   #### Она строится следующим образом:
        new_filepath = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/tasks/{new_filename}")
  * Пример запроса:
    ```shell
    python ./gen/generate.py task task_init_serv
    ```
***
## Модуль для создания нового воркера *generate_worker*
#### Функция worker принимает один аргумент
  * :param worker_name: Название воркера.
#### Внутри функции worker создаётся новый воркер (worker) в соответствии с заданным именем. Она также включает в себя создание файлов воркера, настроек, тестов и обновление настроек проекта.
  * ***worker_base_path*** - переменная, которая определяет путь к месту, где будет храниться новый файл с воркером.
    #### Она строится следующим образом:
        worker_base_path = PROJECT_ROOT.joinpath(f"{SERVICE_NAME_LOWER}/workers/{worker_name}"
  * Пример запроса:
    ```shell
    python ./gen/generate.py worker worker_test
    ```
***
