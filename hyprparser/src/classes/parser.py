import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from .linetype import LineType, LineTypeList
from .structures import (Bezier, Binding, Color, Env, Exec, Gradient, Monitor,
                         Setting, TypeParser, Variable)

last_section = []
last_file = ""

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: str) -> None:
        self.path = path
        self.monitors: List[Monitor] = []
        self.binds: List[Binding] = []
        self.variables: List[Variable] = []
        self.config: Dict[str, Setting] = {}
        self.beziers: Dict[str, Bezier] = {}
        self.env: Dict[str, Env] = {}
        self.exec: List[Exec] = []
        self.files: List[File] = [File(path, Helper.read_file(path))]
        self.insta_save: bool = False
        self.override_options:bool = False


    def reload(self) -> None:
        return Helper.read_lines(Helper.read_file(self.path))

    def save_all(self) -> None:
        for file in self.files:
            file.save()

    def new_option(
        self,
        new_option: Setting,
    ) -> None:
        sections = new_option.option.split(":")[:-1]
        line_n, file = Helper.get_line_option(sections)

        if not file:
            Helper.new_sections(sections)
            return HyprData.new_option(new_option)

        indent = "    " * new_option.option.count(":")
        file.content.insert(line_n + 1, indent + new_option.format())

        if self.insta_save:
            return file.save()

    def get_option(self, option: str) -> Union[Setting, None]:
        return self.config.get(option)

    def set_option(
        self, option: str, value: Union[Gradient, Color, Color, str, int, float, bool]
    ) -> None:
        obj_option = self.config.get(option)

        if not obj_option:
            return

        obj_option.value = value
        new_line = obj_option.format()
        line_n, file = Helper.get_line_option(option)

        if not file:
            file = HyprData.files[0]
            line_n = len(file.content) - 1

        indent = "    " * obj_option.option.count(":")
        file.content[line_n] = indent + new_line

        if HyprData.insta_save:
            return file.save()

    def new_env(self, env: Env) -> None:
        line_n, file = Helper.get_line_option("env")

        if not file:
            file = HyprData.files[0]
            line_n = -1

        if line_n == -1:
            file.content.append(env.format())
        else:
            file.content.insert(line_n, env.format())

        HyprData.env[env.name] = env
        if HyprData.insta_save:
            return file.save()

    def get_env(self, env_name: str) -> Union[Env, None]:
        return self.env.get(env_name)


    def set_env(self, env_name: str, value: List[str]) -> None:
        obj_env = HyprData.env.get(env_name)
        if not obj_env:
            return

        obj_env.value = value
        line_n, file = Helper.get_line_env(env_name)

        if not file:
            file = HyprData.files[0]
            line_n = len(file.content)

        file.content[line_n] = obj_env.format()
        if HyprData.insta_save:
            return file.save()

    def new_bezier(self, bezier:Bezier) -> None:
        line_n, file = Helper.get_line_option("animations:bezier")
        if not file:
            file = HyprData.files[0]
            line_n = -1

        if line_n == -1:

            file.content.insert(line_n, bezier.format())


    def get_bezier(self, bezier_name:str) -> Union[Bezier, None]:
        return self.beziers.get(bezier_name)

    def set_bezier(self, bezier_name: str, value: Tuple[float, float, float, float]) -> None:
        obj_bezier= HyprData.beziers.get(bezier_name)
        if not obj_bezier:
            return

        obj_bezier.transition = value
        line_n, file = Helper.get_line_bezier(obj_bezier.name)

        if not file:
            file = HyprData.files[0]
            line_n = len(file.content)

        file.content[line_n] = obj_bezier.format()
        if HyprData.insta_save:
            return file.save()


    def new_bind(self, bind: Binding) -> None:
        line_n, file = Helper.get_line_option("bind")

        if not file:
            file = HyprData.files[0]
            line_n = -1

        if line_n == -1:
            file.content.append(bind.format())
        else:
            file.content.insert(line_n, bind.format())

        if HyprData.insta_save:
            return file.save()


@dataclass
class File:
    path: str
    content: List[str]

    def save(self) -> None:
        return Helper.save_file(self.path, self.content)


class Helper:
    @staticmethod
    def read_file(path: str) -> List[str]:
        global last_file
        last_file = os.path.expandvars(path)
        with open(last_file) as file:
            return file.read().splitlines()

    @staticmethod
    def save_file(path: str, content: List[str]) -> None:
        with open(os.path.expandvars(path), "w+") as file:
            return file.writelines(map(lambda v: v + "\n", content))

    @staticmethod
    def new_sections(sections: List[str]) -> None:
        if not sections:
            return

        depth = []

        for i, section in enumerate(sections, 0):
            depth += [section]
            _, file = Helper.get_line_option(depth)

            if not file:
                line_n, file = Helper.get_line_option(depth[:-1])

                if not file:
                    continue
                indent = "    " * i
                file.content.insert(line_n + 1, indent + section + " {")
                file.content.insert(line_n + 2, indent + "}")
                if i + 1 == len(sections):
                    return file.save()

    @staticmethod
    def read_lines(lines: List[str]):
        for line in lines:
            if LineParser.skip(line):
                continue

            line = LineParser.format_line(line)

            match LineParser.get_linetype(line):
                case "start-section":
                    LineParser.add_section(line)
                case "end-section":
                    LineParser.del_section(line)
                case "setting":
                    DataParser.parse_setting(line)
                case "bind":
                    DataParser.parse_bind(line)
                case "variable":
                    DataParser.parse_variable(line)
                case "source":
                    DataParser.parse_source(line)
                case "monitor":
                    DataParser.parse_monitor(line)
                case "bezier":
                    DataParser.parse_bezier(line)
                case "env":
                    DataParser.parse_env(line)
                case "exec":
                    DataParser.parse_exec(line)
                case "windowrule":
                    pass
                case "windowrulev2":
                    pass
                case "layerrule":
                    pass
                case _:
                    print(line)

    @staticmethod
    def get_line_option(option: Union[str, List[str]]) -> Tuple[int, Union[File, None]]:
        if isinstance(option, str):
            section_depth = option.split(":")
        else:
            section_depth = option

        for file in HyprData.files:
            depth = []
            for i, line in enumerate(file.content):
                if LineParser.skip(line):
                    continue

                line = LineParser.format_line(line)

                match LineParser.get_linetype(line):
                    case "start-section":
                        section_name, _ = map(str.strip, line.split("{"))
                        depth += [section_name]
                        if depth == section_depth:
                            return i, file

                    case "end-section":
                        depth.pop(-line.count("}"))
                    case _:
                        section_name, _ = line.split(" = ")
                        depth += [section_name]
                        if depth == section_depth:
                            return i, file
                        depth.pop(-1)

        return (-1, None)

    @staticmethod
    def get_line_env(env_name: str) -> Tuple[int, Union[File, None]]:
        for file in HyprData.files:
            for i, line in enumerate(file.content):
                if LineParser.skip(line):
                    continue

                line = LineParser.format_line(line)
                match LineParser.get_linetype(line):
                    case "env":
                        _, env = line.split(" = ")
                        name, *_ = env.split(",")
                        if env_name == name:
                            return i, file
        return (-1, None)
    @staticmethod
    def get_line_bezier(bezier_name:str) -> Tuple[int, Union[File, None]]:
        for file in HyprData.files:
            for i, line in enumerate(file.content):
                if LineParser.skip(line):
                    continue
                line = LineParser.format_line(line)

                match LineParser.get_linetype(line):
                    case "bezier":
                        _, bezier = line.split(" = ")
                        name, *_ = bezier.split(",")
                        if bezier_name == name.strip():
                            return i, file
        return (-1, None)

class LineParser:
    @staticmethod
    def add_section(line: str) -> None:
        global last_section
        section_name, _ = map(str.strip, line.split("{"))
        last_section += [section_name]

    @staticmethod
    def del_section(line: str) -> None:
        global last_section
        last_section.pop(-line.count("}"))

    @staticmethod
    def format_line(line: str) -> str:
        line = line.split("#", 1)[0].strip()

        try:
            name, value = line.split("=", 1)
            return "{} = {}".format(name.strip(), value.strip())
        except ValueError:
            if line:
                return line
        except Exception as e:
            print(e)
        return ""

    @staticmethod
    def get_linetype(line: str) -> LineType:
        line = LineParser.format_line(line)
        if "{" in line:
            return "start-section"
        elif "}" in line:
            return "end-section"
        elif line.startswith("$"):
            return "variable"
        else:
            for linetype in LineTypeList:
                if line.startswith(linetype):
                    return linetype
            return "setting"

    @staticmethod
    def skip(line: str) -> bool:
        tmp = LineParser.format_line(line)
        if tmp.startswith("#") or not tmp:
            return True
        return False


class DataParser:
    @staticmethod
    def parse_monitor(line: str) -> None:
        _, monitor = line.split(" = ")
        name, res, pos, scale = map(str.strip, monitor.split(","))

        return HyprData.monitors.append(Monitor(name, res, pos, scale))

    @staticmethod
    def parse_variable(line: str) -> None:
        return HyprData.variables.append(Variable(*line[1:].split(" = ")))

    @staticmethod
    def parse_setting(line: str) -> None:
        name, value = line.split(" = ")
        section = ":".join(last_section) + ":" + name  # section:subsection:name

        if TypeParser.is_bool(value):
            value = TypeParser.to_bool(value)
        elif TypeParser.is_int(value):
            value = TypeParser.to_int(value)
        elif TypeParser.is_float(value):
            value = TypeParser.to_float(value)
        elif TypeParser.is_color(value):
            value = TypeParser.to_color(value)
        elif TypeParser.is_gradient(value):
            value = TypeParser.to_gradient(value)

        HyprData.config[section] = Setting(section, value)

    @staticmethod
    def parse_exec(line: str) -> None:
        exectype, cmd = line.split(" = ")

        if exectype == "exec-once":
            return HyprData.exec.append(Exec(cmd, True))
        return HyprData.exec.append(Exec(cmd))

    @staticmethod
    def parse_bezier(line: str) -> None:
        _, bezier = line.split(" = ")
        name, *curve = map(str.strip, bezier.split(",", 4))
        curve = tuple(map(float, curve))
        HyprData.beziers[name] = Bezier(name, curve)  # type: ignore

    @staticmethod
    def parse_bind(line: str) -> None:
        bindtype, keys = line.split(" = ")
        mods, key, dispatcher, *params = map(str.strip, keys.split(",", 4))
        mods = mods.split() if mods else []
        return HyprData.binds.append(Binding(mods, key, dispatcher, params, bindtype))

    @staticmethod
    def parse_source(line: str) -> None:
        _, path = line.split(" = ")
        path = os.path.expanduser(path)
        content = Helper.read_file(path)

        HyprData.files.append(File(path, content))
        return Helper.read_lines(content)

    @staticmethod
    def parse_env(line: str) -> None:
        _, env = line.split(" = ")
        var_env, *value = map(str.strip, env.split(",", 1))

        HyprData.env[var_env] = Env(var_env, value)

HyprData: Config = Config("$HOME/.config/hypr/hyprland.conf")
HyprData.reload()
