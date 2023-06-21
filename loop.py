import discord
from discord import app_commands # coding: utf-8
from discord.ext import tasks
import configparser
import requests
import cv2
import datetime
import locale
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテントのintentはオンにする
intents.members = True
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
START = 0
END = 1

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
    schedule_current = jsondata['regular'][0]
    return schedule_current

def get_day_of_week_jp(time):
    time_trimmed  = time[0:10]
    dt = datetime.datetime.strptime(time_trimmed, '%Y-%m-%d')
    w_list = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    return('(' + w_list[dt.weekday()][0:1] + ')')

def set_stage_name(stage):
    stage_dic = {'アラマキ砦':'https://images.gamepedia.jp/splatoon3/badge/s7hg.png', 
                'ムニ・エール海洋発電所':'https://images.gamepedia.jp/splatoon3/badge/m865.png', 
                'シェケナダム':'https://images.gamepedia.jp/splatoon3/badge/ec2w.png', 
                '難破船ドン・ブラコ':'https://images.gamepedia.jp/splatoon3/badge/434c.png',
                'すじこジャンクション跡':'https://images.gamepedia.jp/splatoon3/badge/1q0v.png'}
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
                "S-BLAST92":"S-BLAST'92",

                "カーボンローラー":"CarbonRoller", 
                "スプラローラー":"SplatRoller", 
                "ダイナモローラー":"DynamoRoller", 
                "ヴァリアブルローラー":"FlingzaRoller", 
                "ワイドローラー":"BigSwigRoller", 
                "パブロ":"Inkbrush", 
                "ホクサイ":"Octobrush", 
                "フィンセント":"Painbrush",

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
    shiht_time = (time[START] + ' - ' + time[END])
    embed = discord.Embed(title = str(shiht_time), 
                          description =  str(weapon[0]) +'\n'+ str(weapon[1]) +'\n'+ 
                          str(weapon[2]) +'\n'+ str(weapon[3]),
                          color = int('0xF63E1D', 16))
    embed.set_author(name = stage, )
    return embed

messege_list = ["", "", "", "", ""]

@tasks.loop(seconds=60) #60秒毎
async def send_message():
    url = 'https://api.koukun.jp/splatoon/3/schedules/coop/'
    # 最新のシフトの時刻を取得
    smnw_start_time_current = request_api(url)['start']
    smnw_start_time_recorded = ''

    # txtファイルに記録されているシフトの時刻を取得する
    with open('changed_shift_check.txt', mode='r') as f:
        # ファイルの読み込んで変数に代入
        smnw_start_time_recorded = f.read()
    f.close

    # 取得した最新の時刻と、記録されている時刻が違う場合(=現在のスケジュールが更新された場合)
    if smnw_start_time_current != smnw_start_time_recorded:
        # apiから情報を取得
        smnw_end_time_current = request_api(url)['end']
        time = [smnw_start_time_current, smnw_end_time_current]

        #time =[request_api(url)['start'].replace('-', '/'), request_api(url)['end'].replace('-', '/')]
        day_of_week = [get_day_of_week_jp(time[START]), get_day_of_week_jp(time[END])]
        time[START] = (time[START][5:10] + day_of_week[START] + time[START][10:16]).replace('-', '/')
        time[END] = (time[END][5:10] + day_of_week[END] + time[END][10:16]).replace('-', '/')
        stage = request_api(url)['stage']
        weapon_list = []
        weapons_data = request_api(url)['weapons']
        for wepon in weapons_data:
            weapon_list.append(wepon['name'])
        
        print(request_api(url)['start'].replace('-', '/'))
        # メッセージを送信
        embed = add_embed_srnwShift(time, stage, weapon_list)
        save_weapons_image(weapon_list)
        fname="image.png "
        # ローカルファイルのアドレスに注意
        image_file = discord.File(fp=config_ini.get('PATH', 'path'),filename=fname) 
        embed.set_image(url="attachment://image.png") 
        embed.set_thumbnail(url=f"{set_stage_name(stage)}")
        
        guild = discord.utils.find(lambda g: g.id == config_ini.getint('GUILD', 'guild_id_ygm'), client.guilds)
        #guild_2 = discord.utils.find(lambda g: g.id == config_ini.getint('GUILD', 'guild_id_1'), client.guilds)
        channel = guild.get_channel(config_ini.getint('CHANNEL', 'channel_id'))
        #channel_2 = guild_2.get_channel(config_ini.getint('CHANNEL', 'channel_id_1'))

        await channel.send(file=image_file, embed=embed)
        #image_file_2 = discord.File(fp=config_ini.getint('PATH', 'path'),filename=fname) 
        #await channel_2.send(file=image_file_2, embed=embed)

        # 書き込む
        with open('changed_shift_check.txt', 'w', encoding='UTF-8', newline='\n') as f:
            data = smnw_start_time_current
            f.writelines(data)
        f.close()
    else:
        return

@client.event
async def on_ready(): #botログイン完了時に実行
    print('on_ready') 
    send_message.start()
    
client.run(config_ini.get('TOKEN', 'token'))  