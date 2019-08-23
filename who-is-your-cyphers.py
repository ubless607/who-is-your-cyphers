# coding=utf-8

# 슬기로운 사퍼생활 : 당신의 사이퍼즈 취향을 분석해 드립니다 by ubless607
# https://github.com/ubless607/flask-who-is-your-cyphers

import datetime as dt
import os
import json
import time as tm
from collections import Counter

import config
import numpy as np
import pandas as pd
import aiohttp
import asyncio
import requests
from pytz import timezone


def get_playerstatistics(user):
    try:
        user = user.upper()
        url = "https://api.neople.co.kr/cy/players?nickname=" + user + "&apikey=" + config.key
        dict = requests.get(url).json()
        playerid = (dict['rows'][0]['playerId'])
    except IndexError:
        print("닉네임이 존재하지 않습니다.")
        os._exit(1)
    except requests.exceptions.RequestException:
        print("서버가 응답하지 않습니다.")
        os._exit(1)

    now = dt.datetime.now(timezone('Asia/Seoul'))
    now_time = dt.datetime.strftime(now, "%Y-%m-%d %H:%M")
    past = now - dt.timedelta(days=90)
    past_time = dt.datetime.strftime(past, "%Y-%m-%d %H:%M")

    gametype = input("공식/일반: ")
    try:
        if gametype == "공식":
            url = "https://api.neople.co.kr/cy/players/" + playerid + "/matches?gameTypeId=rating&startDate=" + str(past_time) + "&endDate=" + str(now_time) + "&limit=100&apikey=" + config.key
        else:
            url = "https://api.neople.co.kr/cy/players/" + playerid + "/matches?gameTypeId=normal&startDate=" + str(past_time) + "&endDate=" + str(now_time) + "&limit=100&apikey=" + config.key
        dict = requests.get(url).json()

        url = "https://api.neople.co.kr/cy/players/" + playerid + "?apikey=" + config.key
        dict2 = requests.get(url).json()
    except requests.exceptions.RequestException:
        print("서버가 응답하지 않습니다.")
        os._exit(1)

    print("")
    print("** %s님의 프로필 **" % user)
    print("급수: %s" % dict2['grade'])
    if dict2['ratingPoint'] is None:
        print("티어: Unranked")
    else:
        print("티어: %s (%s)" % (dict2['ratingPoint'], dict2['tierName']))

    ch_list = []
    try:
        for i in range(0, 100):
            ch_list.append(dict['matches']['rows'][i]['playInfo']['characterName'])
    except IndexError:
        pass
    if not ch_list:
        print("전적이 존재하지 않습니다.")
        os._exit(1)

    time_count = []
    try:
        for i in range(0, 100):
            time = dict['matches']['rows'][i]['date'][11:13]
            time_count.append(time)
    except IndexError:
        pass
    time_count = Counter(time_count).most_common(1)

    party_count = []
    try:
        for i in range(0, 100):
            count = dict['matches']['rows'][i]['playInfo']['partyUserCount']
            party_count.append(count)
    except IndexError:
        pass
    party_count = Counter(party_count).most_common(1)

    matchid_list = []
    try:
        for i in range(0, 50):
            count = dict['matches']['rows'][i]['matchId']
            matchid_list.append(count)
    except IndexError:
        pass
    matchid_list2 = []
    try:
        for i in range(50, 100):
            count = dict['matches']['rows'][i]['matchId']
            matchid_list2.append(count)
    except IndexError:
        pass

    position_count = []
    async def fetch(client, matchid):
        async with client.get('https://api.neople.co.kr/cy/matches/' + matchid + '?apikey=' + config.key) as resp:
            if resp.status == 400:
                print("서버가 응답하지 않습니다.")
                os._exit(1)
            assert resp.status == 200
            return await resp.text()
    async def get_position(matchid):
        async with aiohttp.ClientSession() as client:
            temp_dict = await fetch(client, matchid)
            temp_dict = json.loads(temp_dict)
            try:
                for i in range(0, 10):
                    if user == temp_dict['players'][i]['nickname']:
                        count = temp_dict['players'][i]['position']['name']
                        position_count.append(count)
            except IndexError:
                pass

    task1 = [get_position(matchid) for matchid in matchid_list]
    asyncio.run(asyncio.wait(task1))
    if not matchid_list2 == []:
        tm.sleep(1)
        task2 = [get_position(matchid) for matchid in matchid_list2]
        asyncio.run(asyncio.wait(task2))
    position_count2 = Counter(position_count).most_common()

    print("")
    print("** 플레이 스타일 **")
    if party_count[0][0] == 0:
        print("솔로 플레이어")
    else:
        print(str(party_count[0][0]) + "인 파티 유저")
    print('게임 시간대:', time_count[0][0] + '시')
    print('선호 포지션:', Counter(position_count).most_common(1)[0][0])
    position = []
    for k, v in position_count2:
        count = " ".join([k + ':', str(round(v / len(position_count) * 100, 1)) + '%'])
        position.append(count)
    print("[%s]" % (', '.join(position)))

    ch_list = Counter(ch_list)
    ch_list2 = ch_list.most_common(7)

    key_list = [key for key, _ in ch_list2]
    value_list = [key for _, key in ch_list2]
    most_list = []

    for i in range(len(key_list)):
        killcount, deathcount, assistcount = 0, 0, 0
        try:
            for j in range(0, 100):
                if dict['matches']['rows'][j]['playInfo']['characterName'] == key_list[i]:
                    killcount += dict['matches']['rows'][j]['playInfo']['killCount']
                    deathcount += dict['matches']['rows'][j]['playInfo']['deathCount']
                    assistcount += dict['matches']['rows'][j]['playInfo']['assistCount']
        except IndexError:
            pass
        kda = str(round((killcount / value_list[i] + assistcount / value_list[i]) / (deathcount / value_list[i]), 2))
        most_list.append(kda)

    print()
    print("** 선호 캐릭터 TOP7 **")
    for i in range(len(key_list)):
        print(key_list[i] + ':', str(value_list[i])+'판', '(KDA: ' + most_list[i] + ')')
    print("")

    most = ch_list.most_common(1)[0][0]
    most_count = ch_list.most_common(1)[0][1]

    most_level, most_killcount, most_deathcount, most_assistcount, most_attackpoint, most_damagepoint, most_battlepoint, most_sightpoint, most_kda = 0, 0, 0, 0, 0, 0, 0, 0, 0

    try:
        for i in range(0, 100):
            if dict['matches']['rows'][i]['playInfo']['characterName'] == most:
                most_level += dict['matches']['rows'][i]['playInfo']['level']
                most_killcount += dict['matches']['rows'][i]['playInfo']['killCount']
                most_deathcount += dict['matches']['rows'][i]['playInfo']['deathCount']
                most_assistcount += dict['matches']['rows'][i]['playInfo']['assistCount']
                most_attackpoint += dict['matches']['rows'][i]['playInfo']['attackPoint']
                most_damagepoint += dict['matches']['rows'][i]['playInfo']['damagePoint']
                most_battlepoint += dict['matches']['rows'][i]['playInfo']['battlePoint']
                most_sightpoint += dict['matches']['rows'][i]['playInfo']['sightPoint']
    except IndexError:
        pass

    groups = {
        '헬리오스 소속': ['로라스', '타라', '드렉슬러', '앨리셔', '다이무스', '마를렌', '윌라드', '호타루', '자네트', '드니스', '루시', '에바'],
        '지하연합 소속': ['휴톤', '루이스', '트리비아', '도일', '토마스', '나이오비', '이글', '레이튼', '피터', '레베카', '엘리', '티모시'],
        '무소속': ['카인', '시바', '빅터', '트릭시', '히카르도', '제이', '릭', '라이샌더', '루드빅', '클리브', '론', '레오노르'],
        '불명': ['카를로스'],
        '전 안타리우스 소속': ['레나'],
        '미 육군': ['웨슬리'],
        '안타리우스 소속': ['스텔라', '아이작', '제키엘', '헬레나', '시드니'],
        '저스티스 리그 소속': ['클레어'],
        '헬리오스': ['샬럿'],
        '어둠의 능력자 소속': ['미쉘', '까미유', '미아', '탄야'],
        '그랑플람 재단 소속': ['마틴', '브루스', '티엔', '하랑', '테이'],
        '검의 형제 기사단 소속': ['제레온', '벨져'],
        '더 호라이즌 소속': ['리첼', '리사', '캐럴', '멜빈'],
        '드로스트 가문': ['린', '디아나', '엘프리데']
    }

    for k, v in groups.items():
        if most in v:
            group = k

    print("** 모스트 캐릭터 **")
    print("만약 %s님이 사이퍼즈 캐릭터였다면, %s의 %s(이)였을 거예요." % (user, group, most))
    print("평균 레벨: %d" % int(most_level / most_count))
    print("평균 킬/데스/어시: %d/%d/%d" % (int(most_killcount / most_count), int(most_deathcount / most_count), int(most_assistcount / most_count)))
    print("평균 공격량: %d" % int(most_attackpoint / most_count))
    print("평균 피해량: %d" % int(most_damagepoint / most_count))
    print("평균 전투참여: %d" % int(most_battlepoint / most_count))
    print("평균 시야점수: %d" % int(most_sightpoint / most_count))
    most_kda = (most_killcount / most_count + most_assistcount / most_count) / (most_deathcount / most_count)
    print(str("평균 KDA: ") + str(round(most_kda, 2)))

    ch_list3 = {}
    try:
        for i in range(0, 100):
            if dict['matches']['rows'][i]['playInfo']['characterName'] not in ch_list3:
                ch_list3[dict['matches']['rows'][i]['playInfo']['characterName']] = [0, 0]
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win':
                    ch_list3[dict['matches']['rows'][i]['playInfo']['characterName']][0] += 1
                else:
                    ch_list3[dict['matches']['rows'][i]['playInfo']['characterName']][1] += 1
            else:
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win':
                    ch_list3[dict['matches']['rows'][i]['playInfo']['characterName']][0] += 1
                else:
                    ch_list3[dict['matches']['rows'][i]['playInfo']['characterName']][1] += 1
    except IndexError:
        pass

    try:
        for i in range(0, 100):
            ch_list3[list(ch_list3)[i]].append(round(
                ch_list3[list(ch_list3)[i]][0] / (ch_list3[list(ch_list3)[i]][0] + ch_list3[list(ch_list3)[i]][1]), 2))
    except IndexError:
        pass

    print("")
    print("** 캐릭터 승률 **")
    print("3판 이상 플레이한 캐릭터만 표시됩니다.")
    filtered_dic = {k: v for k, v in ch_list3.items() if v[0] + v[1] >= 3}
    sorted_filtered_dic = sorted(filtered_dic.items(), key=lambda x: x[1][2], reverse=True)
    for k, v in sorted_filtered_dic:
        print(k + ':', str(int(v[2] * 100)) + '%', '(' + str(v[0]) + '승', str(v[1]) + '패' + ')')

    date_list = {}
    try:
        for i in range(0, 100):
            date = dict['matches']['rows'][i]['date'][:10]
            if date not in date_list:
                date_list[date] = [0, 0]
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win':
                    date_list[date][0] += 1
                else:
                    date_list[date][1] += 1
            else:
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win':
                    date_list[date][0] += 1
                else:
                    date_list[date][1] += 1
    except IndexError:
        pass

    try:
        for i in range(0, 100):
            date_list[list(date_list)[i]].append(round(date_list[list(date_list)[i]][0] / (date_list[list(date_list)[i]][0] + date_list[list(date_list)[i]][1]), 2))
    except IndexError:
        pass

    print("")
    print("** 날짜별 승률 **")
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
                print("승률이 하락하고 있습니다. %s님의 모스트 '%s'(으)로 플레이해보는 것은 어떨까요?" % (user, most))
            elif most == list(sorted_filtered_dic[0])[0]:
                print("승률이 하락하고 있습니다. %s님의 모스트 '%s'(으)로 플레이해보는 것은 어떨까요?" % (user, most))
            else:
                print("승률이 하락하고 있습니다. %s님의 모스트 '%s'이나 최근 승률이 좋은 '%s'(으)로 플레이해보는 것은 어떨까요?" % (user, most, list(sorted_filtered_dic[0])[0]))
        else:
            print("승률이 상승하고 있습니다. 잘하고 있어요!")


user = input("닉네임을 입력하세요: ")
get_playerstatistics(user)
