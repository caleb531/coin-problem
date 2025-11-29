#!/usr/bin/env python3

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from coinproblem import referee, timer


@pytest.fixture(autouse=True)
def isolate_referee_state():
    """Should isolate shared referee state between tests."""
    original_inputs = referee.inputs
    original_index = referee.next_input_index
    referee.inputs = []
    referee.next_input_index = 0
    try:
        yield
    finally:
        referee.inputs = original_inputs
        referee.next_input_index = original_index


@pytest.mark.parametrize(
    "counts, expected_total",
    [
        ({"pennies": 0, "nickels": 0, "dimes": 0, "quarters": 0}, 0),
        ({"pennies": 4, "nickels": 3, "dimes": 2, "quarters": 1}, 10),
        ({"pennies": 15, "nickels": 5, "dimes": 0, "quarters": 0}, 20),
    ],
)
def test_total_count(counts, expected_total):
    """Should sum all coin quantities."""
    assert referee.get_total_count(counts) == expected_total


@pytest.mark.parametrize(
    "counts, expected_amount",
    [
        ({"pennies": 0, "nickels": 0, "dimes": 0, "quarters": 0}, 0.00),
        ({"pennies": 4, "nickels": 3, "dimes": 2, "quarters": 1}, 0.64),
        ({"pennies": 1, "nickels": 2, "dimes": 3, "quarters": 4}, 1.41),
    ],
)
def test_total_amount(counts, expected_amount):
    """Should calculate the total dollar amount."""
    assert referee.get_total_amount(counts) == expected_amount


@patch("coinproblem.referee.random.randint")
def test_generate_new_input(mock_randint):
    """Should generate consistent count and amount pairs."""
    mock_randint.side_effect = [1, 2, 3, 4]

    generated = referee.generate_new_input(min_count=0, max_count=10)

    assert generated["count"] == 10
    assert generated["amount"] == 1.41
    assert mock_randint.call_count == 4


def test_next_input_caches():
    """Should cache generated input values for reuse."""
    expected = {"count": 6, "amount": 0.56}

    with patch(
        "coinproblem.referee.generate_new_input",
        return_value=expected,
    ) as mock_generate:
        first = referee.get_next_input(min_count=0, max_count=5)
        assert first is expected
        assert referee.inputs == [expected]
        assert referee.next_input_index == 1
        mock_generate.assert_called_once_with(0, 5)

    referee.next_input_index = 0

    with patch("coinproblem.referee.generate_new_input") as mock_generate_again:
        cached = referee.get_next_input(min_count=0, max_count=5)
        assert cached is expected
        assert mock_generate_again.call_count == 0


def test_next_input_cycle():
    """Should cycle cached inputs once the pointer resets."""
    cached_values = [
        {"count": 3, "amount": 0.03},
        {"count": 4, "amount": 0.55},
    ]
    referee.inputs = list(cached_values)

    first = referee.get_next_input(min_count=0, max_count=10)
    second = referee.get_next_input(min_count=0, max_count=10)
    referee.reset_inputs()
    repeated = referee.get_next_input(min_count=0, max_count=10)

    assert first == cached_values[0]
    assert second == cached_values[1]
    assert repeated == cached_values[0]


def test_print_next_input(capsys):
    """Should show a user-friendly preview of the next input."""
    player = SimpleNamespace(index=7)

    referee.print_next_input(player, count=1_234_567, amount=89.01)
    captured = capsys.readouterr()

    assert captured.out == "P7: count = 1,234,567, amount = $89.01 "


class DummyTimer:
    def __init__(self, seconds):
        """Should record the timeout duration."""
        self.seconds = seconds

    def __enter__(self):
        """Should allow use as a context manager without side effects."""
        return None

    def __exit__(self, exc_type, exc, tb):
        """Should avoid suppressing exceptions."""
        return False


class DummyPlayer:
    def __init__(self, path):
        """Should track player bookkeeping attributes."""
        self.path = path
        self.total_correct = 0
        self.total_incorrect = 0
        self.total_error = 0

    def get_success_rate(self):
        """Should return a neutral success rate for tests."""
        return 0.0


def test_run_duel(capsys):
    """Should run the duel with fresh inputs per player."""
    players = [DummyPlayer("player-one"), DummyPlayer("player-two")]

    with patch("coinproblem.referee.reset_inputs") as mock_reset:
        with patch("coinproblem.referee.run_rounds_for_player") as mock_run_rounds:
            with patch("coinproblem.referee.timer.Timer", DummyTimer):
                result = referee.run_duel(
                    players,
                    min_count=1,
                    max_count=5,
                    timeout=9,
                )

    output = capsys.readouterr().out

    assert result == players
    assert mock_reset.call_count == len(players)
    assert mock_run_rounds.call_args_list == [
        call(players[0], 1, 5),
        call(players[1], 1, 5),
    ]
    assert "P0: player-one" in output
    assert "P1: player-two" in output
    assert "min count per coin type: 1" in output
    assert "timeout per player: 9 s" in output


def build_fake_program(buffer_payloads, final_exception=None):
    """Should emulate a spawned child program for tests."""
    program = MagicMock()
    program.isalive.return_value = True
    program.buffer = ""

    def next_payload(*_):
        """Should feed preloaded payloads to the referee loop."""
        if buffer_payloads:
            program.buffer = buffer_payloads.pop(0)
            return None
        if final_exception is not None:
            raise final_exception
        return None

    program.expect_exact.side_effect = next_payload
    return program


class FakePlayer:
    def __init__(self, program):
        """Should wrap a mocked program with referee counters."""
        self._program = program
        self.total_correct = 0
        self.total_incorrect = 0
        self.total_error = 0
        self.index = 0

    def start_program(self):
        """Should attach the provided program to the player."""
        self.program = self._program


def test_run_rounds_records_correct():
    """Should record a correct response from the player."""
    expected_counts = {"pennies": 3, "nickels": 0, "dimes": 0, "quarters": 0}
    sample_input = {"count": 3, "amount": 0.03}
    program = build_fake_program(
        [json.dumps(expected_counts)],
        timer.TimeoutError("timer"),
    )
    player = FakePlayer(program)

    with patch(
        "coinproblem.referee.get_next_input",
        side_effect=[sample_input, sample_input],
    ):
        referee.run_rounds_for_player(player, min_count=0, max_count=1)

    assert player.total_correct == 1
    assert player.total_incorrect == 0
    assert player.total_error == 0
    assert player.program.sendline.call_args_list[0] == call("3,0.03")


def test_run_rounds_records_incorrect():
    """Should record an incorrect response from the player."""
    wrong_counts = {"pennies": 2, "nickels": 0, "dimes": 0, "quarters": 0}
    sample_input = {"count": 3, "amount": 0.03}
    program = build_fake_program(
        [json.dumps(wrong_counts)],
        timer.TimeoutError("timer"),
    )
    player = FakePlayer(program)

    with patch(
        "coinproblem.referee.get_next_input",
        side_effect=[sample_input, sample_input],
    ):
        referee.run_rounds_for_player(player, min_count=0, max_count=1)

    assert player.total_correct == 0
    assert player.total_incorrect == 1
    assert player.total_error == 0


def test_run_rounds_records_error():
    """Should record an error when the player emits invalid JSON."""
    program = build_fake_program(["not-json"], timer.TimeoutError("timer"))
    player = FakePlayer(program)

    with patch(
        "coinproblem.referee.get_next_input",
        side_effect=[
            {"count": 1, "amount": 0.01},
            {"count": 1, "amount": 0.01},
        ],
    ):
        referee.run_rounds_for_player(player, min_count=0, max_count=1)

    assert player.total_correct == 0
    assert player.total_incorrect == 0
    assert player.total_error == 1
