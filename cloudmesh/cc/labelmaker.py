import os
import re
from cloudmesh.common.variables import Variables
from datetime import datetime
from cloudmesh.common.DateTime import DateTime
import time

class Labelmaker:

    def __init__(self, template, t0=None):
        self.t0 = t0
        self.template = template\
            .replace("{os.", "{os_")\
            .replace("{cm.", "{cm_")\
            .replace("{now.", "{now_") \
            .replace("{dt.", "{dt_")
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
        t0 = self.t0 or now
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
            elif variable.startswith("dt_"):
                dummy, name, template = variable.split("_", 2)
                dt = now - t0
                self.template = self.template.replace(template, "dt")
                replacements["dt"] = dt.strftime(value)
        return self.template.format(**data, **replacements)
