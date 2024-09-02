import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 디버깅을 위한 기본 로그 설정
import logging
logging.basicConfig(level=logging.INFO)

# 경매 데이터를 저장할 딕셔너리
auctions = {}
auction_logs = {}

# 봇이 준비되었을 때 호출되는 이벤트
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

# 봇이 서버에서 메시지를 받을 때마다 호출되는 이벤트
@bot.event
async def on_message(message):
    # 봇이 스스로의 메시지를 처리하지 않도록 함
    if message.author == bot.user:
        return

    # 명령어가 실행되도록 설정
    await bot.process_commands(message)

# 명령어 메시지 삭제 함수
async def delete_command_message(ctx):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print("봇이 메시지를 삭제할 권한이 없습니다.")
    except discord.NotFound:
        print("메시지가 이미 삭제된 경우입니다.")

# 경매 시작 명령어
@bot.command()
async def 시작(ctx, item_name: str, starting_bid: int, in_game_name: str):
    """새로운 경매를 시작합니다. !시작 <아이템 이름> <시작 가격> <게임 내 닉네임>"""
    if not item_name or not starting_bid or not in_game_name:
        await ctx.send("명령어 사용법: !시작 <아이템 이름> <시작 가격> <게임 내 닉네임>")
        return

    if item_name in auctions:
        await ctx.send("이미 이 아이템에 대한 경매가 진행 중입니다!")
    else:
        end_time = datetime.utcnow() + timedelta(minutes=5)  # 5분 후 자동 종료
        auction_message = await ctx.send(f"경매가 시작되었습니다! 아이템: {item_name}, 시작 가격: {starting_bid}골드, 게임 내 닉네임: {in_game_name}")
        
        auctions[item_name] = {
            "starting_bid": starting_bid,
            "highest_bid": starting_bid,
            "highest_bidder": None,
            "start_time": datetime.utcnow(),
            "end_time": end_time,
            "in_game_name": in_game_name,
            "auction_message": auction_message  # 채팅 메시지 저장
        }
        
        embed = discord.Embed(title="경매 시작", description=f"아이템: {item_name}\n시작 가격: {starting_bid}골드\n게임 내 닉네임: {in_game_name}",
                              color=discord.Color.blue())
        embed.add_field(name="종료 시간", value=end_time.strftime('%Y-%m-%d %H:%M:%S UTC'))
        await ctx.send(embed=embed)
        
        # 명령어 메시지 삭제
        await delete_command_message(ctx)
        
        auto_end_auction.start(ctx, item_name)

# 입찰 명령어
@bot.command()
async def 입찰(ctx, item_name: str, bid: int):
    """현재 진행 중인 경매에 입찰합니다. !입찰 <아이템 이름> <입찰 가격>"""
    if not item_name or not bid:
        await ctx.send("명령어 사용법: !입찰 <아이템 이름> <입찰 가격>")
        return

    if item_name not in auctions:
        await ctx.send("해당 아이템에 대한 경매가 존재하지 않습니다.")
    else:
        current_auction = auctions[item_name]
        if bid > current_auction["highest_bid"]:
            current_auction["highest_bid"] = bid
            current_auction["highest_bidder"] = ctx.author
            await ctx.send(f"{ctx.author}님이 {bid}골드로 {item_name}에 입찰하셨습니다!")
        else:
            await ctx.author.send(f"입찰 금액이 현재 최고 입찰가 {current_auction['highest_bid']}골드보다 낮습니다. 더 높은 금액으로 다시 입찰해 주세요.")

    # 명령어 메시지 삭제
    await delete_command_message(ctx)

# 경매 종료 명령어
@bot.command()
async def 종료(ctx, item_name: str):
    """경매를 종료하고, 최고 입찰자를 발표합니다. !종료 <아이템 이름>"""
    if not item_name:
        await ctx.send("명령어 사용법: !종료 <아이템 이름>")
        return

    if item_name not in auctions:
        await ctx.send("해당 아이템에 대한 경매가 존재하지 않습니다.")
    else:
        await end_auction(ctx, item_name)

    # 명령어 메시지 삭제
    await delete_command_message(ctx)

# 자동 종료 타이머
@tasks.loop(seconds=1)
async def auto_end_auction(ctx, item_name):
    if item_name in auctions and datetime.utcnow() >= auctions[item_name]["end_time"]:
        await end_auction(ctx, item_name)
        auto_end_auction.stop()

# 경매 종료 처리
async def end_auction(ctx, item_name):
    current_auction = auctions.pop(item_name)
    log_entry = {
        "item": item_name,
        "winner": current_auction["highest_bidder"],
        "winning_bid": current_auction["highest_bid"],
        "in_game_name": current_auction["in_game_name"],
        "timestamp": datetime.utcnow()
    }
    auction_logs[item_name] = log_entry

    # 경매 관련 메시지 삭제
    if current_auction["auction_message"]:
        try:
            await current_auction["auction_message"].delete()
        except discord.NotFound:
            pass  # 메시지가 이미 삭제된 경우

    if current_auction["highest_bidder"] is None:
        embed = discord.Embed(title="경매 종료", description=f"{item_name}에 대한 입찰이 없어 경매가 종료되었습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        winner = current_auction["highest_bidder"]
        winning_bid = current_auction["highest_bid"]
        embed = discord.Embed(title="경매 종료", description=f"{item_name}은 {winner}님이 {winning_bid}골드에 낙찰되었습니다!\n게임 내 닉네임: {current_auction['in_game_name']}",
                              color=discord.Color.green())
        await ctx.send(embed=embed)
        await winner.send(f"축하합니다! {item_name}을 {winning_bid}골드에 낙찰 받았습니다.")

# 경매 로그 보기 명령어
@bot.command()
async def 경매로그(ctx):
    """이전 경매 기록을 보여줍니다."""
    if not auction_logs:
        await ctx.send("저장된 경매 로그가 없습니다.")
    else:
        logs = "\n".join([f"{log['timestamp']} - {log['item']} : {log['winner']} ({log['in_game_name']})님이 {log['winning_bid']}골드에 낙찰" for log in auction_logs.values()])
        embed = discord.Embed(title="경매 기록", description=logs, color=discord.Color.orange())
        await ctx.send(embed=embed)

# 경매 목록 보기 명령어
@bot.command()
async def 경매목록(ctx):
    """현재 진행 중인 모든 경매 목록을 표시합니다."""
    if not auctions:
        await ctx.send("현재 진행 중인 경매가 없습니다.")
    else:
        auction_list = "\n".join([
            f"{item}: 현재 최고 입찰가 {data['highest_bid']}골드 (게임 내 닉네임: {data['in_game_name']}) - 종료 시간: {data['end_time'].strftime('%Y-%m-%d %H:%M:%S')}" 
            for item, data in auctions.items()
        ])
        embed = discord.Embed(title="현재 진행 중인 경매 목록", description=auction_list, color=discord.Color.purple())
        await ctx.send(embed=embed)

# 디스코드 봇 토큰
TOKEN = 'MTI3OTcwMzM1ODgxMDM2MTg2OA.G4dmp2.6uWqpxgpy1ak_k--WGXHHf_rxMwgENMRVhB2mk'

bot.run(TOKEN)
