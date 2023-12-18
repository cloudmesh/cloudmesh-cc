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
        """Initialize the labelmaker.

        Args:
            template (str): The labelmaker tamplate string
            workflow_name (str): The workflow name
            job_name (str): The job name
            t0 (str): The time t0
        """
        self.colon = r'--'
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
            .replace("{dt0.", "{dt0_")\
            .replace("{t1.", "{t1_")\
            .replace("{dt1.", "{dt1_")
        self.variables = re.findall(r'{(.*?)}', self.template)

        self.workflow_name = workflow_name
        self.job_name = job_name

        self.times_filename = Path(Shell.map_filename(
            f'~/.cloudmesh/workflow/{self.workflow_name}/runtime/{self.workflow_name}.dat'
        ).path).as_posix()

    def set_colon(self, value):
        """Set the quote character as colon. Single colon is not allowed.
        The quote character is being replaced with a single colon.
        Warning: setting the colon has not been fully implemented.
        The reason why this is the case is because we cannot use anything
        other than --

        Args:
            value (str): the value of the colon

        Returns:
            None: nothing
        """
        self.colon = value

    def get(self, **data):
        """If now is followed by any of them its uste as strfmt.

        Example: now.%m/%d/%Y, %H:%M:%S

        Args:
            **data

        Returns:

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
                template = variable.split("now_", 1)[1]
                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                # self.template = self.template.replace(variable, "now")
                replacements[variable] = now.strftime(template)
            elif variable.startswith("created_"):
                template = variable.split("created_", 1)[1]
                base = variable.split("created_", 1)[0]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'created_time_{self.job_name}' not in times_dict['times']:
                        raise ValueError
                    else:
                        created_date_time = datetime.strptime(times_dict['times'][f'created_time_{self.job_name}'], r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = created_date_time.strftime(template)

            elif variable.startswith("modified_"):
                template = variable.split("modified_", 1)[1]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'modified_time_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        modified_date_time = datetime.strptime(times_dict['times'][f'modified_time_{self.job_name}'], r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = modified_date_time.strftime(template)

            elif variable.startswith("tstart_"):
                # the time a job started.
                template = variable.split("tstart_", 1)[1]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'tstart_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        tstart_date_time = datetime.strptime(
                            times_dict['times'][
                                f'tstart_{self.job_name}'],
                            r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = tstart_date_time.strftime(
                            template)

            elif variable.startswith("tend_"):
                # the time a job ended.
                template = variable.split("tend_", 1)[1]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'tend_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        tend_date_time = datetime.strptime(
                            times_dict['times'][
                                f'tend_{self.job_name}'],
                            r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = tend_date_time.strftime(
                            template)

            elif variable.startswith("t0_"):
                # the time a workflow started.
                template = variable.split("t0_", 1)[1]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f't0_{self.workflow_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        t0_date_time = datetime.strptime(
                            times_dict['times'][
                                f't0_{self.workflow_name}'],
                            r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = t0_date_time.strftime(
                            template)

            elif variable.startswith("t1_"):
                # the time a workflow ended.
                template = variable.split("t1_", 1)[1]

                if template == "":
                    template = r"%m/%d/%Y, %H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f't1_{self.workflow_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        t1_date_time = datetime.strptime(
                            times_dict['times'][
                                f't1_{self.workflow_name}'],
                            r"%m/%d/%Y, %H:%M:%S")
                        replacements[variable] = t1_date_time.strftime(
                            template)

            elif variable.startswith("dt0_"):
                # time since beginning of workflow
                template = variable.split("dt0_", 1)[1]

                if template == "":
                    template = r"%H:%M:%S"
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
                        elapsed = time.gmtime(dt.seconds)
                        replacements[variable] = time.strftime(template,
                                                               elapsed)

            elif variable.startswith("dt1_"):
                # difference of time from beginning to end of workflow
                template = variable.split("dt1_", 1)[1]

                if template == "":
                    template = r"%H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f't0_{self.workflow_name}' not in times_dict['times'] or f't1_{self.workflow_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        start_time = times_dict['times'][f't0_{self.workflow_name}']
                        end_time = times_dict['times'][f't1_{self.workflow_name}']
                        start = datetime.strptime(
                                start_time, "%m/%d/%Y, %H:%M:%S")
                        end = datetime.strptime(
                                end_time, "%m/%d/%Y, %H:%M:%S")
                        delta = end - start
                        elapsed = time.gmtime(delta.seconds)
                        replacements[variable] = time.strftime(template,
                                                               elapsed)


            elif variable.startswith("dt_"):
                # the total time of a job.
                template = variable.split("dt_", 1)[1]

                if template == "":
                    template = r"%H:%M:%S"
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    raise ValueError
                if 'times' in times_dict:
                    if f'tstart_{self.job_name}' not in times_dict['times'] or f'tend_{self.job_name}' not in times_dict['times']:
                        replacements[variable] = r'N/A'
                    else:
                        start_time = times_dict['times'][f'tstart_{self.job_name}']
                        end_time = times_dict['times'][f'tend_{self.job_name}']
                        start = datetime.strptime(
                                start_time, "%m/%d/%Y, %H:%M:%S")
                        end = datetime.strptime(
                                end_time, "%m/%d/%Y, %H:%M:%S")
                        delta = end - start
                        elapsed = time.gmtime(delta.seconds)
                        replacements[variable] = time.strftime(template,
                                                               elapsed)
        result = self.template.format(**data, **replacements).replace(self.colon, r':')
        return result
        # return self.template.format(**data, **replacements)
