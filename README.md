# Документация

# COMMON часть кода документация
[Документация common](./common/readme.md)

## Запуск приложения через Docker:
```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up
```

## Установка pre-commit hooks

Для установки хуков на репозиторий выполните pre-commit install внутри оболочки poetry.
```bash
poetry shell
pre-commit install
pre-commit install -t prepare-commit-msg
```

Для проверки всех файлов до commit можно использовать:
```bash
pre-commit run -a
```


## Запуск юнит-тестов

Для запуска юнит-тестов в Docker, выполните следующие команды:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . run --rm api pytest -vv .
docker-compose -f deploy/docker-compose.yml --project-directory . down
```

Запуск юнит-тестов локально (без Docker) необходимо:
1. Запустить вашу базу данных.

Например, запуск через Docker в демоне:
```
docker-compose -f deploy/docker-compose.yml --project-directory . up -d db
```


2. Запустить юнит-тесты.
```bash
pytest -vv .
```
3. Запуск sqlfluff с фиксами.
```bash
sqlfluff fix -d postgres -t placeholder --processes 0
```

### Компиляция PO файла в MO формат, использую msgfmt библиотеку

```bash
msgfmt -o ./locale/en/LC_MESSAGES/base.mo ./locale/en/LC_MESSAGES/base.po

```
