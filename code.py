leaderlist = []
best = False
new_score = 0
new_user_name = ""

with open("score_tracker", "r", encoding="utf-8") as f:
    leaderlist = f.readlines()

while True:
    new_user_name = input("enter a 3 letter name\n").upper()
    if len(new_user_name) == 3:
        break

new_score = int(input("enter score\n"))

if len(leaderlist) == 0:
    leaderlist = [f"{new_user_name}: {new_score}\n"]
for i in range(0,len(leaderlist)):
    if int(leaderlist[i][5:-1]) <= new_score and best == False:
        leaderlist.insert(i, f"{new_user_name}: {new_score}\n")
        best = True
        i +=1
    if new_user_name == leaderlist[i][:3] and best == False:
        break
    elif new_user_name == leaderlist[i][:3]:
        leaderlist.pop(i)

with open("score_tracker", "w", encoding="utf-8") as f:
    f.writelines(leaderlist)   