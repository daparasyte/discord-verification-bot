import time
import PIL.ImageColor
import claptcha
import nextcord
from nextcord.utils import get
from nextcord.ui import Button, View
from nextcord.ext import commands
from dotenv import load_dotenv
import os
from os import getenv
import random
import string
from PIL import Image
from claptcha import Claptcha
import shutil

load_dotenv()

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

class Captcha(View):
    def __init__(self):
        super().__init__(timeout=None)

    #generating Captcha for a user
    @nextcord.ui.button(label='Verify Me!', style=nextcord.ButtonStyle.green)
    async def button_callback(self, button: Button, interaction: nextcord.Interaction):
        def randomString():
            rndLetters = (random.choice(string.ascii_uppercase) for _ in range(3))
            rndNumbers = (random.choice(string.digits) for _ in range(2))
            return "".join(rndLetters).join(rndNumbers)

        # 600x200 px, using bicubic resampling filter and adding some white noise
        c = Claptcha(randomString(), "arial.ttf", resample=Image.BICUBIC, noise=0.8, margin=(25,25), size=(350, 100))
        text, _ = c.write("captcha1.png")

        img = Image.open("captcha1.png")
        img = img.convert("RGB")
        d = img.getdata()
        coloured = []
        for item in d:
            # change all white (also shades of whites)
            # pixels to yellow
            if item[0] in list(range(200, 256)):
                coloured.append((135,206,235))
            else:
                coloured.append(item)
        img.putdata(coloured)
        img.save("captcha1.png")

        ID = interaction.user.id

        timestr = time.strftime("%d%m%Y-%H%M%S")                #file to store the user id
        ui = open(f"UserID/user_at_{timestr}.txt", "w")
        ui.write(f'{ID}')
        ui.close()

        file = open(f"captchaFolder/captcha_{ID}.txt", "w")     #file to store Captcha for that particular user
        file.write(text)
        file.close()

        f = open(f"Counter/counter_{ID}.txt", "w")              #file to store number of attempts left for a user
        f.write(str(2))
        f.close()

        try:
            layout = Layout()
            emb = nextcord.Embed(
                title='Captcha Verification!',
                description=f'Press each letter one-by-one using the buttons below.\n\n**Attempts left: 3**',
                colour=nextcord.Colour.orange()
            )
            f = nextcord.File("captcha1.png", filename='captcha.png')
            emb.set_image(url="attachment://captcha.png")
            await interaction.response.send_message(ephemeral=True, view=layout, embed=emb, file=f)
        except Exception:
            await interaction.response.send_message("Oops! Something went wrong. Please click \"Verify Me!\" again!", ephemeral=True)

class button1(Button):
    def __init__(self, label, style, disabled, id):
        super().__init__(label=label, style=style, disabled=disabled, custom_id=id)

    async def callback(self, interaction):
        for child in self.view.children:
            for i in range(4):
                if child.custom_id == f'a{i}':
                    child.disabled=True
                    child.style = nextcord.ButtonStyle.gray
                elif child.label == 'New Captcha':
                    child.disabled = True
        ID = interaction.user.id
        file = open(f"captchaFolder/captcha_{ID}.txt", "r")
        a = file.read(1); b = file.read(1); c = file.read(1); d = file.read(1); e = file.read(1)

        if self.label == a:         #for correct Captcha entry
            self.style = nextcord.ButtonStyle.green
            for child in self.view.children:
                for i in range(4):
                    if child.custom_id == f'b{i}':
                        child.disabled = False
                        child.style = nextcord.ButtonStyle.blurple
        else:                       #for wrong Captcha entry
            self.disabled=True
            self.style=nextcord.ButtonStyle.red
            for child in self.view.children:
                if child.label == a or child.label == b or child.label == c or child.label == d or child.label == e:
                        child.style = nextcord.ButtonStyle.green
                elif child.label == 'New Captcha':
                    child.label = "Try Again"
                    child.emoji = "🔁"
                    child.style = nextcord.ButtonStyle.blurple
                    child.disabled = False

                    f = open(f"Counter/counter_{ID}.txt", "r")
                    atmpt = f.read()
                    num = int(atmpt)
                    f.close()

                    if num != 0:
                        num -= 1
                        f = open(f"Counter/counter_{ID}.txt", "w")
                        f.write(str(num))
                        f.close()
                    else:
                        fail = nextcord.Embed(
                            title='Verification Failed!',
                            description='You have exceeded the allowable attempts limit. For security reasons you will be kicked from the server within 30 seconds.\n\n You can rejoin using the server link and verify yourself again.',
                            colour=nextcord.Colour.red()
                        )
                        wrong = nextcord.File('wrong.png', filename='wrong.png')
                        fail.set_thumbnail(url='attachment://wrong.png')
                        self.view.clear_items()
                        await interaction.edit(embed=fail, view=self.view, attachments=[], file=wrong)
                        time.sleep(20)
                        await interaction.user.kick()
                        reason = nextcord.Embed(
                            title="Failed to Verify!",
                            description="For security reasons, we have decided to kick you.\nYou may rejoin for verification using the link below.\n\n*insert your server link here*",
                        colour = nextcord.Colour.blue()
                        )
                        await interaction.user.send(embed=reason)
        await interaction.edit(view=self.view)

class button2(Button):
    def __init__(self, label, disabled, id):
        super().__init__(label=label, disabled=disabled, custom_id=id)

    async def callback(self, interaction):
        for child in self.view.children:
            for i in range(4):
                if child.custom_id == f'b{i}':
                    child.disabled=True
                    child.style = nextcord.ButtonStyle.gray
        ID = interaction.user.id
        file = open(f"captchaFolder/captcha_{ID}.txt", "r")
        a = file.read(1); b = file.read(1); c = file.read(1); d = file.read(1); e = file.read(1)

        if self.label == b:
            self.style = nextcord.ButtonStyle.green
            for child in self.view.children:
                for i in range(4):
                    if child.custom_id == f'c{i}':
                        child.disabled = False
                        child.style = nextcord.ButtonStyle.blurple
        else:
            self.style = nextcord.ButtonStyle.red
            self.disabled = True
            for child in self.view.children:
                if child.label == b or child.label == c or child.label == d or child.label == e:
                        child.style = nextcord.ButtonStyle.green
                elif child.label == 'New Captcha':
                    child.label = "Try Again"
                    child.emoji = "🔁"
                    child.style = nextcord.ButtonStyle.blurple
                    child.disabled = False

                    f = open(f"Counter/counter_{ID}.txt", "r")
                    atmpt = f.read()
                    num = int(atmpt)
                    f.close()

                    if num != 0:
                        num -= 1
                        f = open(f"Counter/counter_{ID}.txt", "w")
                        f.write(str(num))
                        f.close()
                    else:
                        fail = nextcord.Embed(
                            title='Verification Failed!',
                            description='You have exceeded the allowable attempts limit. For security reasons you will be kicked from the server within 30 seconds.\n\n You can rejoin using the server link and verify yourself again.',
                            colour=nextcord.Colour.red()
                        )
                        wrong = nextcord.File('wrong.png', filename='wrong.png')
                        fail.set_thumbnail(url='attachment://wrong.png')
                        self.view.clear_items()
                        await interaction.edit(embed=fail, view=self.view, attachments=[], file=wrong)
                        time.sleep(20)
                        await interaction.user.kick()
                        reason = nextcord.Embed(
                            title="Failed to Verify!",
                            description="For security reasons, we have decided to kick you.\nYou may rejoin for verification using the link below.\n\n*insert your server link here*",
                        colour = nextcord.Colour.blue()
                        )
                        await interaction.user.send(embed=reason)
        await interaction.edit(view=self.view)

class button3(Button):
    def __init__(self, label, disabled, id):
        super().__init__(label=label, disabled=disabled, custom_id=id)

    async def callback(self, interaction):
        for child in self.view.children:
            for i in range(4):
                if child.custom_id == f'c{i}':
                    child.disabled=True
                    child.style = nextcord.ButtonStyle.gray
        ID = interaction.user.id
        file = open(f"captchaFolder/captcha_{ID}.txt", "r")
        a = file.read(1); b = file.read(1); c = file.read(1); d = file.read(1); e = file.read(1)

        if self.label == c:
            self.style = nextcord.ButtonStyle.green
            for child in self.view.children:
                for i in range(4):
                    if child.custom_id == f'd{i}':
                        child.disabled = False
                        child.style = nextcord.ButtonStyle.blurple
        else:
            self.style = nextcord.ButtonStyle.red
            self.disabled = True
            for child in self.view.children:
                if child.label == c or child.label == d or child.label == e:
                        child.style = nextcord.ButtonStyle.green
                elif child.label == 'New Captcha':
                    child.label = "Try Again"
                    child.emoji = "🔁"
                    child.style = nextcord.ButtonStyle.blurple
                    child.disabled = False

                    f = open(f"Counter/counter_{ID}.txt", "r")
                    atmpt = f.read()
                    num = int(atmpt)
                    f.close()

                    if num != 0:
                        num -= 1
                        f = open(f"Counter/counter_{ID}.txt", "w")
                        f.write(str(num))
                        f.close()
                    else:
                        fail = nextcord.Embed(
                            title='Verification Failed!',
                            description='You have exceeded the allowable attempts limit. For security reasons you will be kicked from the server within 30 seconds.\n\n You can rejoin using the server link and verify yourself again.',
                            colour=nextcord.Colour.red()
                        )
                        wrong = nextcord.File('wrong.png', filename='wrong.png')
                        fail.set_thumbnail(url='attachment://wrong.png')
                        self.view.clear_items()
                        await interaction.edit(embed=fail, view=self.view, attachments=[], file=wrong)
                        time.sleep(20)
                        await interaction.user.kick()
                        reason = nextcord.Embed(
                            title="Failed to Verify!",
                            description="For security reasons, we have decided to kick you.\nYou may rejoin for verification using the link below.\n\n*insert your server link here*",
                        colour = nextcord.Colour.blue()
                        )
                        await interaction.user.send(embed=reason)
        await interaction.edit(view=self.view)

class button4(Button):
    def __init__(self, label, disabled, id):
        super().__init__(label=label, disabled=disabled, custom_id=id)

    async def callback(self, interaction):
        for child in self.view.children:
            for i in range(4):
                if child.custom_id == f'd{i}':
                    child.disabled=True
                    child.style = nextcord.ButtonStyle.gray
        ID = interaction.user.id
        file = open(f"captchaFolder/captcha_{ID}.txt", "r")
        a = file.read(1); b = file.read(1); c = file.read(1); d = file.read(1); e = file.read(1)

        if self.label == d:
            self.style = nextcord.ButtonStyle.green
            for child in self.view.children:
                for i in range(4):
                    if child.custom_id == f'e{i}':
                        child.disabled = False
                        child.style = nextcord.ButtonStyle.blurple
        else:
            self.style = nextcord.ButtonStyle.red
            self.disabled = True
            for child in self.view.children:
                if child.label == d or child.label == e:
                        child.style = nextcord.ButtonStyle.green
                elif child.label == 'New Captcha':
                    child.label = "Try Again"
                    child.emoji = "🔁"
                    child.style = nextcord.ButtonStyle.blurple
                    child.disabled=False

                    f = open(f"Counter/counter_{ID}.txt", "r")
                    atmpt = f.read()
                    num = int(atmpt)
                    f.close()

                    if num != 0:
                        num -= 1
                        f = open(f"Counter/counter_{ID}.txt", "w")
                        f.write(str(num))
                        f.close()
                    else:
                        fail = nextcord.Embed(
                            title='Verification Failed!',
                            description='You have exceeded the allowable attempts limit. For security reasons you will be kicked from the server within 30 seconds.\n\n You can rejoin using the server link and verify yourself again.',
                            colour=nextcord.Colour.red()
                        )
                        wrong = nextcord.File('wrong.png', filename='wrong.png')
                        fail.set_thumbnail(url='attachment://wrong.png')
                        self.view.clear_items()
                        await interaction.edit(embed=fail, view=self.view, attachments=[], file=wrong)
                        time.sleep(20)
                        await interaction.user.kick()
                        reason = nextcord.Embed(
                            title="Failed to Verify!",
                            description="For security reasons, we have decided to kick you.\nYou may rejoin for verification using the link below.\n\nhttps://discord.gg/h3mYpSfeMX",
                        colour = nextcord.Colour.blue()
                        )
                        await interaction.user.send(embed=reason)
        await interaction.edit(view=self.view)

class button5(Button):
    def __init__(self, label, disabled, id):
        super().__init__(label=label, disabled=disabled, custom_id=id)

    async def callback(self, interaction):
        for child in self.view.children:
            for i in range(4):
                if child.custom_id == f'e{i}':
                    child.disabled = True
                    child.style = nextcord.ButtonStyle.gray
        ID = interaction.user.id
        file = open(f"captchaFolder/captcha_{ID}.txt", "r")
        a = file.read(1); b = file.read(1); c = file.read(1); d = file.read(1); e = file.read(1)

        file.close()
        if self.label == e:
            self.style = nextcord.ButtonStyle.green
            id = os.getenv('VERIFIED_ROLE_ID')
            role = get(interaction.guild.roles, id=int(id)) or get(interaction.guild.roles, id=int(id))
            emb = nextcord.Embed(
                title='Verification Successful!',
                description='You have been verified successfully!\nNo further action is required at this time.\n\nYou will gain access to the server within 20 seconds',
                colour=nextcord.Colour.green()
            )

            ver = nextcord.File('verified.png', filename='verified.png')
            emb.set_thumbnail(url='attachment://verified.png')
            await interaction.edit(content=None, embed=emb, view=None, file=ver, delete_after=30, attachments=[])
            time.sleep(5)
            await interaction.user.add_roles(role)
        os.remove(f"captchaFolder/captcha_{ID}.txt")
        os.remove(f"Counter/counter_{ID}.txt")
        else:
            self.style = nextcord.ButtonStyle.red
            self.disabled = True
            for child in self.view.children:
                if child.label == e:
                        child.style = nextcord.ButtonStyle.green
                elif child.label == 'New Captcha':
                    child.label = "Try Again"
                    child.emoji = "🔁"
                    child.style = nextcord.ButtonStyle.blurple
                    child.disabled=False

                    f = open(f"Counter/counter_{ID}.txt", "r")
                    atmpt = f.read()
                    num = int(atmpt)
                    f.close()

                    if num != 0:
                        num -= 1
                        f = open(f"Counter/counter_{ID}.txt", "w")
                        f.write(str(num))
                        f.close()
                    else:
                        fail = nextcord.Embed(
                            title='Verification Failed!',
                            description='You have exceeded the allowable attempts limit. For security reasons you will be kicked from the server within 30 seconds.\n\n You can rejoin using the server link and verify yourself again.',
                            colour=nextcord.Colour.red()
                        )
                        wrong = nextcord.File('wrong.png', filename='wrong.png')
                        fail.set_thumbnail(url='attachment://wrong.png')
                        self.view.clear_items()
                        await interaction.edit(embed=fail, view=self.view, attachments=[], file=wrong)
                        time.sleep(20)
                        await interaction.user.kick()
                        reason = nextcord.Embed(
                            title="Failed to Verify!",
                            description="For security reasons, we have decided to kick you.\nYou may rejoin for verification using the link below.\n\n*insert your server link here*",
                        colour = nextcord.Colour.blue()
                        )
                        await interaction.user.send(embed=reason)
            await interaction.edit(view=self.view)

class New(Button):
    def __init__(self, label, style, emoji):
        super().__init__(label=label, style=style, emoji=emoji)

    #Same as Captcha class
    async def callback(self, interaction):

        def randomString():
            rndLetters = (random.choice(string.ascii_uppercase) for _ in range(3))
            rndNumbers = (random.choice(string.digits) for _ in range(2))
            return "".join(rndLetters).join(rndNumbers)

        # 600x200 px, using bicubic resampling filter and adding some white noise
        c = Claptcha(randomString(), "arial.ttf", resample=Image.BICUBIC, noise=0.7, margin=(25,25), size=(350, 100))
        text, _ = c.write("captcha2.png")
        img = Image.open("captcha2.png")
        img = img.convert("RGB")
        d = img.getdata()
        coloured = []
        for item in d:
            if item[0] in list(range(200, 256)):
                coloured.append((135, 206, 235))
            else:
                coloured.append(item)
        img.putdata(coloured)
        img.save("captcha2.png")

        ID = interaction.user.id

        timestr = time.strftime("%d%m%Y-%H%M%S")
        ui = open(f"UserID/user_at_{timestr}.txt", "w")
        ui.write(f'{ID}')
        ui.close()
        file = open(f"captchaFolder/captcha_{ID}.txt", "w")
        file.write(text)
        file.close()

        f = open(f"Counter/counter_{ID}.txt", "r")
        num = f.read(1)
        n = int(num)
        n = n+1
        f.close()

        try:
            emb_new = nextcord.Embed(
                title='Captcha Verification!',
                description=f'Press each letter one-by-one using the buttons below.\n\n**Attempts left: {str(n)}**',
                colour=nextcord.Colour.orange()
            )
            f = nextcord.File("captcha2.png", filename='captcha2.png')
            emb_new.set_image(url="attachment://captcha2.png")
            view = Layout()
            await interaction.edit(file=f, view=view, embed=emb_new, attachments=[])
        except Exception:
            await interaction.edit("Oops! Something went wrong. Please try again!", view=view)

class Layout(View):
    def __init__(self):
        super().__init__(timeout=120)

        timestr = time.strftime("%d%m%Y-%H%M%S")
        ID = open(f"UserID/user_at_{timestr}.txt", "r")
        ui = ID.read()
        ID.close()

        file = open(f"captchaFolder/captcha_{ui}.txt", "r")     #Reading text one character at a time
        a = file.read(1)
        b = file.read(1)
        c = file.read(1)
        d = file.read(1)
        e = file.read(1)

        os.remove(f"UserID/user_at_{timestr}.txt")
        x = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
             "V", "W", "X", "Y", "Z"]
        y = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        x.remove(b); x.remove(c); x.remove(d)
        y.remove(a); y.remove(e)

        A = []
        A.append(a)
        for i in range(3):
            p = random.choice(y)
            A.append(p)
            y.remove(p)
        print("A: ", A)

        B = []
        B.append(b)
        for i in range(3):
            q = random.choice(x)
            B.append(q)
            x.remove(q)
        print("B: ", B)

        C = []
        C.append(c)
        for i in range(3):
            r = random.choice(x)
            C.append(r)
            x.remove(r)
        print("C: ", C)

        D = []
        D.append(d)
        for i in range(3):
            s = random.choice(x)
            D.append(s)
            x.remove(s)
        print("D: ", D)

        E = []
        E.append(e)
        for i in range(3):
            t = random.choice(y)
            E.append(t)
            y.remove(t)
        print("E: ", E)

        for i in range(4):
            p_1 = random.choice(A)
            A.remove(p_1)
            p_2 = random.choice(B)
            B.remove(p_2)
            p_3 = random.choice(C)
            C.remove(p_3)
            p_4 = random.choice(D)
            D.remove(p_4)
            p_5 = random.choice(E)
            E.remove(p_5)

            b1 = button1(f'{p_1}', nextcord.ButtonStyle.blurple, False, f'a{i}')
            b2 = button2(f'{p_2}', True, f'b{i}')
            b3 = button3(f'{p_3}', True, f'c{i}')
            b4 = button4(f'{p_4}', True, f'd{i}')
            b5 = button5(f'{p_5}', True, f'e{i}')
            #Adding the buttons
            self.add_item(b1)
            self.add_item(b2)
            self.add_item(b3)
            self.add_item(b4)
            self.add_item(b5)

        self.add_item(New("New Captcha", nextcord.ButtonStyle.red, "🔁"))


@bot.event
async def on_ready():
    print("Bot running...")
    channel = os.getenv('VERIFICATION_CHANNEL_ID')
    channel1 = bot.get_channel(int(channel))
    await channel1.purge(limit=50)


@bot.event
async def on_member_join(member):
    channel = os.getenv('VERIFICATION_CHANNEL_ID')
    channel1 = bot.get_channel(int(channel))
    await channel1.send(f'{member.mention}')
    await channel1.purge(limit=1)

# comparing user message with Captcha
@bot.event
async def on_message(message):
    view = View.from_message(message, timeout=None)
    if message.author == bot.user:
        return
    elif message.author == message.guild.owner and message.content.startswith("verify"):
        view = Captcha()
        embed = nextcord.Embed(
            title='SERVER VERIFICATION!',
            description='To prevent bot abuse, new members are required to verify in this server.\n**To begin verification please press the button below.**\n\n*Note: You must verify yourself in order to gain access to the server!*',
            colour=nextcord.Colour.blue()
        )
        await message.channel.send(embed=embed, view=view)
    else:
        pass
    await bot.process_commands(message)
    await message.delete()


bot.run(getenv('TOKEN'))
