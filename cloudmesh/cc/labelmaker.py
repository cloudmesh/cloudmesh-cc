import os
import re
from cloudmesh.common.variables import Variables
from cloudmesh.common.Shell import Console
from datetime import datetime
from cloudmesh.common.DateTime import DateTime
import time

class Labelmaker:

    def __init__(self, template, node=None, t0=None):
        self.cms_variables = Variables()
        self.t0 = t0
        self.template = template\
            .replace("{os.", "{os_")\
            .replace("{cm.", "{cm_")\
            .replace("{now.", "{now_")\
            .replace("{dt.", "{dt_")
        # .replace("{created.", "{created_") \
        # .replace("{modified.", "{modified_") \
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

        print("LABELMAKER", data)


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
            # elif variable.startswith("created_"):
            #     template = variable.split("created_", 1)[1]
            #     self.template = self.template.replace(template, "created")
            #     replacements["created"] = now.strftime(value)
            #     del data["created"]
            # elif variable.startswith("modified_"):
            #     template = variable.split("modified_", 1)[1]
            #     self.template = self.template.replace(template, "modified")
            #     replacements["modified"] = now.strftime(value)
            #     del data["modified"]
            #     print (data)
            #     print (replacements)
            #     print (variables)
            elif variable.startswith("dt_"):
                # template = variable.split("dt_", 1)[1]
                dummy, name, template = variable.split('_', 2)
                cms_t0_name = 'created_time_' + name
                if cms_t0_name not in self.cms_variables:
                    # Console.error(f'workflow {name} not found in cms set',
                    #               traceflag=True)
                    self.cms_variables.__setitem__(
                        cms_t0_name, datetime.strftime(t0, "%m/%d/%Y, %H:%M:%S"))
                else:
                    t0 = datetime.strptime(
                        self.cms_variables[cms_t0_name], "%m/%d/%Y, %H:%M:%S")
                dt = now - t0
                self.template = self.template.replace(variable, "dt")
                elapsed = time.strftime(template, time.gmtime(dt.seconds))
                replacements["dt"] = elapsed
        return self.template.format(**data, **replacements)
