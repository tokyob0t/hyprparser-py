from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union


@dataclass
class Setting:
    option: str
    value: Union["Gradient", "Color", str, int, float, bool]

    def format(self) -> str:
        name = self.option.split(":").pop(-1)

        if isinstance(self.value, bool):
            value = {
                True: "true",
                False: "false",
            }.get(self.value, "false")
        elif isinstance(self.value, (Gradient, Color)):
            value = self.value.format()
        else:
            value = self.value

        return "{} = {}".format(name, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.option,
            "value": getattr(self.value, "to_dict", lambda: self.value)(),
        }


@dataclass
class Exec:
    cmd: str
    exec_once: bool = False

    def format(self) -> str:
        if self.exec_once:
            return "exec-once = {}".format(self.cmd)
        return "exec = {}".format(self.cmd)

    def to_dict(self) -> Dict[str, Union[str, bool]]:
        return {"cmd": self.cmd, "exec-once": self.exec_once}


@dataclass
class Windowrule:
    rule: str
    window: str
    rule_args: str = ""

    def format(self) -> str:
        return "windowrule = {}, {}".format(
            " ".join([self.rule, str(self.rule_args)]), self.window
        )


@dataclass
class Bezier:
    name: str
    transition: Tuple[float, ...]  # It should be Tuple[float, float, float, float]

    def format(self) -> str:
        return "bezier = {}, {}".format(
            self.name, ", ".join(str(i) for i in self.transition)
        )

    def to_dict(self) -> dict:
        return {"name": self.name, "transition": self.transition}


@dataclass
class Color:
    r: str
    g: str
    b: str
    a: str

    @property
    def rgba(self) -> str:
        return "{}{}{}{}".format(self.r, self.g, self.b, self.a)

    def format(self) -> str:
        return "rgba({})".format(self.rgba)


@dataclass
class Gradient:
    angle: int
    colors: List[Color]

    def add_color(self, color: Color) -> None:
        return self.colors.append(color)

    def del_color(self, color: Color) -> None:
        return self.colors.remove(color)

    def format(self) -> str:
        return "{} {}deg".format(" ".join(map(Color.format, self.colors)), self.angle)

    def to_dict(self) -> Dict[str, Union[List[str], int]]:
        return {"colors": list(map(Color.format, self.colors)), "angle": self.angle}


@dataclass
class Variable:
    name: str = ""
    value: str = ""

    def format(self) -> str:
        return "${} = {}".format(self.name, self.value)

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "value": self.value,
        }


@dataclass
class Env:
    name: str
    value: List[str]

    def format(self) -> str:
        return "env = {}, {}".format(self.name, ":".join(self.value))

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        return {"name": self.name, "value": self.value}


@dataclass
class Monitor:
    name: str = ""
    resolution: str = "preferred"
    position: str = "auto"
    scale: str = "1"

    def format(self) -> str:
        return "monitor = {}".format(
            ",".join([self.name, self.resolution, self.position, self.scale])
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "resolution": self.resolution,
            "position": self.position,
            "scale": self.scale,
        }


@dataclass
class Binding:
    mods: List[str]
    key: str
    dispatcher: str
    params: List[str]
    bindtype: str = "e"

    def format(self) -> str:
        return "{} = {}".format(
            self.bindtype,
            ", ".join(
                [
                    " ".join(self.mods),
                    self.key,
                    self.dispatcher,
                    *self.params,
                ]
            ),
        )

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        return {
            "mods": self.mods,
            "key": self.key,
            "dispatcher": self.dispatcher,
            "params": self.params,
            "bindtype": self.bindtype,
        }


class TypeParser:
    @staticmethod
    def is_bool(value: str) -> bool:
        if value in ["on", "yes", "true", "off", "no", "false"]:
            return True
        return False

    @staticmethod
    def to_bool(value: str) -> bool:
        if value in ["on", "yes", "true"]:
            return True
        elif value in ["off", "no", "false"]:
            return False
        raise Exception("Invalid Data-type")

    #! TODO: Use regex to check if a str can be a int
    @staticmethod
    def is_int(value: str) -> bool:
        if value.startswith("-"):
            return TypeParser.is_int(value[1:])
        return value.isdecimal()

    @staticmethod
    def to_int(value: str) -> int:
        return int(value)

    #! TODO: Use regex to check if a str can be a float
    # https://www.geeksforgeeks.org/python-check-for-float-string/
    @staticmethod
    def is_float(value: str) -> bool:
        return TypeParser.is_int(value.replace(".", ""))

    @staticmethod
    def to_float(value: str) -> float:
        return float(value)

    @staticmethod
    def is_color(value: str) -> bool:
        if len(value.split()) != 1:
            return False

        if any(map(value.startswith, ["rgba", "rgb", "0x"])):
            return True

        return False

    @staticmethod
    def to_color(value: str) -> Color:
        for p in ["rgba(", "rgb", "0x"]:
            value = value.removeprefix(p)
        value = value.removesuffix(")")
        r = value[0:2]
        g = value[2:4]
        b = value[4:6]
        a = value[6:8]
        return Color(r, g, b, a)

    @staticmethod
    def is_gradient(value: str) -> bool:
        gradients = value.split()

        if not gradients:
            return False
        if gradients[-1].endswith("deg"):
            gradients = gradients[:-1]

        if all(map(TypeParser.is_color, gradients)):
            return True
        return False

    @staticmethod
    def to_gradient(value: str) -> Gradient:
        gradients = value.split()

        if gradients[-1].endswith("deg"):
            angle = TypeParser.to_int(gradients[-1].removesuffix("deg"))
        else:
            angle = 0

        gradients = gradients[:-1]
        return Gradient(angle, list(map(TypeParser.to_color, gradients)))
