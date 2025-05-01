# MIT License
# Copyright (c) 2024 Gai Ichisawa

import os, logging, json, requests, discord, queue, asyncio
from typing import Callable, Any
from discord.ext import tasks, commands
from discord import app_commands
from models import Models

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger

    async def cog_load(self):
        raise NotImplementedError()

    def on_close(self):
        raise NotImplementedError()

class TTSCog(MyCog):
    def __init__(self, bot: commands.Bot, logger : logging.Logger):
        super().__init__(bot, logger.getChild('ttscog'))
        self.text_channels = {}
        self.voice_clients = {}
        self.voice_channels = {}
        self.prefs = {}
        self.queue = queue.Queue()
        self.is_reading = False

    async def cog_load(self):
        logger = self.logger.getChild('on_ready')
        if os.path.isfile('prefs.json'):
            with open('prefs.json', 'r') as f:
                self.prefs = json.load(f)
            logger.info('Loaded preferences')
        self.loop.start()
        logger.info('Initialized TTSCog')

    def on_close(self):
        logger = self.logger.getChild('on_close')
        with open('prefs.json', 'w') as f:
            f.write(json.dumps(self.prefs))
        logger.info('Saved preferences')
        self.loop.cancel()
        logger.info('TTSCog Closed')

    def get_pref(self, user_id: int, key: str, def_val: ..., cond: Callable[..., bool]):
        user_id_str = str(user_id)
        if user_id_str in self.prefs:
            if key in self.prefs[user_id_str]:
                value = self.prefs[user_id_str][key]
                if cond(value):
                    return value
            self.prefs[user_id_str][key] = def_val
        return def_val

    def get_style(self, user_id: int):
        return self.get_pref(
            user_id=user_id,
            key='style',
            def_val=[Models.つくよみちゃん_れいせい.value],
            cond=lambda style:(
                (type(style) == list and len(style) == 1 and style[0] in Models.get_values()) or
                (type(style) == list and len(style) == 3 and style[0] in Models.get_values() and style[1] in Models.get_values() and style[2] == float and 0.0 <= style[2] <= 1.0)
            )
        )

    def get_speed(self, user_id: int):
        return self.get_pref(
            user_id=user_id,
            key='speed',
            def_val=1.0,
            cond=lambda speed: 0.5 <= speed <= 2.0
        )

    def get_pitch(self, user_id: int):
        return self.get_pref(
            user_id=user_id,
            key='pitch',
            def_val=0.0,
            cond=lambda pitch: -10.0 <= pitch <= 10.0
        )

    def get_intonation(self, user_id: int):
        return self.get_pref(
            user_id=user_id,
            key='intonation',
            def_val=1.0,
            cond=lambda intonation: 0.0 <= intonation <= 10.0
        )

    def get_volume(self, user_id: int):
        return self.get_pref(
            user_id=user_id,
            key='volume',
            def_val=1.0,
            cond=lambda volume: 0.5 <= volume <= 2.0
        )

    @app_commands.command(name='join', description='ボイスチャンネルに参加します。')
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                vc = await channel.connect()
                self.text_channels[interaction.guild.id] = interaction.channel
                self.voice_clients[interaction.guild.id] = vc
                self.voice_channels[interaction.guild.id] = channel
                await interaction.response.send_message(f'{channel.name}に参加しました。')
            else:
                await interaction.response.send_message('既にボイスチャンネルに参加しています。')

    @app_commands.command(name='leave', description='ボイスチャンネルから切断します。')
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.id in self.voice_clients:
            vc = self.voice_clients[interaction.guild.id]
            await vc.disconnect()
            del self.text_channels[interaction.guild.id]
            del self.voice_clients[interaction.guild.id]
            del self.voice_channels[interaction.guild.id]
            await interaction.response.send_message('ボイスチャンネルから切断されました。')

    async def set_pref(self, interaction: discord.Interaction, key: str, value: ..., message: str):
        user_id_str = str(interaction.user.id)
        if user_id_str not in self.prefs or type(self.prefs[user_id_str]) != dict:
            self.prefs[user_id_str] = {}
        self.prefs[user_id_str][key] = value
        await interaction.response.send_message(message)

    @app_commands.command(name='set', description='モデルを設定します。')
    @app_commands.describe(model='モデル')
    async def set(self, interaction: discord.Interaction, model: Models):
        await self.set_pref(interaction, 'style', [model.value], f'モデルを"{model.name}"に設定しました。')

    @app_commands.command(name='speed', description='話速を設定します。')
    @app_commands.describe(speed='話速')
    async def speed(self, interaction: discord.Interaction, speed: app_commands.Range[float, 0.5, 2.0]):
        await self.set_pref(interaction, 'speed', speed, f'話速を{speed}に設定しました。')

    @app_commands.command(name='pitch', description='ピッチを設定します。')
    @app_commands.describe(pitch='ピッチ')
    async def pitch(self, interaction: discord.Interaction, pitch: app_commands.Range[float, -10.0, 10.0]):
        await self.set_pref(interaction, 'pitch', pitch, f'ピッチを{pitch}に設定しました。')

    @app_commands.command(name='intonation', description='抑揚を設定します。')
    @app_commands.describe(intonation='抑揚')
    async def intonation(self, interaction: discord.Interaction, intonation: app_commands.Range[float, 0.0, 10.0]):
        await self.set_pref(interaction, 'intonation', intonation, f'抑揚を{intonation}に設定しました。')

    @app_commands.command(name='volume', description="ボリュームを設定します。")
    @app_commands.describe(volume='ボリューム')
    async def volume(self, interaction: discord.Interaction, volume: app_commands.Range[float, 0.5, 2.0]):
        await self.set_pref(interaction, 'volume', volume, f'ボリュームを{volume}に設定しました。')

    @app_commands.command(name='morph', description='２つのモデルを合成します。')
    @app_commands.describe(base_model='ベースモデル')
    @app_commands.describe(target_model='ターゲットモデル')
    @app_commands.describe(morph_rate='合成の割合')
    async def morph(self, interaction: discord.Interaction, base_model: Models, target_model: Models, morph_rate: app_commands.Range[float, 0.0, 1.0]):
        await self.set_pref(interaction, 'style', [base_model.value, target_model.value, morph_rate],
            f'ベースモデルを"{base_model.name}"に、ターゲットモデルを"{target_model.name}"に、合成の割合を{morph_rate}に設定しました。')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild and message.guild.id in self.voice_clients and message.content:
            if self.text_channels[message.guild.id] != message.channel:
                return

            self.queue.put(message)

            await self.bot.process_commands(message)

    @tasks.loop(seconds=1)
    async def loop(self):
        if self.queue.empty() or self.is_reading: return

        lock = asyncio.Lock()

        try:
            async with lock:
                is_reading = True

                message = self.queue.get()

                vc = self.voice_clients[message.guild.id]
                style = self.get_style(message.author.id)

                if len(message.content) > 40:
                    text = message.content[0:40] + "以下略"
                else:
                    text = message.content

                response = requests.post(
                    url='http://localhost:50031/audio_query',
                    params={
                        'text': text,
                        'speaker': style[0],
                    }
                )
                query = response.json()
                query['speedScale'] = self.get_speed(message.author.id)
                query['pitchScale'] = self.get_pitch(message.author.id)
                query['intonationScale'] = self.get_intonation(message.author.id)
                query['volumeScale'] = self.get_volume(message.author.id)
                query['prePhonemeLength'] = 0.0
                query['postPhonemeLength'] = 0.0
                query['pauseLength'] = None
                query['pauseLengthScale'] = 1.0
                query['outputSamplingRate'] = 44100
                query['outputStereo'] = False

                if len(style) == 1:
                    response = requests.post(
                        url='http://localhost:50031/synthesis',
                        params={
                            'speaker': style[0]
                        },
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(query),
                    )
                elif len(style) == 3:
                    response = requests.post(
                        url='http://localhost:50031/synthesis_morphing',
                        params={
                            'base_speaker': style[0],
                            'target_speaker': style[1],
                            'morph_rate': style[2]
                        },
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(query)
                    )

                temp_file = f'temp_{message.id}.wav'

                with open(temp_file, 'wb') as f:
                    f.write(response.content)

                vc.play(
                    discord.FFmpegPCMAudio(
                        temp_file,
                        before_options='-channel_layout mono'
                    ),
                    application='lowdelay',
                    bitrate=128,
                    fec=True,
                    bandwidth='full',
                    signal_type='voice',
                    after=lambda e: os.remove(temp_file)
                )

                is_reading = False
        except Exception as err:
            self.logger.error(msg="Unhandled exception has occurred", exc_info=err)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None and after.channel is None and len(before.channel.members) == 1 and before.channel in self.voice_channels.values():
            vc = self.voice_clients[before.channel.guild.id]
            await vc.disconnect()
            await self.text_channels[before.channel.guild.id].send('メンバーがいないためボイスチャンネルから切断されました。')
            del self.text_channels[before.channel.guild.id]
            del self.voice_clients[before.channel.guild.id]
            del self.voice_channels[before.channel.guild.id]
