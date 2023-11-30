# -*- encoding: utf-8 -*-
'''
@File    :   estimate.py
@Time    :   2021/11/09
@Version :   6.5
@instruct:   对棋盘状态进行评估的文件,对逻辑判断进行了优化

Input: board
    A matrix used to represent chessboard information
    Args  : 0--empty  1--my pieces  2--opponent pieces 3--win state
    E.g.
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 2, 0, 1, 0, 0, 2, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 2, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

Output: AlphaBetaSearch returns a location
    the best location to win
    E.g.
        5,5
'''

import random
from copy import deepcopy
import math

# 棋盘大小
width=20
height=20

def checkWetheredge(x,y):
    '''
    Info  :     返回每个棋子周围r圈的位置
    '''
    r=2
    return [(i,j) for i in range(max(x-r,0),min(x+r+1,width)) for j in range(max(y-r,0),min(y+r+1,height))]  

def CheckWhichToGo(board):
    '''
    Info  :     返回一个当前棋盘的探索列表，探索棋子两个距离内的点
    '''
    Queue = []
    my_place = [(i,j) for i in range(0,20) for j in range(0,20) if board[i][j] != 0]  #寻找棋盘上所有棋的位置
    for x,y in my_place:
        for i,j in checkWetheredge(x,y):
            if board[i][j] == 0 and (i,j) not in Queue:
                Queue.append((i,j))
    return Queue    #新下的棋子应该在已经放置的棋子的周围，否则与其他棋子相隔太远浪费时间，且没有意义

# 棋形对应数组下标
'''
    Table  ：   win--获胜状态
                all4--四字状态（活四对应两个）
                flex3--活三
                block3--眠三
                flex2--活二
                block2--眠二
'''
win=5
all4=4
flex3=3
flex2=2
block3=1
block2=0
# 棋型数目
ChessType=6


def checkOut(i,j):
    '''
        Info   ： 检查一个位置是否在棋盘内
        Input  :  点坐标
        Output ： 此坐标在不在棋盘内
    '''
    return i<0 or i>=width or j<0 or j>=height

# Direction list :  向右、向上、右上、右下四个方向的分量
directionx=[1,0,1,1]
directiony=[0,1,1,-1]

def isGuraded(board,i,j,dx,dy,player=1):
    '''
    Info   :  检查一个五连区域是否被防守住
    Input  :  棋盘信息，和一个五连区域的一端坐标和方向,以及当前立场,和新落子的位置
    Output ： 中间有无对手的子，如果有说明这个区域被防住了
    '''
    oppo_player=3-player
    for time in range(5):
        if board[i+time*dx][j+time*dy]==oppo_player:
            return True
    return False

def emptyNum(board,i,j,dx,dy):
    '''
    Info   :  计算一个五连区域的空点数
    Input  :  棋盘信息，和一个五连区域的一端坐标和方向
    Output ： 五个点有几个空点
    '''
    cnt=0
    for time in range(5):
         if board[i+time*dx][j+time*dy]==0:
            cnt +=1
    return cnt

'''-----------------    version 3.5 更新了检测一个五元组强度的函数和一个活棋检测函数------------------'''
def power(board,x,y,dx,dy,player):
    '''
    Info    :    检测一个五元组强度的函数
    Input   :    棋盘空间，起始坐标，方向，哪方强度
    Output  :    五元组能否取胜，不能返回-1，能的话返回已有几个子
    '''
    # 落在棋盘外
    if checkOut(x+4*dx,y+4*dy) or checkOut(x,y):
        return -11
    answer=0
    for time in range(5):
        if board[x+time*dx][y+time*dy]==3-player:
            return -1
        elif board[x+time*dx][y+time*dy]==player:
            answer +=1
    if answer==4 and board[x][y]!=0 and board[x+4*dx][y+4*dy]!=0 and 0<=x+5*dx<20 and 0<=y+5*dy<20 and board[x+5*dx][y+5*dy]==player:
        return -1
    return answer
def freetest(board,x,y,dx,dy,player,add=(None,None,None)):
    '''
    Info    :   检测五元组在方向偏移bias后是否唯一对应一活棋,true说明活棋,需要提前保证五元组为可获胜的。
    Input   :    棋盘空间，起始坐标，方向，偏移量,下棋方
    Output  :    1--是第一个活三，0--是但不是第一个，-1--眠，-2--是但不独立，-999--不合法
    '''
    bias=1
    # 检测合法性
    if checkOut(x,y) or checkOut(x+4*dx,y+4*dy) :
        return -999
    istop=checkOut(x-(bias)*dx,y-bias*dy) # 起点顶着棋盘
    alert= not checkOut(x+6*dx,y+6*dy) and (board[x+6*dx][y+6*dy]==player or (x+6*dx,y+6*dy,player)==add) #五元组后两格是否为己方棋子
    # 复制列表的首尾获取
    tail=4+bias+1 if not checkOut(x+5*dx,y+5*dy) else 4+bias
    begin=-bias if not istop else 0
    mylist=[board[x+n*dx][y+n*dy] if (x+n*dx,y+n*dy)!=(add[0],add[1]) else add[2] for n in range(begin,tail) ]
    # 后继检查
    backcheck=mylist[-begin]==0  and (tail==6 and mylist[5-begin]==0)
    # 前继检查
    forecheck= not istop and mylist[4-begin]==0 and (mylist[0]==0 or mylist[0]==player)
    if forecheck: #有前继
        return 0
    if not forecheck and not backcheck: #前后继都没有
        if tail==5+bias and mylist[5-begin]==player or (begin==-bias and mylist[0]==player) :
            return -2
        return -1
    # [0,0,0,1,1,1,0,1]第二到6位会被查出活三，但其实不是，进行修正
    # [0,0,1,0,1,1,0,1]第二到6位又应该计算
    # [0,0,1,0,1,1,0,1,1]
    if mylist[4-begin]!=0 and alert:
        if mylist[1-begin]==0:
            return -2
        if mylist[1-begin]!=0 and mylist[2-begin]==0 and 0<=x+7*dx<20 and 0<=y+7*dy<20 and board[x+7*dx][y+7*dy]==player:
            return -2
    return 1
'''-----------------------------------------------------------------------------'''

def count(board,player):
    '''
    Info   :    根据棋盘信息统计所有获胜状态数
    Input  ：   棋盘信息，当前立场
    Output ：   一个列表，统计不同强度的获胜状态的数量
    '''
    record=[0] * ChessType
    for direction in range(4):
        dx=directionx[direction]
        dy=directiony[direction]
        for i in range(width):
            for j in range(height):
                # 如果超出棋盘或被守住免去统计
                if checkOut(i+4*dx,j+4*dy) or isGuraded(board,i,j,dx,dy,player):
                    continue 
                its_power=power(board,i,j,dx,dy,player)
                if its_power==5:
                    record[win]+=1
                elif its_power==4:
                    # print('all4',i,j,dx,dy)
                    record[all4]+=1
                elif its_power==3:
                    test=freetest(board,i,j,dx,dy,player)
                    if test==1 :
                        # print('f3',i,j,dx,dy)
                        record[flex3]+=1
                    elif test==-1 :
                        record[block3]+=1
                elif its_power==2:
                    test=freetest(board,i,j,dx,dy,player)
                    if test==1:
                        # print('%d 的 f2'%player,i,j,dx,dy)
                        record[flex2]+=1
                    elif test==-1:
                        # print('b2',i,j,dx,dy) if player==1 else 0
                        record[block2]+=1
    return record

'''----------------version 2.0 新增更新记录的函数-------------------'''
def update(board,recordAll,x,y,player):
    '''
    Info   ：     用于更新获胜状态记录的函数
    Input  ：     两方的获胜状态记录，当前落子位置,s是哪一方落得子
    Output ：     新的两方的获胜状态记录
    '''
    # 先检查是否落在空位
    if board[x][y]!=0:
        print('不能下在这里')
        return recordAll
    # 深复制一份
    recordAll_new=deepcopy(recordAll)
    for direction in range(4):
        dx=directionx[direction]
        dy=directiony[direction]
        # 只用检查周围合法区域的变化即可
        for m in range(-6,2):
            i=x+m*dx
            j=y+m*dy
            # 如果超出棋盘免去修改
            if checkOut(i+4*dx,j+4*dy) or checkOut(i,j):
                continue 
            CanIWin_before=not isGuraded(board,i,j,dx,dy,player)  # 我落子前在此处是否有获胜可能
            CanOppoWin_before=not isGuraded(board,i,j,dx,dy,3-player)  # 我落子前对方在此处是否有获胜可能
            
            '''修改对方记录，在我的回合对方记录一定非增'''
            # 原本是对面的非5获胜状态
            if CanOppoWin_before:  
                itspower_before=power(board,i,j,dx,dy,3-player)
                if not -4<=m<=0:  # 此时落子不在检测五元组内
                    if itspower_before==4:
                        continue
                    # 活2活3在更新棋盘后减少
                    test_before=freetest(board,i,j,dx,dy,3-player)
                    test_now=freetest(board,i,j,dx,dy,3-player,add=(x,y,player))
                    if 2<=itspower_before<=3 and test_before==1 and test_now!=1:
                        # print('del f2',i,j,dx,dy,'现在test',test_now)
                        recordAll_new[2-player][itspower_before]-=1
                    if 2<=itspower_before<=3 and test_before!=-1 and test_now==-1:
                        # print('new b2',i,j,dx,dy) if  (i,j,dx,dy)==(9,9,1,-1) else 0
                        recordAll_new[2-player][itspower_before-2]+=1
                else:           # 此时落子在检测五元组内，若原本有贡献必减一
                    if itspower_before==4:
                        recordAll_new[2-player][all4]-=1
                        continue
                    test_before=freetest(board,i,j,dx,dy,3-player)
                    if 2<=itspower_before<=3:
                        if test_before==1:
                            recordAll_new[2-player][itspower_before]-=1  # 活3活2
                        elif test_before==-1:
                            recordAll_new[2-player][itspower_before-2]-=1  # 眠3眠2

            '''修改我方记录，在我的回合我方记录一定变更好'''
            # 原本是我的非5获胜状态
            if CanIWin_before: 
                itspower_before=power(board,i,j,dx,dy,player)
                if not -4<=m<=0: # 此时落子不在检测五元组内，不影响眠2眠3及4连
                    if itspower_before==4:
                        continue
                    test_before=freetest(board,i,j,dx,dy,player)
                    test_now=freetest(board,i,j,dx,dy,player,add=(x,y,player))
                    # 活2活3在更新棋盘后减少
                    if 2<=itspower_before<=3 and test_before==1 and test_now!=1:
                        recordAll_new[player-1][itspower_before]-=1
                else:          # 此时落子在检测五元组内
                    if itspower_before==4:
                        recordAll_new[player-1][win]+=1
                        continue
                    test_before=freetest(board,i,j,dx,dy,player)
                    test_now=freetest(board,i,j,dx,dy,player,add=(x,y,player))
                    if itspower_before==3:
                        # 旧棋型删去
                        if test_before==1: recordAll_new[player-1][flex3]-=1
                        elif test_before==-1:  recordAll_new[player-1][block3]-=1
                        # 新棋型添加,新五元组必定四连
                        recordAll_new[player-1][all4]+=1
                    if itspower_before==2:
                        # 旧棋型删去
                        if test_before==1: recordAll_new[player-1][flex2]-=1
                        elif test_before==-1:  recordAll_new[player-1][block2]-=1
                        # 新棋型添加,新五元组必定三连，继续判断类型
                        if test_now==1: recordAll_new[player-1][flex3]+=1
                        elif test_now==-1: recordAll_new[player-1][block3]+=1
                    if itspower_before==1:
                        # 新棋型添加,新五元组必定二连，继续判断类型
                        if test_now==1: recordAll_new[player-1][flex2]+=1
                        elif test_now==-1: recordAll_new[player-1][block2]+=1
                        
    return recordAll_new
'''----------------------------------------------------------------------'''





def estimate(board,player,i=None,j=None,coefficient=[1,15,8,100,150,2000,1,15,8,100,150,2000,0.5,0.8],recordAll=None):
    '''
    Info   :  评估落子在某一位置后的获胜状态的得分
    Input  ： 棋盘信息、落子坐标(可以给也可以不给)
    Output ： 一个得分
    win=5
    all4=4
    flex3=3
    flex2=2
    block3=1
    block2=0
    '''
    if i!=None and j!=None:
        if board[i][j]!=0:
            print('不能下在这里')
            return 0
        if recordAll==None:
            board_save=deepcopy(board)
            board_save[i][j]=player
            record1=count(board_save,player) 
            record2=count(board_save,3-player)
        else:
            record1=recordAll[player-1]# 当前立场局势
            record2=recordAll[2-player]# 对立局势
    else:
        if recordAll==None:
            record1=count(board,player) 
            record2=count(board,3-player)
        else:
            record1=recordAll[player-1]# 当前立场局势
            record2=recordAll[2-player]# 对立局势
    flag=1 if player==1 else -1
    reverse_re2=[-item for item in record2]
    relation1=0
    relation2=0
    # 我方落子直接赢
    if record1[win]>0:  
        value= 999999*flag
    # 对方再下1棋赢--多杀
    elif record2[all4]>=2 or (record2[all4]==1 and record2[flex3]>=1):
        value= -flag*(record2[all4]*35000+record2[flex3]*16000)
    # 对方再下1棋赢--单杀
    elif record2[all4]>0:
        value= -50000*flag
    # 我方再下1棋赢
    elif record1[all4]>=2: 
        value= (40000+1000*record1[all4])*flag
    # 我方平均再下1.5棋赢--多杀
    elif record1[all4]==1 and record1[flex3]>0:
        value= (30000+1000*record1[flex3])*flag
    # 对方再下2棋赢--多杀
    elif record2[flex3]>=2:
        value= -(20000+1000*record2[flex3])*flag
    # 对方再下2棋赢--单杀,对面有活三，我方无四
    elif record2[flex3]==1 and record1[all4]==0:
         value= -9000*flag
    # 我方再下2棋赢--多杀
    elif record1[flex3]>=2 and record2[block3]==0: 
        value= 1000*record1[flex3]*flag
    else:
        
        # 余下情况说明局势不明朗，给一个待发展分，获胜单元中如果只有一个点则方向不明确不做考虑
        value1=0
        value2=0
        
        for t in range(ChessType):
            value1+= coefficient[t]*record1[t]
            value2+= coefficient[t+6]*record2[t]

        relation1=0
        relation2=0
        for t in range(1,2):
            if i>=t and j>=t and board[i-t][j-t]==player: relation2+=1
            if i<20-t and j<20-t and board[i+t][j+t]==player: relation2+=1
            if i>=t and board[i-t][j]==player: relation1+=1
            if i<20-t and board[i+t][j]==player: relation1+=1
            if j>=t and board[i][j-t]==player: relation1+=1
            if j<20-t and board[i][j+t]==player: relation1+=1
            if i>=t and j<20-t and board[i-t][j+t]==player: relation2+=1
            if j>=t and i<20-t and board[i+t][j-t]==player: relation2+=1
        relation2=pow(relation2,0.1)
        relation1=pow(relation1,0.1)

        value1+=coefficient[12]*relation1+coefficient[13]*relation2

        weight=1
        value=flag*(weight*value1-value2)

    return value,record1+reverse_re2+[relation1,relation2]

def print_borad(board):
    myreplace={0:'.',1:'X',2:'O'}
    board2=[]
    for i in range(20):
        board2.append([myreplace[item] if item in myreplace else item for item in board[i]])
    print(1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0)
    for i in range(20):
        print(' '.join(board2[i]),'#',i+1)

if __name__=='__main__':
    board=[[0]*20 for i in range(20)]
    board[10][9:18]=[0,0,1,0,1,1,1,1,2]
    # board[12][12]=1
    print_borad(board)
    print(estimate(board,1,10,10))
