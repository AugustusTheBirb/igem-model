import random
with open("./map model/testData.csv", "w") as f:
    for i in range(150):
        #56.497772, 20.427051
        #53.441055, 27.249561
        
        z = round(random.random(),3)
        x = random.randint(0, 2500)
        y = random.randint(0, 1875) 
        f.write(f"{x},{y},{z}\n")
