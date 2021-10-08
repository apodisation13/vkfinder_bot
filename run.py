from new import run_app


if __name__ == '__main__':
    while True:
        try:
            run_app()
        except KeyboardInterrupt:  # чтобы не было ошибки когда завершаю
            print('завершение работы')
        except Exception:
            print('вышла фигня, ну ничё')
