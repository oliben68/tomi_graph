from abc import ABCMeta, abstractmethod

from hopla.documents.schema_based.document import ValidatedDocument


def model_document(class_name, model_class, **dct):
    return type(class_name, (ValidatedDocument, ), dct)


class ModelDocument(metaclass=ABCMeta):
    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def read(self):
        pass


# class MetaDockerMachine(type):
#     def __new__(mcs, class_name, bases, dct):
#         docker_machine_class = super(MetaDockerMachine, mcs).__new__(mcs, class_name, bases, dct)
#
#         def add_method(new_cmd):
#             built_command = "{docker_machine_bin} {cmd}".format(docker_machine_bin=DOCKER_MACHINE_BIN, cmd=new_cmd)
#
#             def added_method(_, *args, **kwargs):
#                 try:
#                     cmd_args = ' '.join(args)
#                     cmd_options = ' '.join(
#                         ["--" + key.replace("_", "-") + " " + (
#                             str(value) + " " if str(type(value).__name__) not in ['NoneType', 'bool'] else "") for
#                          key, value in
#                          kwargs.items()])
#                     string_command = "{built_command} {args} {options}".format(built_command=built_command,
#                                                                                args=cmd_args,
#                                                                                options=cmd_options).strip()
#
#                     stdout, stderr = Popen(shlex.split(string_command), stdout=PIPE, stderr=PIPE).communicate()
#                     if stderr is not None and len(stderr) > 0:
#                         str_stderr = stderr.decode('UTF-8').strip()
#                         if str_stderr.lower().startswith("warning"):
#                             return str_stderr
#                         return "[ERROR]: {msg}".format(msg=str_stderr)
#                     if type(COMMANDS[new_cmd]) == dict and "cols" in COMMANDS[new_cmd].keys() and \
#                             COMMANDS[new_cmd]["cols"]:
#                         output = []
#                         for idx, line in enumerate(stdout.decode('UTF-8').strip().split("\n")):
#                             if idx == 0:
#                                 cols = line.split()
#                                 continue
#                             dict_line = {}
#                             for indx, val in enumerate(re.split(r'\s{2,}', line)):
#                                 dict_line[cols[indx]] = val
#                             output.append(dict_line)
#                         return output
#                     else:
#                         return stdout.decode('UTF-8').strip()
#                 except Exception as ex:
#                     raise DockerException(ex)
#
#             return added_method
#
#         setattr(docker_machine_class, "commands_info", COMMANDS)
#         for cmd, info in COMMANDS.items():
#             setattr(docker_machine_class, cmd, add_method(cmd))
#
#         return docker_machine_class