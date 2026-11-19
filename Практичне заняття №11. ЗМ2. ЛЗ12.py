from __future__ import annotations
from abc import ABC, abstractmethod


class ExpressionError(Exception):
    pass


class Telement(ABC):
    def __init__(self, left: Telement | None = None, right: Telement | None = None) -> None:
        self.left = left
        self.right = right

    @abstractmethod
    def result(self) -> float:
        pass

    @abstractmethod
    def copy(self) -> Telement:
        pass

    @abstractmethod
    def differ(self) -> Telement:
        pass

    def set_var(self, value: float) -> None:
        if self.left is not None:
            self.left.set_var(value)
        if self.right is not None:
            self.right.set_var(value)


class Real(Telement):
    def __init__(self, value: float) -> None:
        super().__init__(None, None)
        self.value = float(value)

    def result(self) -> float:
        return self.value

    def copy(self) -> Telement:
        return Real(self.value)

    def differ(self) -> Telement:
        return Real(0.0)


class Var(Telement):
    def __init__(self, value: float = 0.0) -> None:
        super().__init__(None, None)
        self.value = float(value)

    def result(self) -> float:
        return self.value

    def copy(self) -> Telement:
        return Var(self.value)

    def differ(self) -> Telement:
        return Real(1.0)

    def set_var(self, value: float) -> None:
        self.value = float(value)


class Plus(Telement):
    def __init__(self, left: Telement, right: Telement) -> None:
        super().__init__(left, right)

    def result(self) -> float:
        assert self.left is not None and self.right is not None
        return self.left.result() + self.right.result()

    def copy(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Plus(self.left.copy(), self.right.copy())

    def differ(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Plus(self.left.differ(), self.right.differ())


class Minus(Telement):
    def __init__(self, left: Telement, right: Telement) -> None:
        super().__init__(left, right)

    def result(self) -> float:
        assert self.left is not None and self.right is not None
        return self.left.result() - self.right.result()

    def copy(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Minus(self.left.copy(), self.right.copy())

    def differ(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Minus(self.left.differ(), self.right.differ())


class Mult(Telement):
    def __init__(self, left: Telement, right: Telement) -> None:
        super().__init__(left, right)

    def result(self) -> float:
        assert self.left is not None and self.right is not None
        return self.left.result() * self.right.result()

    def copy(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Mult(self.left.copy(), self.right.copy())

    def differ(self) -> Telement:
        # (u * v)' = u' * v + u * v'
        assert self.left is not None and self.right is not None
        return Plus(
            Mult(self.left.differ(), self.right.copy()),
            Mult(self.left.copy(), self.right.differ()),
        )


class Div(Telement):
    def __init__(self, left: Telement, right: Telement) -> None:
        super().__init__(left, right)

    def result(self) -> float:
        assert self.left is not None and self.right is not None
        divisor = self.right.result()
        if divisor == 0.0:
            raise ExpressionError("Ділення на нуль під час обчислення виразу.")
        return self.left.result() / divisor

    def copy(self) -> Telement:
        assert self.left is not None and self.right is not None
        return Div(self.left.copy(), self.right.copy())

    def differ(self) -> Telement:
        # (u / v)' = (u' * v - u * v') / (v * v)
        assert self.left is not None and self.right is not None
        numerator = Minus(
            Mult(self.left.differ(), self.right.copy()),
            Mult(self.left.copy(), self.right.differ()),
        )
        denominator = Mult(self.right.copy(), self.right.copy())
        return Div(numerator, denominator)


def pos_from_end(s: str, sub: str) -> int:

    idx = s.rfind(sub)
    return idx + 1 if idx != -1 else 0


def form(expr: str) -> Telement:

    if not isinstance(expr, str):
        raise ExpressionError("Вираз повинен бути рядком.")

    # Прибираємо зайві пробіли та підтримуємо десяткову кому й крапку
    s = expr.replace(" ", "").replace(",", ".")
    if not s:
        raise ExpressionError("Порожній математичний вираз.")

    length = len(s)


    for op, cls in (("+", Plus), ("-", Minus), ("*", Mult), ("/", Div)):
        p = pos_from_end(s, op)
        if p > 1:
            s1 = s[: p - 1]
            s2 = s[p:]
            if not s1 or not s2:
                raise ExpressionError(f"Неповні операнди навколо оператора '{op}' у виразі '{expr}'.")
            return cls(form(s1), form(s2))

    if s == "x":
        return Var()

    try:
        val = float(s)
    except ValueError as exc:
        raise ExpressionError(f"Некоректний елемент або невідомий символ у виразі: '{expr}'.") from exc

    if val != val or val in (float("inf"), float("-inf")):
        raise ExpressionError(f"Неприпустиме числове значення у виразі: '{expr}'.")

    return Real(val)


def read_expression(prompt: str) -> Telement:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Помилка: введено порожній рядок. Спробуйте ще раз.")
            continue
        try:
            return form(raw)
        except ExpressionError as err:
            print(f"Помилка у виразі: {err}")


def read_digits(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            digits = int(raw)
            if digits < 0 or digits > 15:
                print("Помилка: кількість знаків після коми має бути в межах від 0 до 15.")
                continue
            return digits
        except ValueError:
            print("Помилка: введіть ціле число для точності (наприклад, 4).")


def main() -> None:
    print("=== Інтерпретатор математичних виразів: Політ ракети ===")
    print("Допустимі операції: +, -, *, / | Числа та змінна: x\n")

    time_tree = read_expression("Введіть вираз для часу (наприклад, 5.88+1.25/0.13698*3): ")
    path_tree = read_expression("Введіть вираз для шляху s(x) (наприклад, 8.3*x*x*x-12/x/x+0.13): ")
    digits = read_digits("Введіть точність (кількість знаків після десяткової крапки, 0..15): ")

    try:
        t_val = time_tree.result()

        vel_tree = path_tree.differ()
        acc_tree = vel_tree.differ()

        for tree in (path_tree, vel_tree, acc_tree):
            tree.set_var(t_val)

        s_val = path_tree.result()
        v_val = vel_tree.result()
        a_val = acc_tree.result()

        fmt = f"{{:.{digits}f}}"
        print("\n--- Результати обчислень ---")
        print(f"Час:        {fmt.format(t_val)}")
        print(f"Шлях:       {fmt.format(s_val)}")
        print(f"Швидкість:  {fmt.format(v_val)}")
        print(f"Прискорення:{fmt.format(a_val)}")

    except ExpressionError as err:
        print(f"\nПомилка обчислення: {err}")
    except ZeroDivisionError:
        print("\nПомилка обчислення: ділення на нуль.")
    except OverflowError:
        print("\nПомилка обчислення: переповнення числового типу.")
    except Exception as err:
        print(f"\nНеочікувана помилка: {err}")


if __name__ == "__main__":
    main()