import discord
from discord import app_commands # coding: utf-8
from discord.ext import tasks
import configparser
import requests
import cv2

intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテントのintentはオンにする
intents.members = True
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

MY_GUILDS = [discord.Object(id=config_ini.getint('GUILD', 'guild_id_ygm'))]

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self) 
    async def setup_hook(self):
        for id in MY_GUILDS:
            self.tree.copy_global_to(guild=id)
            await self.tree.sync(guild=id)
    
client = MyClient(intents=intents)

def request_api(url):
    response  = requests.get(url)
    jsondata = response.json()
    schedule_now = jsondata['regular'][0]
    return schedule_now

def set_stage_name(stage):
    stage_dic = {'アラマキ砦':'https://images.gamepedia.jp/splatoon3/badge/s7hg.png', 
                'ムニ・エール海洋発電所':'https://images.gamepedia.jp/splatoon3/badge/m865.png', 
                'シェケナダム':'https://images.gamepedia.jp/splatoon3/badge/ec2w.png', 
                '難破船ドン・ブラコ':'https://images.gamepedia.jp/splatoon3/badge/434c.png'}
    stage_name = ''
    if stage in stage_dic:
        stage_name = stage_dic[stage]
    return stage_name  

def set_wepon_name(wepon):
    wepon_dic = {"ボールドマーカー":"Sploosh-o-matic", 
                "わかばシューター":"SplattershotJr", 
                "シャープマーカー":"Splash-o-matic", 
                "プロモデラーMG":"AerosprayMG", 
                "スプラシューター":"Splattershot", 
                ".52ガロン":"52Gal", 
                "N-ZAP85":"N-ZAP85", 
                "プライムシューター":"SplattershotPro", 
                ".96ガロン":"96Gal", 
                "ジェットスイーパー":"JetSquelcher", 
                "L3リールガン":"L-3Nozzlenose", 
                "H3リールガン":"H-3Nozzlenose", 
                "ボトルガイザー":"Squeezer", 
                "スペースシューター":"SplattershotNova", 

                "ノヴァブラスター":"LunaBlaster", 
                "ホットブラスター":"Blaster", 
                "ロングブラスター":"RangeBlaster", 
                "クラッシュブラスター":"ClashBlaster", 
                "ラピッドブラスター":"RapidBlaster", 
                "Rブラスターエリート":"RapidBlasterPro", 

                "カーボンローラー":"CarbonRoller", 
                "スプラローラー":"SplatRoller", 
                "ダイナモローラー":"DynamoRoller", 
                "ヴァリアブルローラー":"FlingzaRoller", 
                "ワイドローラー":"BigSwigRoller", 
                "パブロ":"Inkbrush", 
                "ホクサイ":"Octobrush", 

                "スクイックリンα":"ClasicSquiffer", 
                "スプラチャージャー":"SplatCharger", 
                "スプラスコープ":"Splatterscope", 
                "リッター4K":"E-liter4K", 
                "4Kスコープ":"E-liter4KScope", 
                "14式竹筒銃・甲":"Bamboozler14MkI", 
                "ソイチューバー":"GooTuber", 
                "R-PEN/5H":"Snipewriter5H", 

                "バケットスロッシャー":"Slosher", 
                "ヒッセン":"Tri-Slosher", 
                "スクリュースロッシャー":"SloshingMachine", 
                "オーバーフロッシャー":"Bloblobber", 
                "エクスプロッシャー":"Explosher", 

                "スプラスピナー":"MiniSplatling", 
                "バレルスピナー":"HeavySplatling", 
                "ハイドラント":"HydraSplatling", 
                "クーゲルシュライバー":"BallpointSplatling", 
                "ノーチラス47":"Nautilus47", 

                "スパッタリー":"DappleDualies", 
                "スプラマニューバー":"SplatDualies", 
                "ケルビン525":"GloogaDualies", 
                "デュアルスイーパー":"DualieSquelchers", 
                "クアッドホッパーブラック":"DarkTetraDualies", 

                "パラシェルター":"SplatBrella", 
                "キャンピングシェルター":"TentaBrella", 
                "スパイガジェット":"UndercoverBrella",

                "トライストリンガー":"Tri-Stringer", 
                "LACT-450":"REEF-LUX450", 

                "ドライブワイパー":"SplatanaWiper",
                "ジムワイパー":"SplatanaStamper", 
                }

    wepon_name = ""
    if wepon in wepon_dic:
        wepon_name = wepon_dic[wepon]
    else:
        wepon_name = "secret"
    return wepon_name

def save_weapons_image(weapon_list):
    weapon_name = ['', '', '', '']
    for i in range(4):
        weapon_name[i] = set_wepon_name(weapon_list[i])
    img = []
    for i in range(4):
        img.append(cv2.imread('img/'+str(weapon_name[i])+'.png'))
    img_2 = []
    img_2.append(cv2.hconcat([img[0], img[1]]))
    img_2.append(cv2.hconcat([img[2], img[3]]))
    img_3 = cv2.hconcat([img_2[0], img_2[1]])
    cv2.imwrite('img/image.png', img_3)

def add_embed_srnwShift(time, stage, weapon):
    embed = discord.Embed(title = stage, 
                          description =  str(weapon[0]) +'\n'+ str(weapon[1]) +'\n'+ 
                          str(weapon[2]) +'\n'+ str(weapon[3]),
                          color = int('0xF63E1D', 16))
    embed.set_author(name = time, )
    return embed

@tasks.loop(seconds=10)#20秒毎
async def send_message():
    url = 'https://api.koukun.jp/splatoon/3/schedules/coop/'
    # 最新のシフトの時刻を取得
    smnw_time_now = request_api(url)['start']
    smnw_time_recorded = ''
    #print(smnw_time_now)

    # txtファイルに記録されているシフトの時刻を取得する
    with open('changed_shift_check.txt', mode='r') as f:
        # ファイルの読み込んで変数に代入
        smnw_time_recorded = f.read()
    f.close

    #print(smnw_time_recorded)

    # 取得した最新の時刻と、記録されている時刻が違う場合
    if smnw_time_now != smnw_time_recorded:
        print('==')
        # apiから情報を取得
        time =[request_api(url)['start'], request_api(url)['end']]
        stage = request_api(url)['stage']
        weapon_list = []
        weapons_data = request_api(url)['weapons']
        for wepon in weapons_data:
            weapon_list.append(wepon['name'])

        # メッセージを送信
        embed = add_embed_srnwShift(time, stage, weapon_list)
        save_weapons_image(weapon_list)
        fname="image.png "
        image_file = discord.File(fp=f"C:/Users/N/Documents/GitHub/salmonrunnw-schedule-bot/img/image.png ",filename=fname) 
        embed.set_image(url="attachment://image.png") 
        embed.set_thumbnail(url=f"{set_stage_name(stage)}")
        guild = guild = discord.utils.find(lambda g: g.id == config_ini.getint('GUILD', 'guild_id_ygm'), client.guilds)
        channel = guild.get_channel(config_ini.getint('CHANNEL', 'channel_id'))
        await channel.send(file=image_file, embed=embed)
        # ここを書く
        # # 書き込む
        # f = open('changed_shift_check.txt', 'a', encoding='UTF-8', newline='\n')
        # data = str(smnw_time_now)
        # f.writelines(data)
    else:
        return



@client.event
async def on_ready(): #botログイン完了時に実行
    print('on_ready') 
    send_message.start()

client.run(config_ini.get('TOKEN', 'token'))  