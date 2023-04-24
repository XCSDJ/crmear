



dict_vin ={"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,
"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8,"J":1,"K":2,"L":3,"M":4,"N":5,"P":7,"R":9,"S":2,"T":3,"U":4,"V":5,"W":6,"X":7,"Y":8,"Z":9}
list_sc = [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]
x = "LVAV2JVB8PE301538"


def check_vin(vin):
    num=0
    for i,j in enumerate(vin):
        if i !=8:
            s1 = list_sc[i]*dict_vin[j]
            num+=s1
    return num%11==int(vin[8])
print({1:"1"}) 
    




