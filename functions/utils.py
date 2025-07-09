

import platform
from datetime import datetime as dt

from pyrogram import __version__ as _p_v
from telethon import Button
from telethon import __version__ as _t_v
from telethon import events

from core.bot import Bot, Var, asyncio
from database import DataBase
from functions.tools import Tools

ABOUT = """
**⏱ Uptime** : `{}`
**💡 Version** : `{}`
**👥 Users** : `{}`
**🗃️ Documents** : `{}`

• **🐍 Python**: `{}`
• **✈️ Telethon**: `{}`
• **🏔️ Pyrogram**: `{}`
• **💻 Server**: `{}`
• **📖 Source Code** : {}

~ **Developer**  __@Kaif_00z __
"""


class AdminUtils:
    def __init__(self, dB: DataBase, bot: Bot):
        self.db = dB
        self.bot = bot
        self.tools = Tools()
        self.python_version = platform.python_version()
        self.system = f"{platform.system()}-{platform.release()}"
        self.telethon_version = _t_v
        self.pyrogram_version = _p_v
        self.started_at = dt.now()

    def admin_panel(self):
        btn = [
            [
                Button.inline("📜 LOGS", data="slog"),
                Button.inline("♻️ Restart", data="sret"),
            ],
            [
                Button.inline("🎞️ Encode [Toogle]", data="entg"),
                Button.inline("📸 SS [Toggle]", data="sstg"),
            ],
            [Button.inline("🔘 Button Upload [Toogle]", data="butg")],
            [Button.inline("🗃️ Separate Channel Upload [Toogle]", data="scul")],
            [Button.inline("🔊 Broadcast", data="cast")],
        ]
        return btn

    def back_btn(self):
        return [[Button.inline("🔙", data="bek")]]

    async def _logs(self, e):
        await e.delete()
        await e.reply(
            file="AutoAnimeBot.log", thumb="thumb.jpg", buttons=self.back_btn()
        )

    async def _restart(self, e, schedule):
        await e.reply("`Restarting...`")
        schedule.restart()

    async def _encode_t(self, e):
        if await self.db.is_original_upload():
            await self.db.toggle_original_upload()
            return await e.edit(
                "`Successfully On The Compression`", buttons=self.back_btn()
            )
        await self.db.toggle_original_upload()
        return await e.edit(
            "`Successfully Off The Compression`", buttons=self.back_btn()
        )

    async def _btn_t(self, e):
        if await self.db.is_separate_channel_upload():
            return await e.edit(
                "`You Can't On/Off The Button Upload When Seprate Channel Is Enabled`",
                buttons=self.back_btn(),
            )
        if await self.db.is_button_upload():
            await self.db.toggle_button_upload()
            return await e.edit(
                "`Successfully Off The Button Upload`", buttons=self.back_btn()
            )
        await self.db.toggle_button_upload()
        return await e.edit("`Successfully On The Upload`", buttons=self.back_btn())

    async def _ss_t(self, e):
        if await self.db.is_ss_upload():
            await self.db.toggle_ss_upload()
            await e.edit(
                "`Successfully DISABLED Screenshot & Mediainfo Upload`",
                buttons=self.back_btn(),
            )
        else:
            await self.db.toggle_ss_upload()
            await e.edit(
                "`Successfully ENABLED Screenshot & Mediainfo Upload`",
                buttons=self.back_btn(),
            )

    async def _sep_c_t(self, e):
        if Var.SESSION:
            if await self.db.is_button_upload():
                if await self.db.is_separate_channel_upload():
                    await self.db.toggle_separate_channel_upload()
                    return await e.edit(
                        "`Successfully Off The Separate Channel Upload`",
                        buttons=self.back_btn(),
                    )
                await self.db.toggle_separate_channel_upload()
                return await e.edit(
                    "`Successfully On The Separate Channel Upload`",
                    buttons=self.back_btn(),
                )
            else:
                return await e.edit(
                    "`To Use The Separate Channel Upload First You Have To Enable Button Upload`",
                    buttons=self.back_btn(),
                )
        else:
            return await e.edit(
                "`To Use The Separate Channel Upload First You Have To Add SESSION Variable in The Bot",
                buttons=self.back_btn(),
            )

    async def broadcast_bt(self, e):
        users = await self.db.get_broadcast_user()
        await e.edit("**Please Use This Feature Responsibly ⚠️**")
        await e.reply(
            f"**Send a single Message To Broadcast 😉**\n\n**There are** `{len(users)}` **Users Currently Using Me👉🏻**.\n\nSend /cancel to Cancel Process."
        )
        async with e.client.conversation(e.sender_id) as cv:
            reply = cv.wait_event(events.NewMessage(from_users=e.sender_id))
            repl = await reply
            await e.delete()
            if repl.text and repl.text.startswith("/cancel"):
                return await repl.reply("`Broadcast Cancelled`")
        sent = await repl.reply("`🗣️ Broadcasting Your Post...`")
        done, er = 0, 0
        for user in users:
            try:
                if repl.poll:
                    await repl.forward_to(int(user))
                else:
                    await e.client.send_message(int(user), repl.message)
                await asyncio.sleep(0.2)
                done += 1
            except BaseException as ex:
                er += 1
                print(ex)
        await sent.edit(
            f"**Broadcast Completed To** `{done}` **Users.**\n**Error in** `{er}` **Users.**"
        )

    async def _about(self, e):
        total_docs = await self.db.file_store_db.count_documents({})
        total_users = await self.db.broadcast_db.count_documents({})
        text = ABOUT.format(
            self.tools.ts(int((dt.now() - self.started_at).seconds) * 1000),
            Var.__version__,
            total_users,
            total_docs,
            self.python_version,
            self.telethon_version,
            self.pyrogram_version,
            self.system,
            "[OngoingAnimeBot](https://github.com/AutoAnimeBot)",
        )
        await e.reply(text, file="assest/about.jpg", link_preview=False)
