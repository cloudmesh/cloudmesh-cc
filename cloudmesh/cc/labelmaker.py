"""Cloudmesh cc labelmaker."""
from pathlib import Path
import yaml
import os
import re
from cloudmesh.common.variables import Variables
from cloudmesh.common.Shell import Shell
from datetime import datetime
from cloudmesh.common.DateTime import DateTime
import time


class Labelmaker:
    """Class that creates labels for the jobs in the graph display."""
    def __init__(self,
                 template,
                 workflow_name: str,
                 job_name: str,
                 t0=None):
        self.cms_variables = Variables()
        self.t0 = t0
        self.template = template\
            .replace("{os.", "{os_")\
            .replace("{cm.", "{cm_")\
            .replace("{now.", "{now_")\
            .replace("{dt.", "{dt_")\
            .replace("{created.", "{created_")\
            .replace("{modified.", "{modified_")\
            .replace("{tstart.", "{tstart_")\
            .replace("{tend.", "{tend_")\
            .replace("{t0.", "{t0_")\
            .replace("{dt0.", "{dt0_")
        self.variables = re.findall(r'{(.*?)}', self.template)

        self.workflow_name = workflow_name
        self.job_name = job_name

        self.times_filename = Path(Shell.map_filename(
            f'~/.cloudmesh/workflow/{self.workflow_name}/runtime/{self.workflow_name}.dat'
        ).path).as_posix()

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

        #print("LABELMAKER", data)


        for variable in self.variables:
            if variable.startswith("os_"):
                key = variable.split("os_", 1)[1]
                value = str(os.environ[key]).encode('unicode-escape').decode()
                replacements[variable] = value
            elif variable.startswith("cm_"):
                key = variable.split("cm_", 1)[1]
                value = None
                if key in variables:
                    value = variables[key]
                replacements[variable] = value
            elif variable.startswith("now_"):
                value = variable.split("now_", 1)[1]
                self.template = self.template.replace(variable, "now")
                replacements["now"] = now.strftime(value)
            elif variable.startswith("created_"):
                template = variable.split("created_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'created_time_{self.job_name}' not in times_dict['times']:
                        raise ValueError
                    else:
                        replacements[variable] = times_dict['times'][f'created_time_{self.job_name}']

            elif variable.startswith("modified_"):
                template = variable.split("modified_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'modified_time_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        replacements[variable] = times_dict['times'][f'modified_time_{self.job_name}']

            elif variable.startswith("tstart_"):
                template = variable.split("tstart_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'tstart_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        replacements[variable] = times_dict['times'][f'tstart_{self.job_name}']

            elif variable.startswith("tend_"):
                template = variable.split("tend_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'tend_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        replacements[variable] = times_dict['times'][f'tend_{self.job_name}']

            elif variable.startswith("t0_"):
                template = variable.split("t0_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f't0_{self.workflow_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        replacements[variable] = times_dict['times'][f't0_{self.workflow_name}']

            elif variable.startswith("dt0_"):
                template = variable.split("dt0_", 1)[1]

                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f't0_{self.workflow_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        start_time = times_dict['times'][f't0_{self.workflow_name}']
                        t0 = datetime.strptime(
                                start_time, "%m/%d/%Y, %H:%M:%S")
                        dt = now - t0
                        elapsed = time.strftime("%H:%M:%S", time.gmtime(dt.seconds))
                        replacements[variable] = elapsed

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
