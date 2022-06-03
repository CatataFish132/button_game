buttons = []
for i in range(3):
    buttons.append([])
    for j in range(4):
        buttons[-1].append(0)
print(buttons)
button_count = 0
# count total presses
with open("button_logs.txt", "r") as f:
    for line in f.readlines():
        # line = f.readline()
        i,j = line.split(",")
        buttons[int(i)][int(j)] += 1
        button_count += 1

for button_row in buttons:
    print(button_row)

print(presses_per_button := round(button_count/12))
for i in range(len(buttons)):
    for j in range(len(button_row)):
        buttons[i][j] = str((buttons[i][j]*100)/presses_per_button) + "%"

for button_row in buttons:
    print(button_row)




last_i = 2
last_j = 3
count = 0
test_i = None
test_j = None
error = False
with open("button_logs.txt", "r") as f:
    while True:
        line = f.readline()
        if line == "":
            break
        # REMOVE THIS
        #if count == 100:
        #    break
        next_i = last_i + 1
        if next_i > 2:
            next_i = 0
            next_j = last_j + 1
            if next_j > 3:
                next_j = 0
                next_i = 0
        try:
            i, j = line.split(",")
        except:
            print(count)
        i = int(i)
        j = int(j)


        if error and test_j == j and test_i == i:
            print(i,j," button press out of nowhere on line ", count-1)
        elif error and next_i == i and next_j == j:
            print(i,j," skipped buttons presses on line ", count-1)
            # TODO calculate how many



        if last_i == i and last_j == j:
            print(i,j, "at line ",count," has been pressed double")
            # keep this false
            error = False
        elif test_j == j or test_i == i:
            # print("now its correct")
            test_i = None
            test_j = None
            error = False
        elif next_i != i or next_j != j:
            # print("fault detected at line: ", count)
            # print("the pressed button should have been ", next_i, next_j, " but was ", i, j)
            test_j = next_j
            test_i = next_i
            error = True
        else:
            error = False
            test_j = None
            test_i = None
        last_i = i
        last_j = j
        count += 1

