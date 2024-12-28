import sys, logging, coloredlogs, discord
from discord.ext import commands
from cog import MyCog, TTSCog

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.logger = logging.getLogger('bot')
        std_handler = logging.StreamHandler(stream=sys.stdout)
        std_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(std_handler)
        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {
            'asctime': {'color': 'black', 'bright': True},
            'hostname': {'color': 'magenta'},
            'levelname': {'color': 'blue', 'bright': True},
            'name': {'color': 'blue'},
            'programname': {'color': 'cyan'}
        }
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'critical': {'color': 'red', 'bold': True},
            'error': {'color': 'red'},
            'warning': {'color': 'yellow'},
            'notice': {'color': 'magenta'},
            'info': {},
            'debug': {'color': 'green'},
            'spam': {'color': 'green', 'faint': True},
            'success': {'color': 'green', 'bold': True},
            'verbose': {'color': 'blue'}
        }
        coloredlogs.install(
            level='DEBUG',
            logger=self.logger,
            fmt='%(asctime)s %(levelname)-8s %(name)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def on_ready(self):
        logger = self.logger.getChild('on_ready')
        await self.add_cog(TTSCog(self, self.logger))
        await self.tree.sync()
        logger.info('Synced command tree to the guild')
        logger.info('Keep in mind that synchronization of commands can take a few minutes')
        activity = discord.Activity(type=discord.ActivityType.playing, name='稼働中')
        await self.change_presence(status=discord.Status.online, activity=activity)
        logger.info('Logged in')

    async def close(self):
        logger = self.logger.getChild('on_close')
        for cog_name in self.cogs:
            cog = self.get_cog(cog_name)
            if isinstance(cog, MyCog):
                cog.on_close()
        await super().close()
        logger.info('Closed')