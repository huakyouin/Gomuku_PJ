import sys
import os
import json
from typing import NewType
from typing_extensions import runtime
import pandas as pd
import math
import csv
import random
import estimate

# 获取工作路径
filepath=sys.path[0]

# 读迭代次数
def load_iter():
    f = open(filepath+"/"+"iter.txt")
    data=f.read()
    f.close()
    data=int(data)
    return data

# 从文件读取学习系数
def load_coefficient():
    f = open(filepath+"/"+"coefficient.txt")
    data=f.read()
    f.close()
    data=data.split('\n')
    data=list(map(lambda x: float(x), data))
    return data

# 存迭代次数
def save_iter(iter):
    f = open(filepath+"/"+"iter.txt",'w')
    str1 = str(iter)
    f.write(str1)
    f.close()
    return

# 往文件中修改学习系数
def save_coefficient(data):
    f = open(filepath+"/"+"coefficient.txt",'w')
    str1 = '\n'.join('%s' %id for id in data)
    f.write(str1)
    f.close()
    return

# 从文件读取\预处理训练集
def prepare_traindata():
    i=1
    data0=[]
    for filename in os.listdir(filepath+'/traindata'):
        if os.path.exists(filepath+'/treated'+'/'+filename):
            f = open(filepath+'/treated'+'/'+filename, 'r')
            csvreader = csv.reader(f)
            final_list = list(csvreader)
            data2=[(int(item[0]),int(item[1])) for item in final_list]
            # data2=pd.read_csv(filepath+'/treated'+'/'+filename,usecols=int)
            data0.append(data2)
            continue
        f = open(filepath+'/traindata'+'/'+filename,"r",encoding="utf-8") 
        data=f.read()
        data=data.split('\n')
        del data[0]
        length=len(data)
        del data[length-4:length]
        data1=[item.split(',') for item in data]
        data2=[(int(item[0]),int(item[1])) for item in data1]
        f.close()
        df = pd.DataFrame(data2)
        df.to_csv(filepath+'/treated'+'/'+filename,index=False,header=False)
        data0.append(data2)
    return data0

# 随机抽取函数
def sampling(data,choosenum=1):
    length=len(data)
    answer=[]
    for choosetime in range(choosenum):
        ran=random.randint(0, length-1)
        answer.append(data[ran])
    return answer

# 将训练数据转化成棋盘,返回第i步棋的棋盘及第i+1步的落子位置及所属玩家
def build_board(data,step):
    board=[[0]*20 for i in range(20)]
    for i in range(1,step+1):
        player=1 if i%2==1 else 2
        x,y=data[i-1]           # 编码定义
        board[x-1][y-1]=player            # 编码定义
    belong=1 if step%2==0 else 2
    if step==len(data):  return board,None,belong  # 如果还未给出就返回None
    return board,data[step],belong        # 编码定义

# 打印规整的棋盘信息
def print_borad(board):
    myreplace={0:'.',1:'X',2:'O'}
    board2=[]
    for i in range(20):
        board2.append([myreplace[item] if item in myreplace else item for item in board[i]])
    print(1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0)
    for i in range(20):
        print(' '.join(board2[i]),'#',i+1)

# 判断当前对局数据是哪一方赢了
def who_win(data):
    return 1 if len(data)%2==1 else 2

# 获取在某一局面时落在指定位置得分估值的函数
def est_next(board,next,player,coefficient):
    val,para=estimate.estimate(board,player,i=next[0]-1,j=next[1]-1,coefficient=coefficient)   # 编码定义
    return val,para       

# 获取某一局面时所有候选点得分估值的函数
def est_all(board,player,coefficient):
    list=estimate.CheckWhichToGo(board)
    answer2=[]
    answer3=[]
            
    for point in list:
        x,y=point
        val,para=estimate.estimate(board,player,x,y,coefficient)
        answer2.append((val,(x+1,y+1),para))       # 人类定义
        answer3=sorted(answer2) if player==2 else sorted(answer2,reverse=True)
    return answer3

# 打印候选点情况的函数
def print_estALL(board,player,coefficient,num=0):
    print('各点估值：') if num!=0 else 0
    print('\n'.join(str(i) for i in est_all(board,player,coefficient)[0:num])) if num!=0 else 0

# 根据某一步选择进行系数学习的函数
def one_step_learning(board,next,player,coefficient,rate):
    case_list=est_all(board,player,coefficient)
    # 如果必胜了就不进行学习
    if abs(case_list[0][0])>=1000: return 0,coefficient
    true_best=est_next(board,next,player,coefficient)
    # 如果真最优与过估计最优相同就直接返回
    if case_list[0][2]==true_best[1]: return 0,coefficient
    loss=case_list[0][0]-true_best[0]
    gradient=[case_list[0][2][i]-true_best[1][i] for i in range(len(true_best[1]))]
    x_gradient=0
    for i in range(len(coefficient)):
        x_gradient+=coefficient[i]*gradient[i]
    # 如果梯度为0也返回原值防止报错
    if x_gradient==0: return 0,coefficient
    my_lambda=loss/x_gradient
    new_coefficient=[coefficient[i]+rate*my_lambda*gradient[i] for i in range(len(true_best[1]))]
    return my_lambda, new_coefficient

# 对一场对局进行学习的函数
def one_game_learning(traindata,learn_side='both',learning_rate=0.2):
    data=sampling(traindata)[0]
    win_side=who_win(data)       
    for step in range(2,len(data)):
        coefficient=load_coefficient()
        board,next,player=build_board(data,step)
        # 只学习赢方的下法
        if learn_side=='win' and player!=win_side: continue
        # print('player %d choose:'%player,next,'val=',est_next(board,next,player,coefficient)[0])
        ignore,new_coefficient=one_step_learning(board,next,player,coefficient,learning_rate)
        save_coefficient(new_coefficient)
        print_estALL(board,player,new_coefficient)
    print('player %d win!'%win_side)
        


# 用于调试的杂七杂八的函数
def Debug():
    coefficient=load_coefficient()
    data=sampling(prepare_traindata())[0]
    # coefficient=[1,15,8,100,150,2000,-1,-15,-8,-100,-150,-2000]
    # print('抽取到：',data)
    board,next,player=build_board(data,1)
    print_borad(board)
    print('player %d win'%who_win(data))
    print('player %d choose:'%player,next,'val=',est_next(board,next,player,coefficient)[0])
    # print_estALL(board,player,coefficient)
    ignore,new_coefficient=one_step_learning(board,next,player,coefficient,0.2)
    save_coefficient(new_coefficient)
    print_estALL(board,player,new_coefficient)
    

# 初始化权值函数
def initial():
    start=[0.1,0.2,0.3,0.4,0.5,2000,0.1,0.2,0.3,0.4,0.5,2000,0.01]
    save_coefficient(start)



# 自对奕学习一次
def self_learning(learning_rate=0.5,e=0.2):
    data=[(10,10),(9,9)]
    board=build_board(data,2)[0]
    coefficient=load_coefficient()
    # 初始化
    case_list=est_all(board,1,coefficient)
    para_list=[[0]*12,[0]*12]
    player=1
    # 比赛结束前一直循环
    while(abs(case_list[0][0])!=999999):
        r_v = random.uniform(0, 1) #epsilon
        if r_v>e or abs(case_list[0][0])>=1000:
            data.append(case_list[0][1])
            para_list.append(case_list[0][2])
            x,y=case_list[0][1]  # 自然坐标
        else:
            upper=0
            for i in range(len(case_list)):
                if abs(case_list[i][0])>=1000:
                    break
                upper+=1
            ran=random.randint(0, upper-1)
            data.append(case_list[ran][1])
            para_list.append(case_list[ran][2])
            x,y=case_list[ran][1]  # 自然坐标
        board[x-1][y-1]=player   # 存储坐标
        # print('player %d at'%player ,x,y)
        # print_borad(board)
        # print(case_list[0:5])
        player=3-player
        case_list=est_all(board,player,coefficient)
    
    winner=1 if case_list[0][0]>=1000 else 2
    data.append(case_list[0][1])
    para_list.append(case_list[0][2])
    x,y=case_list[0][1]  # 自然坐标
    board[x-1][y-1]=player   # 存储坐标
    print_borad(board)
    # print(data)
    print('winner:',winner)
    
    # 开始更新权值,反向传播

    true_list=[1 if (i+winner)%2==1 else 0 for i in range(len(data))]
    flag_list=[-1 if (i+winner)%2==1 else 1 for i in range(len(data))]
    max_error=0
    old_error=1
    time=0
    while(abs(max_error-old_error)>0.001 and time<50):
        for step in range(1,len(data)-3):
            old_error=max_error
            max_error=0
            back_step=len(data)-1-step
            val=0
            for i in range(len(coefficient)):
                val+=coefficient[i]*para_list[back_step][i]
            turn=1
            if back_step%2==1  : 
                turn=2
            if val>1000:
                h=1
            elif val<-1000:
                h=0
            else:
                h=1/(1+math.exp(-val))
            
            error=abs(true_list[back_step]-h)
            max_error+=error
            gradient=[flag_list[back_step]*error*(1-error)*item for item in para_list[back_step]]
            new_coefficient=[coefficient[i]-pow(0.9,step-1)*learning_rate*gradient[i] for i in range(len(coefficient))]
            if new_coefficient[12]<0: new_coefficient[12]=0.01 # 稍微垫一下
            if new_coefficient[13]<0: new_coefficient[13]=0.02 # 稍微垫一下
            coefficient=new_coefficient
            val2=0
            # for i in range(len(coefficient)):
            #     val2+=coefficient[i]*para_list[back_step][i]
            # print('player:',turn,'val ',val,'下在：',data[back_step],'参数：',para_list[back_step])
            # print('new val-val:',val2-val)

        save_coefficient(coefficient)
        # print("error:",max_error)
        time+=1

        


if __name__=='__main__':
    # initial()
    iter=load_iter()
    while(iter<=5000):
        print('iter:',iter)
        l_r=0.003*(1-iter/10000)
        self_learning(learning_rate=l_r,e=0.15-iter/10000*0.15)
        iter+=1
        save_iter(iter)
    # traindata=prepare_traindata()
    # for time in range(1000):
    #     print('第%d轮：'%time)
    #     one_game_learning(traindata,learn_side='win',learning_rate=0.3)


# 神秘代码
# nohup python train.py > my.log 2>&1 &
# 查看进度
# ps -aux | grep "train.py" 
# 结束进程
# kill -s 9 PID