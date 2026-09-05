"""REPL для модели слоя доступа к данным."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import model

HELP_TEXT = """
Команды:
  cp <ip>                               создать участника
  dp <uid>                              удалить участника
  lp                                    список участников

  ca <participant_uid> <tags> [payload] создать задание
  da <uid>                              удалить задание
  la                                    список заданий

  cr <assignment_uid> <state> [output]  создать результат
  dr <uid>                              удалить результат
  lr                                    список результатов

  q                                     выборка (последние 9 минут)
  help                                  эта справка
  exit                                  выход
"""


def _fmt(items: list) -> str:
    """Форматировать список для вывода."""
    if not items:
        return "  (пусто)"
    return "\n".join(f"  {item}" for item in items)


def _handle(parts: list[str]) -> None:
    """Обработать одну команду."""
    cmd = parts[0].lower()

    if cmd == "help":
        print(HELP_TEXT)

    elif cmd == "cp":
        if len(parts) < 2:
            print("Использование: cp <ip>")
            return
        print(f"Создан: {model.create_participant(ip=parts[1])}")

    elif cmd == "dp":
        if len(parts) < 2:
            print("Использование: dp <uid>")
            return
        model.delete_participant(int(parts[1]))
        print("Удалён.")

    elif cmd == "lp":
        print(_fmt(model.get_all_participants()))

    elif cmd == "ca":
        if len(parts) < 3:
            print("Использование: ca <participant_uid> <tags> [payload]")
            return
        payload = parts[3] if len(parts) > 3 else ""
        rec = model.create_assignment(
            participant=int(parts[1]),
            tags=parts[2],
            payload=payload,
        )
        print(f"Создано: {rec}")

    elif cmd == "da":
        if len(parts) < 2:
            print("Использование: da <uid>")
            return
        model.delete_assignment(int(parts[1]))
        print("Удалено.")

    elif cmd == "la":
        print(_fmt(model.get_all_assignments()))

    elif cmd == "cr":
        if len(parts) < 3:
            print("Использование: cr <assignment_uid> <state> [output]")
            return
        output = parts[3] if len(parts) > 3 else ""
        rec = model.create_result(
            assignment=int(parts[1]),
            state=parts[2],
            output=output,
        )
        print(f"Создан: {rec}")

    elif cmd == "dr":
        if len(parts) < 2:
            print("Использование: dr <uid>")
            return
        model.delete_result(int(parts[1]))
        print("Удалён.")

    elif cmd == "lr":
        print(_fmt(model.get_all_results()))

    elif cmd == "q":
        rows = model.query_recent_assignments()
        print(f"Результат выборки ({len(rows)} строк):")
        print(_fmt(rows))

    else:
        print(f'Неизвестная команда: "{cmd}". Введите "help".')


def main() -> None:
    """Запустить REPL."""
    print('=== Модель слоя доступа к данным. Введите "help". ===')
    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break
        if not raw:
            continue
        parts = raw.split(None, 3)
        if parts[0].lower() in ("exit", "quit"):
            print("Выход.")
            break
        try:
            _handle(parts)
        except (ValueError, KeyError) as exc:
            print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
