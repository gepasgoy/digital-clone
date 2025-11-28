import log
import captcha
import two_fa


def main():
    # Последовательный запуск окон
    # Ждем закрытия окна логина
    log.window.wait_window(log.window)

    # Потом запускаем капчу
    captcha.root.wait_window(captcha.root)

    # # Потом 2FA
    # two_fa_window.wait_window(two_fa_window)

    print("Все этапы пройдены!")


if __name__ == "__main__":
    main()