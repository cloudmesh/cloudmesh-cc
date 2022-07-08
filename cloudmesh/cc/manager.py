class WorkflowManager:

    def __init__(self):
        pass
    
# cc workflow add [--name=NAME] [--job=JOB] ARGS...
# cc workflow delete [--name=NAME] --job=JOB
# cc workflow list [--name=NAME] [--job=JOB]
# cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
# cc workflow [--name=NAME] --dependencies=DEPENDENCIES
# cc workflow status --name=NAME [--output=OUTPUT]
# cc workflow graph --name=NAME
# cc workflow service add [--name=NAME] FILENAME
# cc workflow service list [--name=NAME] [--job=JOB]
# cc workflow service job add [--name=NAME] --job=JOB ARGS...
# cc workflow service job delete NAME
# cc workflow service job list NAME
# cc workflow service run --name=NAME