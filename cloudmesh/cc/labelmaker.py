import os
import re
from cloudmesh.common.variables import Variables
from datetime import datetime


class Labelmaker:

    def __init__(self, template):
        self.template = template\
            .replace("{os.", "{os_")\
            .replace("{cm.", "{cm_")\
            .replace("{now.", "{now_")
        self.variables = re.findall(r'{(.*?)}', self.template)



    def get(self, **data):
        """
        If now is followed by any of them its uste as strfmt
        Example: now.%m/%d/%Y, %H:%M:%S"

        :param data:
        :type data:
        :return:
        :rtype:
        """
        now = datetime.now()
        variables = Variables()
        replacements = {}

        for variable in self.variables:
            if variable.startswith("os_"):
                key = variable.split("os_", 1)[1]
                value = str(os.environ[key]).encode('unicode-escape').decode()
                replacements[variable] = value
            elif variable.startswith("cm_"):
                key = variable.split("cm_", 1)[1]
                if key in variables:
                    value = variables[key]
                replacements[variable] = value
            elif variable.startswith("now_"):
                value = variable.split("now_", 1)[1]
                self.template = self.template.replace(variable, "now")
                replacements["now"] = now.strftime(value)

        return self.template.format(**data, **replacements)
