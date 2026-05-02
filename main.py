import pickle
import os
import sys

# -----------------------------------------------------------
# 1. Map Data
# 2차원 리스트를 통해 캠퍼스 맵 구현
# 인덱스: Map[y][x] -> x=열(동서), y=행(남북)
# None -> 이동 불가 공간
# -----------------------------------------------------------
Map = [
    ["종합관", "본관", "경영관", "노천극장", "새천년관", "이윤재관"],
    ["백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC"],
    ["중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학"],
    ["체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스"],
    ["공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None],
    ["공학원", "백양로1", "공터1", "암병원", "의과대학", None],
    ["연대앞 버스정류장", "정문", "스타벅스", "세브란스 버스정류장", None, None]
]

# -----------------------------------------------------------
# 2. Classes
# -----------------------------------------------------------

#임무 이름 & 설명 담는 데이터 클래스
class Quest:
    def __init__(self, name, description):
        self.name = name
        self.description = description

# 맵 안 각 장소의 좌표, 상점, 임무 등의 정보를 관리하는 클래스
class Place:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.buy_items = {}
        self.sell_items = {}
        self.event_info = None

    # 해당 장소에서 가능한 상호작용 명령어 목록 반환
    def get_interactions(self):
        interactions = []
        if self.buy_items:
            interactions.append("구매")
        if self.sell_items:
            interactions.append("판매")
        if self.name in ["정문", "독수리상", "본관", "세브란스", "이윤재관"]:
            interactions.append("임무")
        return interactions

# 플레이어 상태, 위치, 행동 관리하는 클래스
class Player:
    def __init__(self, places, start_place_name):
        self.places = places
        self.location = places[start_place_name]
        self.hp = 10.0
        self.balance = 10000
        self.inventory = {"두쫀쿠": 0, "카페라떼": 0}
        self.quests = []
        self.completed_quests = set()
        self.difficulty = "보통"
        self.history = []
        self.event_answers = {}

    # 사용자에게 입력을 받으면 입력 내용을 history에 기록한 뒤 반환
    def get_input(self, prompt_text="입력: "):
        val = input(prompt_text)
        self.history.append(val)
        return val

    # 현재 위치에서 동서남북(dx, dy) 방향에 있는 장소 이름 반환
    def get_neighbor(self, dx, dy):
        nx, ny = self.location.x + dx, self.location.y + dy
        if 0 <= ny < len(Map) and 0 <= nx < len(Map[ny]):
            name = Map[ny][nx]
            if name:
                return name
        return "막힘"

    # 현재 상태(계좌 잔액, HP, 현재위치, 인접 장소) 출력
    def print_status(self):
        print(f"계좌의 잔액 = {self.balance:,}원")
        print(f"HP = {self.hp:g}")
        print(f"현재위치 = {self.location.name}")
        east = self.get_neighbor(1, 0)
        west = self.get_neighbor(-1, 0)
        south = self.get_neighbor(0, 1)
        north = self.get_neighbor(0, -1)
        print(f"동서남북 = {east}, {west}, {south}, {north}")

    # 입력된 방향(동/서/남/북)으로 이동 - 이동 시 HP 차감
    def move(self, direction):
        dx, dy = 0, 0
        if direction == "동": dx = 1
        elif direction == "서": dx = -1
        elif direction == "남": dy = 1
        elif direction == "북": dy = -1

        nx, ny = self.location.x + dx, self.location.y + dy
        if 0 <= ny < len(Map) and 0 <= nx < len(Map[ny]):
            new_place_name = Map[ny][nx]
            if new_place_name:
                # 난이도에 따른 HP 차감
                loss = 1.0
                if self.difficulty == "어려움": loss = 2.0
                self.hp -= loss
                # hp가 0이 되면 게임 종료(sys.exit -> 프로그램 종료 코드)
                if self.hp<=0:
                    print("게임 오버!")
                    sys.exit(0)

                # 위치 이동
                self.location = self.places[new_place_name]

                #해당 위치에서 가능한 상호작용 목록
                interacts = self.location.get_interactions()
                inter_text = ""
                if len(interacts) > 0:
                    inter_text = f" [{', '.join(interacts)}]"
                print(f"{self.location.name}으로 이동했다.{inter_text}")

                if self.location.event_info:
                    print(self.location.event_info)
                return

        print("선택한 방향으로 이동할 수 없습니다")

    # 인벤토리 열기 및 보유한 아이템 출력
    def open_bag(self):
        print("가방 내용물:")
        items = list(self.inventory.keys())
        for i, name in enumerate(items, 1):
            print(f"{i}) {name} {self.inventory[name]}개")

        # 인벤토리 속 아이템 사용
        val = self.get_input("사용할 물건의 번호나 이름을 입력하세요 (취소: 0): ")
        if val == "0":
            return

        selected_item = None
        if val.isdigit() and 1 <= int(val) <= len(items):
            selected_item = items[int(val)-1]
        elif val in items:
            selected_item = val

        if selected_item:
            if self.inventory[selected_item] > 0:
                self.inventory[selected_item] -= 1
                if selected_item == "두쫀쿠": self.hp += 10
                elif selected_item == "카페라떼": self.hp += 5
                print(f"{selected_item}을(를) 사용했습니다. HP가 증가했습니다. (현재 HP: {self.hp:g})")
            else:
                print("보유하고 있지 않습니다.")
        else:
            print("잘못된 선택입니다.")

    # 현재 위치에서 아이템 구매
    def buy(self):
        if not self.location.buy_items:
            print("여기서는 구매할 수 없습니다.")
            return

        items = list(self.location.buy_items.keys())
        while True:
            # 구매 가능한 아이템 목록 출력
            for i, name in enumerate(items, 1):
                price = self.location.buy_items[name]
                hp_up = 10 if name == "두쫀쿠" else 5
                print(f"{i}) {name}: {price}원, HP가 {hp_up}만큼 증가한다.")
            print(f"{len(items)+1}) 종료")

            val = self.get_input("입력: ")
            if val.isdigit():
                idx = int(val)
                if idx == len(items) + 1:
                    break
                elif 1 <= idx <= len(items):
                    item_name = items[idx-1]
                    price = self.location.buy_items[item_name]
                    if self.balance >= price:
                        self.balance -= price
                        self.inventory[item_name] += 1
                        print(f"{item_name}을(를) 구매해서 가방에 넣었다. 계좌 잔액 = {self.balance:,}원")
                    else:
                        print("잔액이 부족합니다.")
                else:
                    print("잘못된 선택입니다.")
            else:
                print("잘못된 선택입니다.")

    # 현재 위치에서 보유한 아이템 판매
    def sell(self):
        if not self.location.sell_items:
            print("여기서는 판매할 수 없습니다.")
            return

        items = list(self.location.sell_items.keys())
        while True:
            # 판매 가능한 아이템 목록 출력
            for i, name in enumerate(items, 1):
                price = self.location.sell_items[name]
                print(f"{i}) {name}: {price}원에 판매")
            print(f"{len(items)+1}) 종료")

            val = self.get_input("입력: ")
            if val.isdigit():
                idx = int(val)
                if idx == len(items) + 1:
                    break
                elif 1 <= idx <= len(items):
                    item_name = items[idx-1]
                    price = self.location.sell_items[item_name]
                    if self.inventory[item_name] > 0:
                        self.inventory[item_name] -= 1
                        self.balance += price
                        print(f"{item_name}을(를) 판매했습니다. 계좌 잔액 = {self.balance:,}원")
                    else:
                        print("보유하고 있지 않습니다.")
                else:
                    print("잘못된 선택입니다.")
            else:
                print("잘못된 선택입니다.")

    # 현재 위치에 맞는 퀘스트 이벤트 처리
    def handle_quest_interaction(self):
        loc = self.location.name
        # - 정문: 독수리상 방문 퀘스트 부여
        if loc == "정문":
            print("학교에서 어떤 일들이 일어나고있는지 소식들이 모이는 독수리상에서 알아보자.")

            has_quest=False

            for q in self.quests:
                if q.name == "독수리상 방문":
                    has_quest = True
                    break

            if has_quest == False and "독수리상 방문" not in self.completed_quests:
                self.quests.append(Quest("독수리상 방문", "독수리상에서 소식을 알아보자."))
                print("[임무목록]에 임무가 추가되었습니다.")

        # - 독수리상: 독수리상 방문 완료 후 2개의 수사 퀘스트 부여
        elif loc == "독수리상":
            for q in self.quests:
                if q.name == "독수리상 방문":
                    self.quests.remove(q)
                    self.completed_quests.add("독수리상 방문")
                    break
            
            new_quests = [
                Quest("교내 부조리 수사", "부조리를 찾아서 본관에 보고하라."),
                Quest("교내 위생사건 수사", "위생사건의 원인을 찾아서 세브란스에 보고하라.")
            ]
            added = False
            for nq in new_quests:
                already_has_quest = False
                for q in self.quests:
                    if q.name == nq.name:
                        already_has_quest = True  
                        break

                if already_has_quest == False and nq.name not in self.completed_quests:
                    self.quests.append(nq)
                    added = True
                    
            if added:
                print("[임무목록]에 임무가 추가되었습니다.")
        
        # - 본관: 부조리 수사 퀘스트 정답 제출
        elif loc == "본관":
            target_quest = None
            
            for q in self.quests:
                if q.name == "교내 부조리 수사":
                    target_quest = q  
                    break            

            if target_quest:
                ans = self.get_input("교내 어디에 부조리가 있나? (답을 입력하면 해결): ")
                if ans == self.event_answers.get("교내 부조리 수사", "") and ans != "":
                    print("해결후: 수업들으러 이윤재관 가야지!")
                    self.quests.remove(target_quest) 
                    self.completed_quests.add("교내 부조리 수사")
                else:
                    print("답이 틀렸습니다.")
            else:
                print("현재 해결할 부조리 수사 임무가 없습니다.")

        # - 세브란스: 위생사건 수사 퀘스트 정답 제출
        elif loc == "세브란스":
            target_quest = None
            
            for q in self.quests:
                if q.name == "교내 위생사건 수사":
                    target_quest = q  
                    break    
                    
            if target_quest:
                ans = self.get_input("교내 어디에 식중독 원인이 있나? (답을 입력하면 해결): ")
                if ans == self.event_answers.get("교내 위생사건 수사", "") and ans != "":
                    print("해결후: 수업들으러 이윤재관 가야지!")
                    self.quests.remove(target_quest) 
                    self.completed_quests.add("교내 위생사건 수사")
                else:
                    print("답이 틀렸습니다.")
            else:
                print("현재 해결할 위생사건 수사 임무가 없습니다.")

        # - 이윤재관: 두 수사 퀘스트를 완료했을 시 게임 클리어
        elif loc == "이윤재관":
            q1 = "교내 부조리 수사" in self.completed_quests
            q2 = "교내 위생사건 수사" in self.completed_quests
            
            if q1 and q2:
                print("부조리와 식중독 수사를 완료했구나! 수업은 이걸로 끝입니다. 또 만나요~")
                sys.exit(0)
            elif q1:
                print("부조리 수사를 완료했구나! 식중독 원인도 찾아주세요~")
            elif q2:
                print("식중독 수사를 완료했구나! 부조리도 찾아주세요~")
            else:
                print("독수리상에서 임무를 받아오거나 해결하고 오세요.")

    # 현재 진행 중인 임무 목록을 출력
    def show_quests(self):
        if not self.quests:
            print("현재 진행 중인 임무가 없습니다.")
        else:
            print("[임무목록]")
            for q in self.quests:
                print(f"- {q.name}: {q.description}")

    # 게임 난이도 변경
    def change_difficulty(self):
        print(f"현재 난이도는 {self.difficulty}입니다.")
        val = self.get_input("변경할 난이도를 입력하세요 (쉬움, 보통, 어려움): ")
        if val in ["쉬움", "보통", "어려움"]:
            self.difficulty = val
            print(f"난이도가 {val}(으)로 변경되었습니다.")
        else:
            print("잘못된 입력입니다.")

# -----------------------------------------------------------
# 3. 게임 실행 설정 & File I/O
# -----------------------------------------------------------

# Map 배열을 순회하여 모든 Place 객체를 생성하고, 각 장소에 구매/판매 아이템과 사건 정보를 설정한 뒤 딕셔너리로 반환. events.pkl이 있으면 사건 정보와 퀘스트 정답도 함께 로드
def init_map():
    places = {}
    for y, row in enumerate(Map):
        for x, name in enumerate(row):
            if name:
                p = Place(name, x, y)

                # 구매 가격 맵
                if name in ["학생회관"]:
                    p.buy_items = {"두쫀쿠": 5000, "카페라떼": 3000}
                elif name in ["스타벅스", "ABMRC"]:
                    p.buy_items = {"두쫀쿠": 4000, "카페라떼": 2000}

                # 판매 가격 맵
                if name in ["체육관", "공학관", "공학원", "재활병원", "어린이병원", "종합관", "노천극장"]:
                    p.sell_items = {"두쫀쿠": 7000, "카페라떼": 4000}
                elif name in ["중앙도서관", "백양관", "대강당", "백주년기념관", "안과병원", "암병원", "새천년관", "알렌관", "제중관", "의과대학", "치과대학", "세브란스", "본관", "경영관"]:
                    p.sell_items = {"두쫀쿠": 6000, "카페라떼": 3000}

                # 사건관련정보
                if name == "중앙도서관":
                    p.event_info = "자리에 짐을 잔뜩 올려서 차지하고, 키오스크에서 배석받은 학생이 와도 비켜주지 않는 빌런"
                elif name == "공터2":
                    p.event_info = "학생회관에서 버린 음식물쓰레기가 부패하여 학생회관으로 흘러들어가고있다!"

                places[name] = p


    event_answers = {}
    try:
        with open("events.pkl", "rb") as f:
            data = pickle.load(f)
            events = data.get("events", {})
            for k, v in events.items():
                if k in places:
                    places[k].event_info = v
            event_answers = data.get("answers", {})
    except FileNotFoundError:
        pass  

    return places, event_answers

# 현재 플레이어 상태를 pickle 파일로 저장
# 저장 데이터: HP, 잔액, 위치, 인벤토리, 진행 중인 퀘스트, 완료한 퀘스트, 난이도, History
def save_game(player):
    path = player.get_input("저장할 파일명 또는 경로를 입력하세요: ")
    
    try:
        save_data = {}

        save_data["hp"] = player.hp
        save_data["balance"] = player.balance
        save_data["location_name"] = player.location.name
        save_data["inventory"] = player.inventory

        quest_list = []
        for q in player.quests:
            quest_list.append((q.name, q.description))
        save_data["quests"] = quest_list

        save_data["completed_quests"] = player.completed_quests
        save_data["difficulty"] = player.difficulty
        save_data["history"] = player.history

        f = open(path, "wb")
        pickle.dump(save_data, f)
        f.close()

        print("저장되었습니다.")

    except Exception as e:
        print("저장 실패:", e)

# pickle 파일에서 저장된 게임 상태를 불러와 플레이어 객체에 적용. 현재 폴더의 .pkl 파일 목록을 보여주고, 번호 또는 경로로 선택 가능
def load_game(player):
    print("현재 폴더의 저장된 파일 목록:")
    files = []
    for f in os.listdir('.'):
        if f.endswith('.pkl') and f != 'events.pkl':
            files.append(f)
    for i, f in enumerate(files, 1):
        print(f"{i}) {f}")
    
    path = player.get_input("불러올 파일의 번호 또는 경로를 입력하세요: ")
    
    target_path = None
    if path.isdigit() and 1 <= int(path) <= len(files):
        target_path = files[int(path)-1]
    else:
        target_path = path

    try:
        with open(target_path, "rb") as f:
            save_data = pickle.load(f)
            player.hp = save_data["hp"]
            player.balance = save_data["balance"]
            player.location = player.places[save_data["location_name"]]
            player.inventory = save_data["inventory"]
            
            player.quests = []
            for name, desc in save_data["quests"]:
                player.quests.append(Quest(name, desc))
            
            player.completed_quests = save_data["completed_quests"]
            player.difficulty = save_data["difficulty"]
            player.history = save_data["history"]
        print("성공적으로 불러왔습니다.")
    except Exception as e:
        print(f"불러오기 실패: {e}")

# -----------------------------------------------------------
# 4. 메인 게임 Loop
# -----------------------------------------------------------

# 게임 초기화 및 메인 루프 실행
def main():
    places, event_answers = init_map()
    player = Player(places, "연대앞 버스정류장")
    player.event_answers = event_answers
    
    # 게임 인트로 출력
    print("송도 생활을 마치고 신촌에 처음 도착했다. 연대앞 버스정류장이다.")
    print("현재 시각은 11시.")
    print("1시 수업은 이윤재관 511호다.")
    
    while True:
        cmd = player.get_input("입력: ")
        
        if cmd == "상태":
            player.print_status()
        elif cmd in ["동", "서", "남", "북"]:
            player.move(cmd)
        elif cmd == "가방":
            player.open_bag()
        elif cmd == "구매":
            player.buy()
        elif cmd == "판매":
            player.sell()
        elif cmd == "임무":
            if player.location.name in ["정문", "독수리상", "본관", "세브란스", "이윤재관"]:
                player.handle_quest_interaction()
            else:
                print("여기서는 임무 상호작용을 할 수 없습니다.")
        elif cmd == "임무목록":
            player.show_quests()
        elif cmd == "저장":
            save_game(player)
        elif cmd == "불러오기":
            load_game(player)
        elif cmd == "난이도":
            player.change_difficulty()

if __name__ == "__main__":
    main()