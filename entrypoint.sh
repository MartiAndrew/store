#!/usr/bin/env bash

case $1 in
    start_app)
        python store/web/main.py
    ;;
    shell)
        bash
    ;;
    sqlfluff)
        sqlfluff fix -d postgres -t placeholder --processes 0
    ;;
    mypy)
        mypy ./store/
    ;;
    pytest)
        pytest -v -W ignore:ResourceWarning,error ./store/
    ;;
    flake8)
        flake8 --count ./store/
    ;;
    black)
        black --check ./store/
    ;;
    isort)
        isort ./store/
    ;;
    help) echo -e "
        Usage: $0 ARG
        Please use one from next arguments:
            'start_app' - start store application
            'shell' - run shell into docker container of an application
            'ruff' - start linter Ruff
            'format' - start formating Ruff linter
            'sqlfluff' - start linter SqlFluff
            'mypy' - start checking type annotation
            'pytest' - running all tests over pytest
            'flake8' - Run flake8 for linting
            'black' - Check code formatting using Black
            'isort' - Run isort for import sorting"
    ;;
    *) python store/web/main.py
esac
