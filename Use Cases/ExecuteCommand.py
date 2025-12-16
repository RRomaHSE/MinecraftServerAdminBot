class ExecuteCommand:
    def __init__(self, rcon_client):
        self.rcon_client = rcon_client

    def execute(self, command):
        success, message = self.rcon_client.send_command(command)
        log_command(CommandResult(command, success, message))
        return CommandResult(command, success, message)