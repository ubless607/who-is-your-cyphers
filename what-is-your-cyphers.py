import json
import requests
import datetime as dt
from collections import Counter

def get_playerid() :
    global user
    user = input("닉네임을 입력하세요: ")
    url = "https://api.neople.co.kr/cy/players?nickname=" + user + "&wordType=<wordType>&apikey=RvYjrC3nMgBprP2Z7KmPsfSGEikysfhW"
    url_json = requests.get(url).json()
    playerid = (url_json['rows'][0]['playerId'])
    return playerid

username = get_playerid()


def get_characterStatistics(username) :
    now = dt.datetime.now()
    nowDatetime = dt.datetime.strftime(now, "%Y-%m-%d %H:%M")
    past = now - dt.timedelta(days=30)
    pastDatetime = dt.datetime.strftime(past, "%Y-%m-%d %H:%M")

    gametype = input("공식/일반: ")
    if (gametype == "공식") :
        url = "https://api.neople.co.kr/cy/players/" + username + "/matches?gameTypeId=rating&startDate=" + str(pastDatetime) + "&endDate=" + str(nowDatetime) + "&limit=100&apikey=RvYjrC3nMgBprP2Z7KmPsfSGEikysfhW"
    else:
        url = "https://api.neople.co.kr/cy/players/" + username + "/matches?gameTypeId=normal&startDate=" + str(pastDatetime) + "&endDate=" + str(nowDatetime) + "&limit=100&apikey=RvYjrC3nMgBprP2Z7KmPsfSGEikysfhW"
    dict = requests.get(url).json()
    character_list = []

    try:
        for i in range (0, 100):    
            character_list.append(dict['matches']['rows'][i]['playInfo']['characterName'])
    except IndexError:
        pass

    character_list = Counter(character_list)
    print("** 선호 캐릭터 TOP6 **")
    character_list2 = character_list.most_common(6)
    for k,v in character_list2 :
        print(k,':',v)
    print("")

    global most
    most = character_list.most_common(1)[0][0]
    most2 = character_list.most_common(1)[0][1]

    most_level,most_killCount,most_deathCount,most_assistCount, most_attackPoint,most_damagePoint, most_battlePoint,most_sightPoint,most_KDA  = 0, 0 ,0 ,0, 0 ,0, 0,0, 0

    try:
        for i in range (0, 100):
            if dict['matches']['rows'][i]['playInfo']['characterName'] == most :
                most_level += dict['matches']['rows'][i]['playInfo']['level']
                most_killCount += dict['matches']['rows'][i]['playInfo']['killCount']
                most_deathCount += dict['matches']['rows'][i]['playInfo']['deathCount']
                most_assistCount += dict['matches']['rows'][i]['playInfo']['assistCount']
                most_attackPoint += dict['matches']['rows'][i]['playInfo']['attackPoint']
                most_damagePoint += dict['matches']['rows'][i]['playInfo']['damagePoint']
                most_battlePoint+= dict['matches']['rows'][i]['playInfo']['battlePoint']
                most_sightPoint+= dict['matches']['rows'][i]['playInfo']['sightPoint']
    except IndexError:
        pass

    if most == '로라스' :
        group = '헬리오스'
    elif most == '휴톤' :
        group = '지하연합'
    elif most == '루이스' :
        group = '지하연합'
    elif most == '타라' :
        group = '헬리오스'
    elif most == '트리비아' :
        group = '지하연합'
    elif most == '카인' :
        group = '무소속'
    elif most == '레나' :
        group = '전 안타리우스'
    elif most == '드렉슬러' :
        group = '헬리오스'
    elif most == '도일' :
        group = '지하연합'
    elif most == '토마스' :
        group = '지하연합'
    elif most == '나이오비' :
        group = '지하연합'
    elif most == '시바' :
        group = '무소속'
    elif most == '웨슬리' :
        group = '미 육군'
    elif most == '스텔라' :
        group = '안타리우스'
    elif most == '앨리셔' :
        group = '헬리오스'
    elif most == '클레어' :
        group = '저스티스 리그'
    elif most == '다이무스' :
        group = '헬리오스'
    elif most == '이글' :
        group = '지하연합'
    elif most == '마를렌' :
        group = '헬리오스'
    elif most == '샬럿' :
        group = '헬리오스?'
    elif most == '윌라드' :
        group = '헬리오스'
    elif most == '레이튼' :
        group = '지하연합'
    elif most == '미쉘' :
        group = '어둠의 능력자'
    elif most == '린' :
        group = '드로스트 가문'
    elif most == '빅터' :
        group = '무소속'
    elif most == '카를로스' :
        group = '불명'
    elif most == '호타루' :
        group = '헬리오스'
    elif most == '트릭시' :
        group = '무소속'
    elif most == '히카르도' :
        group = '무소속'
    elif most == '까미유' :
        group = '어둠의 능력자'
    elif most == '자네트' :
        group = '헬리오스'
    elif most == '피터' :
        group = '지하연합'
    elif most == '아이작' :
        group = '안타리우스'
    elif most == '레베카' :
        group = '지하연합'
    elif most == '엘리' :
        group = '지하연합'
    elif most == '마틴' :
        group = '그랑플람 재단'
    elif most == '브루스' :
        group = '그랑플람 재단'
    elif most == '미아' :
        group = '어둠의 능력자'
    elif most == '드니스':
        group = '헬리오스'
    elif most == '제레온' :
        group = '검의 형제 기사단'
    elif most == '루시' :
        group = '헬리오스'
    elif most == '티엔' :
        group = '그랑플람 재단'
    elif most == '하랑' :
        group = '그랑플람 재단'
    elif most == 'J' :
        group = '무소속'
    elif most == '벨져' :
        group = '검의 형제 기사단'
    elif most == '리첼' :
        group = '더 호라이즌'
    elif most == '리사' :
        group = '더 호라이즌'
    elif most == '릭' :
        group = '무소속'
    elif most == '제키엘' :
        group = '안타리우스'
    elif most == '탄야' :
        group = '어둠의 능력자'
    elif most == '캐럴' :
        group = '더 호라이즌'
    elif most == '라이샌더' :
        group = '무소속'
    elif most == '루드빅' :
        group = '무소속'
    elif most == '멜빈' :
        group = '더 호라이즌'
    elif most == '디아나' :
        group = '드로스트 가문'
    elif most == '클리브' :
        group = '무소속'
    elif most == '헬레나' :
        group = '안타리우스'
    elif most == '에바' :
        group = '헬리오스'
    elif most == '론' :
        group = '무소속'
    elif most == '레오노르' :
        group = '무소속'
    elif most == '시드니' :
        group = '안타리우스'
    elif most == '테이' :
        group = '그랑플람 제단'
    elif most == '티모시' :
        group = '지하연합'
    elif most == '엘프리데' :
        group = '무소속'
    print("** %s님이 만약 사이퍼즈 속 캐릭터라면, %s의 %s(이)였을 거예요. **" % (user, group, most))
    print("평균레벨 : %d" % int(most_level/most2))
    print("평균 킬/데스/어시: %d/%d/%d" % (int(most_killCount/most2), int(most_deathCount/most2),int(most_assistCount/most2)))
    print("평균 공격량: %d" % int(most_attackPoint/most2))
    print("평균 피해량: %d" % int(most_damagePoint/most2))
    print("평균 전투참여: %d" % int(most_battlePoint/most2))
    print("평균 시야점수: %d" % int(most_sightPoint/most2))
    most_KDA = (most_killCount/most2 + most_assistCount/most2) / (most_deathCount/most2)
    print(str("평균 KDA: ") + str(round(most_KDA, 2)))

    character_list3 = {}

    try:
        for i in range (0, 100):    
            if dict['matches']['rows'][i]['playInfo']['characterName'] not in character_list3:
                character_list3[dict['matches']['rows'][i]['playInfo']['characterName']] = [0, 0]
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win' :
                    character_list3[dict['matches']['rows'][i]['playInfo']['characterName']][0] += 1
                else :
                    character_list3[dict['matches']['rows'][i]['playInfo']['characterName']][1] += 1
            else :
                if dict['matches']['rows'][i]['playInfo']['result'] == 'win' :
                    character_list3[dict['matches']['rows'][i]['playInfo']['characterName']][0] += 1
                else :
                    character_list3[dict['matches']['rows'][i]['playInfo']['characterName']][1] += 1		
    except IndexError:
        pass

    try:
        for i in range (0, 100):
            character_list3[list(character_list3)[i]].append(round(character_list3[list(character_list3)[i]][0] / (character_list3[list(character_list3)[i]][0]+character_list3[list(character_list3)[i]][1]),2))
    except IndexError:
        pass

    print("")
    print("** 캐릭터 승률(4판 이상 플레이한 캐릭터만 표시) **")
    filtered_dic = {k:v for k,v in character_list3.items() if v[0]+v[1] >= 4}
    sorted_filtered_dic = sorted(filtered_dic.items(), key=lambda x: x[1][2], reverse=True)
    for k,v in sorted_filtered_dic :
        print(k,':',v) 
    
get_characterStatistics(username)

