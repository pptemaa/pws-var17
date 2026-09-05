"""Тесты модели слоя доступа к данным."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import model


@pytest.fixture(autouse=True)
def reset():
    """Сбрасывать состояние модели перед каждым тестом."""
    model._participants.clear()
    model._assignments.clear()
    model._results.clear()
    model._next_id["participant"] = 1
    model._next_id["assignment"] = 1
    model._next_id["result"] = 1
    yield


class TestParticipant:
    """Тесты операций над Participant."""

    def test_create_returns_record(self):
        """create_participant возвращает словарь с uid и ip."""
        p = model.create_participant("1.2.3.4")
        assert p["uid"] == 1
        assert p["ip"] == "1.2.3.4"

    def test_create_increments_uid(self):
        """Каждый новый участник получает уникальный uid."""
        p1 = model.create_participant("1.1.1.1")
        p2 = model.create_participant("2.2.2.2")
        assert p2["uid"] == p1["uid"] + 1

    def test_create_empty_ip_raises(self):
        """Пустой ip вызывает ValueError."""
        with pytest.raises(ValueError):
            model.create_participant("")

    def test_get_all_returns_all(self):
        """get_all_participants возвращает всех участников."""
        model.create_participant("1.1.1.1")
        model.create_participant("2.2.2.2")
        assert len(model.get_all_participants()) == 2

    def test_delete_removes_record(self):
        """delete_participant удаляет запись."""
        p = model.create_participant("1.1.1.1")
        model.delete_participant(p["uid"])
        assert model.get_all_participants() == []

    def test_delete_unknown_raises(self):
        """Удаление несуществующего uid вызывает KeyError."""
        with pytest.raises(KeyError):
            model.delete_participant(999)


class TestAssignment:
    """Тесты операций над Assignment."""

    @pytest.fixture()
    def participant(self):
        """Создать участника для тестов."""
        return model.create_participant("10.0.0.1")

    def test_create_returns_record(self, participant):
        """create_assignment возвращает корректную запись."""
        a = model.create_assignment(
            participant=participant["uid"], tags="py"
        )
        assert a["participant"] == participant["uid"]
        assert a["tags"] == "py"

    def test_create_unknown_participant_raises(self):
        """Создание задания для несуществующего участника."""
        with pytest.raises(KeyError):
            model.create_assignment(participant=999, tags="x")

    def test_get_all_returns_all(self, participant):
        """get_all_assignments возвращает все задания."""
        model.create_assignment(participant=participant["uid"], tags="a")
        model.create_assignment(participant=participant["uid"], tags="b")
        assert len(model.get_all_assignments()) == 2

    def test_delete_removes_record(self, participant):
        """delete_assignment удаляет запись."""
        a = model.create_assignment(
            participant=participant["uid"], tags="x"
        )
        model.delete_assignment(a["uid"])
        assert model.get_all_assignments() == []

    def test_delete_unknown_raises(self):
        """Удаление несуществующего задания вызывает KeyError."""
        with pytest.raises(KeyError):
            model.delete_assignment(999)


class TestResult:
    """Тесты операций над Result."""

    @pytest.fixture()
    def assignment(self):
        """Создать участника и задание для тестов."""
        p = model.create_participant("10.0.0.2")
        return model.create_assignment(
            participant=p["uid"], tags="test"
        )

    def test_create_returns_record(self, assignment):
        """create_result возвращает корректную запись."""
        r = model.create_result(
            assignment=assignment["uid"],
            state="done",
            duration=42,
        )
        assert r["assignment"] == assignment["uid"]
        assert r["duration"] == 42

    def test_create_unknown_assignment_raises(self):
        """Создание результата для несуществующего задания."""
        with pytest.raises(KeyError):
            model.create_result(assignment=999)

    def test_get_all_returns_all(self, assignment):
        """get_all_results возвращает все результаты."""
        model.create_result(assignment=assignment["uid"], state="done")
        model.create_result(assignment=assignment["uid"], state="error")
        assert len(model.get_all_results()) == 2

    def test_delete_removes_record(self, assignment):
        """delete_result удаляет запись."""
        r = model.create_result(
            assignment=assignment["uid"], state="done"
        )
        model.delete_result(r["uid"])
        assert model.get_all_results() == []

    def test_delete_unknown_raises(self):
        """Удаление несуществующего результата вызывает KeyError."""
        with pytest.raises(KeyError):
            model.delete_result(999)


class TestQuery:
    """Тесты выборки query_recent_assignments."""

    def test_returns_recent_records(self):
        """Возвращает записи для участников, созданных недавно."""
        p = model.create_participant("5.5.5.5")
        a = model.create_assignment(
            participant=p["uid"], tags="ml"
        )
        model.create_result(
            assignment=a["uid"], state="done", duration=10
        )
        rows = model.query_recent_assignments()
        assert len(rows) == 1
        assert rows[0]["ip"] == "5.5.5.5"
        assert rows[0]["tags"] == "ml"
        assert rows[0]["duration"] == 10

    def test_excludes_old_records(self):
        """Не возвращает участников, созданных давно."""
        old_ts = model._now_ms() - 10 * 60 * 1000
        model.create_participant("9.9.9.9", created=old_ts)
        rows = model.query_recent_assignments()
        assert rows == []

    def test_empty_when_no_data(self):
        """Пустой результат при отсутствии данных."""
        assert model.query_recent_assignments() == []
