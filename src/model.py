"""Модель слоя доступа к данным.

Сущности: Participant, Assignment, Result.
Хранение: в памяти (списки словарей).
"""

import time

_participants: list[dict] = []
_assignments: list[dict] = []
_results: list[dict] = []

_next_id: dict[str, int] = {
    "participant": 1,
    "assignment": 1,
    "result": 1,
}


def _new_id(entity: str) -> int:
    """Выдать следующий uid для сущности."""
    uid = _next_id[entity]
    _next_id[entity] += 1
    return uid


def _now_ms() -> int:
    """Текущее время в миллисекундах."""
    return int(time.time() * 1000)


def create_participant(ip: str, created: int | None = None) -> dict:
    """Создать участника с заданным IP-адресом."""
    if not ip:
        raise ValueError("ip обязателен")
    record = {
        "uid": _new_id("participant"),
        "created": created if created is not None else _now_ms(),
        "ip": ip,
    }
    _participants.append(record)
    return record


def delete_participant(uid: int) -> bool:
    """Удалить участника по uid."""
    for i, p in enumerate(_participants):
        if p["uid"] == uid:
            _participants.pop(i)
            return True
    raise KeyError(f"Participant uid={uid} не найден")


def get_all_participants() -> list[dict]:
    """Вернуть всех участников."""
    return list(_participants)


def create_assignment(
    participant: int,
    payload: str = "",
    description: str = "",
    tags: str = "",
    state: str = "new",
    created: int | None = None,
) -> dict:
    """Создать задание для участника."""
    if not any(p["uid"] == participant for p in _participants):
        raise KeyError(f"Participant uid={participant} не найден")
    record = {
        "uid": _new_id("assignment"),
        "created": created if created is not None else _now_ms(),
        "payload": payload,
        "participant": participant,
        "description": description,
        "tags": tags,
        "state": state,
    }
    _assignments.append(record)
    return record


def delete_assignment(uid: int) -> bool:
    """Удалить задание по uid."""
    for i, a in enumerate(_assignments):
        if a["uid"] == uid:
            _assignments.pop(i)
            return True
    raise KeyError(f"Assignment uid={uid} не найден")


def get_all_assignments() -> list[dict]:
    """Вернуть все задания."""
    return list(_assignments)


def create_result(
    assignment: int,
    output: str = "",
    state: str = "pending",
    error: str = "",
    duration: int = 0,
    created: int | None = None,
) -> dict:
    """Создать результат для задания."""
    if not any(a["uid"] == assignment for a in _assignments):
        raise KeyError(f"Assignment uid={assignment} не найден")
    record = {
        "uid": _new_id("result"),
        "created": created if created is not None else _now_ms(),
        "output": output,
        "state": state,
        "error": error,
        "assignment": assignment,
        "duration": duration,
    }
    _results.append(record)
    return record


def delete_result(uid: int) -> bool:
    """Удалить результат по uid."""
    for i, r in enumerate(_results):
        if r["uid"] == uid:
            _results.pop(i)
            return True
    raise KeyError(f"Result uid={uid} не найден")


def get_all_results() -> list[dict]:
    """Вернуть все результаты."""
    return list(_results)


def _cross_join_ar() -> list[tuple[dict, dict]]:
    """Декартово произведение Assignment x Result с фильтром A.uid = R.assignment."""
    return [
        (a, r)
        for a in _assignments
        for r in _results
        if a["uid"] == r["assignment"]
    ]


def _outer_join_par(
    ar_pairs: list[tuple[dict, dict]],
) -> list[dict]:
    """Внешнее соединение Participant с парами AR по P.uid = A.participant."""
    rows = []
    for p in _participants:
        matched = [
            (a, r) for (a, r) in ar_pairs
            if a["participant"] == p["uid"]
        ]
        if matched:
            for (a, r) in matched:
                rows.append({"P": p, "A": a, "R": r})
        else:
            rows.append({"P": p, "A": None, "R": None})
    return rows


def query_recent_assignments(
    window_ms: int = 9 * 60 * 1000,
) -> list[dict]:
    """Выборка по формуле реляционной алгебры из задания.

    π_{A.tags, P.ip, R.duration}(
        σ_{P.created > now − 9min}(
            P ⟗_{P.uid=A.participant} σ_{A.uid=R.assignment}(A × R)
        )
    )
    """
    threshold = _now_ms() - window_ms
    ar_pairs = _cross_join_ar()
    joined = _outer_join_par(ar_pairs)
    filtered = [row for row in joined if row["P"]["created"] > threshold]
    return [
        {
            "tags": row["A"]["tags"] if row["A"] else None,
            "ip": row["P"]["ip"],
            "duration": row["R"]["duration"] if row["R"] else None,
        }
        for row in filtered
    ]
