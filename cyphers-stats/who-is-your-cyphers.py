from collections import Counter
import datetime as dt
import os

import numpy as np
import pandas as pd
from pytz import timezone
import requests

import config #api_key file

"""당신의 사이퍼즈 취향을 분석해드리는 파이썬 스크립트입니다.

네오플 OpenAPI에서 조회 가능한 최근 100경기를 분석하여 입력한 능력자의 프로필, 선호 캐릭터 목록, 모스트 캐릭터,
승률이 높은 캐릭터 목록, 그리고 날짜별 승률과 그 분석 결과를 보여줍니다. 전적은 1시간마다 갱신됩니다.

사용 가능한 함수:
- get_playerid: 닉네임을 입력값으로 받아 playerid 값을 반환합니다.
- get_playerinfo: playerid를 입력값으로 받아 플레이어 프로필 정보를 반환합니다.
- print_playerinfo: 닉네임, 급수, 티어를 예쁘게 출력합니다.
- get_pvplog: 공식/일반 전적을 반환합니다.
- analyze_pvplog: 전적 기록을 분석합니다.
- print_pvplog: 플레이 스타일, 시간대, 선호 포지션을 출력합니다.
- top_character: 선호 캐릭터 목록, 모스트 캐릭터, 승률이 높은 캐릭터 목록을 출력합니다.
- winrate_per_date: 날짜별 승률과 분석 결과를 출력합니다.

api_key 적용하기:
- https://developers.neople.co.kr/ 에 접속하여 소셜 로그인 후 마이페이지 > 애플리케이션 등록 > api key를 발급받습니다.
- 스크립트 파일과 동일한 경로에 config.py를 생성한 후 key={api_key}를 작성한 뒤 저장합니다.
"""


def get_playerid(user_input):
    try:
        global playerid, username
        api_url = "https://api.neople.co.kr/cy/players?nickname=" + user_input + "&apikey=" + config.key
        api_resp = requests.get(api_url).json()
        playerid = api_resp['rows'][0]['playerId']
        username = api_resp['rows'][0]['nickname']
    except IndexError:
        print("닉네임이 존재하지 않습니다.")
        os._exit(1)
    except requests.exceptions.RequestException:
        print("서버가 응답하지 않습니다.")
        os._exit(1)

def get_playerinfo(player_id):
    try:
        api_url = "https://api.neople.co.kr/cy/players/" + player_id + "?apikey=" + config.key
        api_resp = requests.get(api_url).json()
        return api_resp
    except requests.exceptions.RequestException:
        print("서버가 응답하지 않습니다.")
        os._exit(1)

def print_playerinfo(player_id):
    resp = get_playerinfo(player_id)
    print("")
    print(f'*** {username}님의 프로필 ***')
    print(f'급수: {resp["grade"]}')
    if resp['ratingPoint'] is None:
        print("티어: Unranked")
    else:
        print(f'티어: {resp["ratingPoint"]} ({resp["tierName"]})')

def get_pvplog(game_type):
    now = dt.datetime.now(timezone('Asia/Seoul'))
    now_time = dt.datetime.strftime(now, "%Y-%m-%d %H:%M")
    past = now - dt.timedelta(days=90)
    past_time = dt.datetime.strftime(past, "%Y-%m-%d %H:%M")

    try:
        if game_type == "공식":
            api_url = "https://api.neople.co.kr/cy/players/" + playerid + "/matches?gameTypeId=rating&startDate=" + str(past_time) + "&endDate=" + str(now_time) + "&limit=100&apikey=" + config.key
        else:
            api_url = "https://api.neople.co.kr/cy/players/" + playerid + "/matches?gameTypeId=normal&startDate=" + str(past_time) + "&endDate=" + str(now_time) + "&limit=100&apikey=" + config.key
        api_resp = requests.get(api_url).json()
        return api_resp
    except requests.exceptions.RequestException:
        print("서버가 응답하지 않습니다.")
        os._exit(1)

def analyze_pvplog(game_type):
    global resp, character_list, time_count, party_count, position_count
    resp = get_pvplog(game_type)
    character_list = []
    try:
        for _ in range(0, 100):
            character_list.append(resp['matches']['rows'][_]['playInfo']['characterName'])
    except IndexError:
        pass
    if not character_list:
        print("전적이 존재하지 않습니다.")
        os._exit(1)
    time_count = []
    try:
        for _ in range(0, 100):
            time = resp['matches']['rows'][_]['date'][11:13]
            time_count.append(time)
    except IndexError:
        pass
    time_count = Counter(time_count).most_common(1)
    party_count = []
    try:
        for _ in range(0, 100):
            count = resp['matches']['rows'][_]['playInfo']['partyUserCount']
            party_count.append(count)
    except IndexError:
        pass
    party_count = Counter(party_count).most_common(1)
    position_count = []
    try:
        for _ in range(0, 100):
            count = resp['matches']['rows'][_]['position']['name']
            position_count.append(count)    
    except IndexError:
        pass
    position_count = Counter(position_count).most_common()

def print_pvplog():
    global position_count
    print("")
    print("*** 플레이 스타일 ***")
    if party_count[0][0] == 0:
        print("솔로 플레이어")
    else:
        print(str(party_count[0][0]) + "인 파티 유저")
    print('게임 시간대:', time_count[0][0] + '시')
    print('선호 포지션:', position_count[0][0])
    position_count = dict(position_count)
    position = []
    position_sum = sum(position_count.values())
    for k, v in position_count.items():
        count = " ".join([k + ':', str(round(v / position_sum * 100, 1)) + '%'])
        position.append(count)
    print(f'[{", ".join(position)}]')

def top_character():
    global character_list, most_character
    character_list = Counter(character_list).most_common(5)
    key_list = [key for key, _ in character_list]
    value_list = [key for _, key in character_list]
    most_list = []

    for i in range(len(key_list)):
        playtime = 0
        try:
            for j in range(0, 100):
                if resp['matches']['rows'][j]['playInfo']['characterName'] == key_list[i]:
                    playtime += resp['matches']['rows'][j]['playInfo']['playTime']
        except IndexError:
            pass
        playtime_mins = playtime // 60
        playtime_hours = playtime_mins // 60
        playtime_format = f"{playtime_hours:02d}:{playtime_mins % 60:02d}:{playtime % 60:02d}"
        most_list.append(playtime_format)

    print("")
    print("*** 선호 캐릭터 TOP5 ***")
    for i in range(len(key_list)):
        print(key_list[i] + ':', str(value_list[i])+'판', '(플레이 시간: ' + most_list[i] + ')')
    print("")

    most_character = character_list[0][0]
    most_count = character_list[0][1]

    most_level, most_killcount, most_deathcount, most_assistcount, most_attackpoint, most_damagepoint, most_battlepoint, most_sightpoint, most_getCoin, most_playTime, most_kda = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    try:
        for _ in range(0, 100):
            if resp['matches']['rows'][_]['playInfo']['characterName'] == most_character:
                most_level += resp['matches']['rows'][_]['playInfo']['level']
                most_killcount += resp['matches']['rows'][_]['playInfo']['killCount']
                most_deathcount += resp['matches']['rows'][_]['playInfo']['deathCount']
                most_assistcount += resp['matches']['rows'][_]['playInfo']['assistCount']
                most_attackpoint += resp['matches']['rows'][_]['playInfo']['attackPoint']
                most_damagepoint += resp['matches']['rows'][_]['playInfo']['damagePoint']
                most_battlepoint += resp['matches']['rows'][_]['playInfo']['battlePoint']
                most_sightpoint += resp['matches']['rows'][_]['playInfo']['sightPoint']
                most_getCoin += resp['matches']['rows'][_]['playInfo']['getCoin']
    except IndexError:
        pass

    groups = {
        '헬리오스 소속': ['로라스', '타라', '드렉슬러', '앨리셔', '다이무스', '마를렌', '윌라드', '호타루', '자네트', '드니스', '루시', '에바'],
        '지하연합 소속': ['휴톤', '루이스', '트리비아', '도일', '토마스', '나이오비', '이글', '레이튼', '피터', '레베카', '엘리', '티모시'],
        '무소속': ['카인', '시바', '빅터', '트릭시', '히카르도', '제이', '릭', '라이샌더', '루드빅', '클리브', '론', '레오노르', '카로슈', '에밀리', '이사벨'],
        '불명': ['카를로스'],
        '전 안타리우스 소속': ['레나'],
        '미 육군': ['웨슬리'],
        '안타리우스 소속': ['스텔라', '아이작', '제키엘', '헬레나', '시드니', '플로리안'],
        '저스티스 리그 소속': ['클레어', '파수꾼 A', '케니스'],
        '헬리오스': ['샬럿'],
        '어둠의 능력자 소속': ['미쉘', '까미유', '미아', '탄야'],
        '그랑플람 재단 소속': ['마틴', '브루스', '티엔', '하랑', '테이'],
        '검의 형제 기사단 소속': ['제레온', '벨져'],
        '더 호라이즌 소속': ['리첼', '리사', '캐럴', '멜빈', '라이언'],
        '드로스트 가문': ['린', '디아나', '엘프리데', '티샤']
    }

    for k, v in groups.items():
        if most_character in v:
            group = k

    most_kda = (most_killcount / most_count + most_assistcount / most_count) / (most_deathcount / most_count)
    print("*** 모스트 캐릭터 ***")
    print(f'만약 {username}님이 사이퍼즈 캐릭터였다면, {group}의 {most_character}(이)였을 거예요.')
    print(f'평균 레벨: {int(most_level / most_count)}')
    print(f'평균 킬/데스/어시: {int(most_killcount / most_count)}/{int(most_deathcount / most_count)}/{int(most_assistcount / most_count)} (KDA: {str(round(most_kda, 2))})')
    print(f'평균 공격량: {int(most_attackpoint / most_count)}')
    print(f'평균 피해량: {int(most_damagepoint / most_count)}')
    print(f'평균 전투참여: {int(most_battlepoint / most_count)}')
    print(f'평균 시야점수: {int(most_sightpoint / most_count)}')
    print(f'평균 코인량: {int(most_getCoin / most_count)}')

    character_winrate = {}
    try:
        for _ in range(0, 100):
            if resp['matches']['rows'][_]['playInfo']['characterName'] not in character_winrate:
                character_winrate[resp['matches']['rows'][_]['playInfo']['characterName']] = [0, 0]
                if resp['matches']['rows'][_]['playInfo']['result'] == 'win':
                    character_winrate[resp['matches']['rows'][_]['playInfo']['characterName']][0] += 1
                else:
                    character_winrate[resp['matches']['rows'][_]['playInfo']['characterName']][1] += 1
            else:
                if resp['matches']['rows'][_]['playInfo']['result'] == 'win':
                    character_winrate[resp['matches']['rows'][_]['playInfo']['characterName']][0] += 1
                else:
                    character_winrate[resp['matches']['rows'][_]['playInfo']['characterName']][1] += 1
    except IndexError:
        pass

    try:
        for _ in range(0, 100):
            character_winrate[list(character_winrate)[_]].append(round(character_winrate[list(character_winrate)[_]][0] / (character_winrate[list(character_winrate)[_]][0] + character_winrate[list(character_winrate)[_]][1]), 2))
    except IndexError:
        pass

    print("")
    print("*** 캐릭터 승률 ***")
    print("3판 이상 플레이한 캐릭터만 표시됩니다.")
    global filtered_dic, sorted_filtered_dic
    filtered_dic = {k: v for k, v in character_winrate.items() if v[0] + v[1] >= 3}
    sorted_filtered_dic = sorted(filtered_dic.items(), key=lambda x: x[1][2], reverse=True)
    for k, v in sorted_filtered_dic:
        print(k + ':', str(int(v[2] * 100)) + '%', '(' + str(v[0]) + '승', str(v[1]) + '패' + ')')


def winrate_per_date():
    date_list = {}
    try:
        for _ in range(0, 100):
            date = resp['matches']['rows'][_]['date'][:10]
            if date not in date_list:
                date_list[date] = [0, 0]
                if resp['matches']['rows'][_]['playInfo']['result'] == 'win':
                    date_list[date][0] += 1
                else:
                    date_list[date][1] += 1
            else:
                if resp['matches']['rows'][_]['playInfo']['result'] == 'win':
                    date_list[date][0] += 1
                else:
                    date_list[date][1] += 1
    except IndexError:
        pass

    try:
        for _ in range(0, 100):
            date_list[list(date_list)[_]].append(round(date_list[list(date_list)[_]][0] / (date_list[list(date_list)[_]][0] + date_list[list(date_list)[_]][1]), 2))
    except IndexError:
        pass

    print("")
    print("*** 날짜별 승률 ***")
    print("최근 7일 전적을 불러옵니다.")
    sorted_date_dic = sorted(date_list.items(), key=lambda x: x)
    sorted_date_dic = sorted_date_dic[-7:]
    for k, v in sorted_date_dic:
        print(k + ':', str(int(v[2] * 100)) + '%', '(' + str(v[0]) + '승', str(v[1]) + '패' + ')')
    if len(sorted_date_dic) == 1:
        print("승률을 분석하기에는 전적이 부족합니다.")
    else:
        data = pd.DataFrame(sorted_date_dic)
        data[0] = pd.to_datetime(data[0])
        data[0] = data[0].map(dt.datetime.toordinal)

        pd.options.mode.chained_assignment = None
        for i in range(len(sorted_date_dic)):
            data[1][i] = data[1][i][2]

        x = data.iloc[:, 0]
        y = data.iloc[:, 1]
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        num = 0
        den = 0
        for i in range(len(x)):
            num += (x[i] - x_mean) * (y[i] - y_mean)
            den += (x[i] - x_mean) ** 2
        m = num / den

        if m < 0:
            if filtered_dic == {}:
                print(f"승률이 하락하고 있습니다. {username}님의 모스트 '{most_character}'(으)로 플레이해보는 것은 어떨까요?")
            elif most_character == list(sorted_filtered_dic[0])[0]:
                print(f"승률이 하락하고 있습니다. {username}님의 모스트 '{most_character}'(으)로 플레이해보는 것은 어떨까요?")
            else:
                print(f"승률이 하락하고 있습니다. {username}님의 모스트 '{most_character}'이나 최근 승률이 좋은 '{list(sorted_filtered_dic[0])[0]}'(으)로 플레이해보는 것은 어떨까요?")
        else:
            print("승률이 상승하고 있습니다. 연승을 기원합니다!")

if __name__ == "__main__":
    get_playerid(user := input("닉네임을 입력하세요: "))
    analyze_pvplog(gametype := input("공식/일반: "))
    print_playerinfo(playerid)
    print_pvplog()
    top_character()
    winrate_per_date()
