from new import run_app


if __name__ == '__main__':
    try:
        run_app()
    except KeyboardInterrupt:  # чтобы не было ошибки когда завершаю
        print('завершение работы')
