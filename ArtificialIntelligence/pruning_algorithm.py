import numpy as np
import re
from time import time


class PruningAlg:
    # 0表示空位置，1表示黑棋，2表示白棋，3表示边界
    empty = 0
    black = 1
    white = 2
    border = 3

    def __init__(self, ctrl_side=white):
        """

        :param ctrl_side: 程序所控制的一方（用数字表示）  默认为白棋
        """
        self.left, self.right, self.top, self.bottom = 0, 0, 0, 0  # 待搜索棋盘的边界
        self.ctrl_side = ctrl_side  # 程序控制的一方  默认控制白棋
        self.opposite_side = self.white if ctrl_side == self.black else self.black  # 对手  默认为白棋
        self.board = None  # 棋盘矩阵
        self.inf = 1000000  # 自定义正无穷
        self.max_layer = 2  # 搜索到的最大层数
        self.static_eval_layer = -1  # 层数小于等于静态评估层时进行静态评估
        # (进攻系数/防守系数)越大表示进攻性越强，反之防守性越强
        self.attack_coefficient = 2
        self.deffense_coefficent = 1
        self.border_width = 1  # 边界宽度
        self.expand_span = 2  # 向外扩展的格数

        self.node_cnt = 0  # 实际搜索结点数
        self.eval_cnt = 0  # 总评估次数
        self.static_eval_cnt = 0  # 静态评估次数
        self.leaves_eval_cnt = 0  # 叶子结点数
        self.round_cnt = 0  # 回合数
        self.theo_node_cnt = 0  # 理论最大搜索结点数

        # 五连
        ctrl_str5 = re.compile('{ctrl}{{5,}}'.format(ctrl=ctrl_side))
        oppo_str5 = re.compile('{ctrl}{{5,}}'.format(ctrl=self.opposite_side))

        # 活四
        ctrl_alive4 = re.compile('{empty}{ctrl}{{4}}{empty}'.format(ctrl=ctrl_side, empty=self.empty))
        oppo_alive4 = re.compile('{empty}{ctrl}{{4}}{empty}'.format(ctrl=self.opposite_side, empty=self.empty))

        # 冲四
        ctrl_punch4 = re.compile('(?:{border}|{oppo}){ctrl}{{4}}{empty}|'
                                 '{empty}{ctrl}{{4}}(?:{border}|{oppo})|'
                                 '{empty}{ctrl}{{3}}{oppo}{ctrl}{empty}|'
                                 '{empty}{ctrl}{oppo}{ctrl}{{3}}{empty}|'
                                 '{empty}{ctrl}{{2}}{oppo}{ctrl}{{2}}{empty}'.format(ctrl=ctrl_side, empty=self.empty,
                                                                                     oppo=self.opposite_side,
                                                                                     border=self.border))
        oppo_punch4 = re.compile('(?:{border}|{oppo}){ctrl}{{4}}{empty}|'
                                 '{empty}{ctrl}{{4}}(?:{border}|{oppo})|'
                                 '{empty}{ctrl}{{3}}{oppo}{ctrl}{empty}|'
                                 '{empty}{ctrl}{oppo}{ctrl}{{3}}{empty}|'
                                 '{empty}{ctrl}{{2}}{oppo}{ctrl}{{2}}{empty}'.format(ctrl=self.opposite_side,
                                                                                     empty=self.empty, oppo=ctrl_side,
                                                                                     border=self.border))

        # 活三
        ctrl_alive3 = re.compile('{empty}{ctrl}{{3}}{empty}'.format(ctrl=ctrl_side, empty=self.empty))
        oppo_alive3 = re.compile('{empty}{ctrl}{{3}}{empty}'.format(ctrl=self.opposite_side, empty=self.empty))

        # 跳活三
        ctrl_jump_alive3 = re.compile('{empty}{ctrl}{empty}{ctrl}{{2}}{empty}|'
                                      '{empty}{ctrl}{{2}}{empty}{ctrl}{empty}'.format(ctrl=self.ctrl_side,
                                                                                      empty=self.empty))
        oppo_jump_alive3 = re.compile('{empty}{ctrl}{empty}{ctrl}{{2}}{empty}|'
                                      '{empty}{ctrl}{{2}}{empty}{ctrl}{empty}'.format(ctrl=self.opposite_side,
                                                                                      empty=self.empty))

        # 眠三
        ctrl_asleep3 = re.compile('{empty}{{2}}{ctrl}{{3}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{3}}{empty}{{2}}|'
                                  '{empty}{ctrl}{empty}{ctrl}{{2}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{2}}{empty}{ctrl}{empty}|'
                                  '{empty}{ctrl}{{2}}{empty}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{ctrl}{{2}}{empty}|'
                                  '{empty}{ctrl}{empty}{{2}}{ctrl}{{2}}{empty}|'
                                  '{empty}{ctrl}{{2}}{empty}{{2}}{ctrl}{empty}|'
                                  '{empty}{ctrl}{empty}{ctrl}{empty}{ctrl}{empty}|'
                                  '(?:{border}|{oppo}){empty}{ctrl}{{3}}{empty}(?:{border}|{oppo})'.format(
            ctrl=ctrl_side, empty=self.empty, oppo=self.opposite_side, border=self.border))
        oppo_asleep3 = re.compile('{empty}{{2}}{ctrl}{{3}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{3}}{empty}{{2}}|'
                                  '{empty}{ctrl}{empty}{ctrl}{{2}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{2}}{empty}{ctrl}{empty}|'
                                  '{empty}{ctrl}{{2}}{empty}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{ctrl}{{2}}{empty}|'
                                  '{empty}{ctrl}{empty}{{2}}{ctrl}{{2}}{empty}|'
                                  '{empty}{ctrl}{{2}}{empty}{{2}}{ctrl}{empty}|'
                                  '{empty}{ctrl}{empty}{ctrl}{empty}{ctrl}{empty}|'
                                  '(?:{border}|{oppo}){empty}{ctrl}{{3}}{empty}(?:{border}|{oppo})'.format(
            ctrl=self.opposite_side, empty=self.empty, oppo=ctrl_side, border=self.border))

        # 活二
        ctrl_alive2 = re.compile('{empty}{{2}}{ctrl}{{2}}{empty}{{2}}|'
                                 '{empty}{ctrl}{empty}{ctrl}{empty}|'
                                 '{empty}{ctrl}{empty}{{2}}{ctrl}{empty}'.format(ctrl=ctrl_side, empty=self.empty))
        oppo_alive2 = re.compile('{empty}{{2}}{ctrl}{{2}}{empty}{{2}}|'
                                 '{empty}{ctrl}{empty}{ctrl}{empty}|'
                                 '{empty}{ctrl}{empty}{{2}}{ctrl}{empty}'.format(ctrl=self.opposite_side, empty=self.empty))

        # 眠二
        ctrl_asleep2 = re.compile('{empty}{{3}}{ctrl}{{2}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{2}}{empty}{{3}}|'
                                  '{empty}{{2}}{ctrl}{empty}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{ctrl}{empty}{{2}}|'
                                  '{empty}{ctrl}{empty}{{2}}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{{2}}{ctrl}{empty}|'
                                  '{empty}{ctrl}{empty}{{3}}{ctrl}{empty}'.format(ctrl=ctrl_side, empty=self.empty,
                                                                                  oppo=self.opposite_side,
                                                                                  border=self.border))
        oppo_asleep2 = re.compile('{empty}{{3}}{ctrl}{{2}}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{{2}}{empty}{{3}}|'
                                  '{empty}{{2}}{ctrl}{empty}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{ctrl}{empty}{{2}}|'
                                  '{empty}{ctrl}{empty}{{2}}{ctrl}(?:{border}|{oppo})|'
                                  '(?:{border}|{oppo}){ctrl}{empty}{{2}}{ctrl}{empty}|'
                                  '{empty}{ctrl}{empty}{{3}}{ctrl}{empty}'.format(ctrl=self.opposite_side,
                                                                                  empty=self.empty, oppo=ctrl_side,
                                                                                  border=self.border))

        # 每一项的含义：   评估招式:对应分数
        self.eval_ctrl_items = {ctrl_str5: 10000, ctrl_alive4: 500, ctrl_punch4: 30, ctrl_alive3: 25,
                                ctrl_jump_alive3: 20,
                                ctrl_asleep3: 10, ctrl_alive2: 5, ctrl_asleep2: 2}
        self.eval_oppo_items = {oppo_str5: 10000, oppo_alive4: 500, oppo_punch4: 30, oppo_alive3: 25,
                                oppo_jump_alive3: 20,
                                oppo_asleep3: 10, oppo_alive2: 5, oppo_asleep2: 2}

    def readBoard(self, board: np.array):
        """
        读取棋盘、外扩格数，确定搜索范围
        在不超过棋盘大小的前提下，以已下棋子所确定的最小矩阵再向外扩展expand_span个格子
        :param board: 棋盘
        :return:
        """
        self.left = board.shape[1]
        self.right = -1
        self.top = board.shape[0]
        self.bottom = -1

        # 遍历寻找包含已下棋子的最小矩阵
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                if board[i][j] != self.empty:
                    self.left = min(self.left, j)
                    self.right = max(self.right, j)
                    self.top = min(self.top, i)
                    self.bottom = max(self.bottom, i)

        # 棋盘里没有棋子,抛出错误
        if self.left > self.right or self.top > self.bottom:
            raise

        # 向外扩展  如果扩展后超出棋盘范围，则取棋盘大小作为搜索边界
        self.left = max(self.left - self.expand_span, 0)
        self.right = min(self.right + self.expand_span, board.shape[1] - 1)
        self.top = max(self.top - self.expand_span, 0)
        self.bottom = min(self.bottom + self.expand_span, board.shape[0] - 1)

        # 给棋盘加一圈边界
        self.board = np.zeros(shape=(
            self.bottom - self.top + 1 + self.border_width * 2, self.right - self.left + 1 + self.border_width * 2),
            dtype='int8')
        self.board[0, :] = self.board[-1, :] = np.ones(self.right - self.left + 1 + self.border_width * 2,
                                                       dtype='int8') * self.border
        self.board[:, 0] = self.board[:, -1] = np.ones(self.bottom - self.top + 1 + self.border_width * 2,
                                                       dtype='int8') * self.border
        # 截取出搜索部分的棋盘  棋盘矩阵里的数的类型为int8
        self.board[1:-1, 1:-1] = np.array(board, dtype='int8')[self.top:self.bottom + 1, self.left:self.right + 1]

    def calUtility(self) -> int:
        """
        计算该结点的评估值
        :return: 评估值
        """
        # 统计评价次数
        self.eval_cnt += 1

        # 己方的评估值
        ctrl_value = 0
        ctrl_value += self.evalInRow(self.eval_ctrl_items)
        ctrl_value += self.evalInDiag(self.eval_ctrl_items)
        self.board = np.rot90(self.board)  # 逆时针旋转90度,求列和逆对角线的评估值
        ctrl_value += self.evalInRow(self.eval_ctrl_items)
        ctrl_value += self.evalInDiag(self.eval_ctrl_items)

        # 对方的评估值  此时矩阵已旋转
        opposite_value = 0
        opposite_value += self.evalInRow(self.eval_oppo_items)
        opposite_value += self.evalInDiag(self.eval_oppo_items)
        self.board = np.rot90(self.board, -1)  # 顺时针旋转90度，恢复原来的状态
        opposite_value += self.evalInRow(self.eval_oppo_items)
        opposite_value += self.evalInDiag(self.eval_oppo_items)
        value = int(self.attack_coefficient * ctrl_value - self.deffense_coefficent * opposite_value)
        return value

    def terminalTest(self, layer):
        """
        终止结点判断
        :param layer:
        :return:
        """
        if layer >= self.max_layer:
            return True
        else:
            return False

    def static_eval(self, mode, layer):
        """
        静态评价启发
        :param mode: 评价模式  mode=='max'表示对极大结点评价；mode=='min'表示对极小结点评价
        :param layer: 调用该函数时所处的层数
        :return: 经排序后的待扩展结点
        """
        empty_pos = []
        for i in range(self.border_width, self.board.shape[0] - 1):
            for j in range(self.border_width, self.board.shape[1] - 1):
                # 遍历到可以下棋的位置
                if self.board[i][j] == self.empty:
                    # 统计结点数
                    self.node_cnt += 1
                    # 静态评价  该过程是在父节点扩展时进行的，所以layer-1
                    if layer - 1 <= self.static_eval_layer:
                        # 统计静态评价的次数
                        self.static_eval_cnt += 1

                        # 得到该步产生的结果
                        self.board[i][j] = self.ctrl_side
                        empty_pos.append((i, j, self.calUtility()))
                        # 取消该步产生的结果
                        self.board[i][j] = self.empty
                    else:
                        empty_pos.append((i, j, 0))
        if mode == 'max':
            empty_pos.sort(key=lambda pos: pos[2])  # 按效用值从小到大排序
        elif mode == 'min':
            empty_pos.sort(key=lambda pos: pos[2], reverse=True)  # 按效用值从大到小排序
        return empty_pos

    def maxValue(self, alpha, beta, layer):
        """
        求当前状态的极大值
        :param layer:
        :param alpha:
        :param beta:
        :return: 极大值和存有类型为numpy.ndarray的最佳选择位置   传入终止棋盘时返回的位置为None
        """
        # 传入终止状态时返回效用值
        if self.terminalTest(layer - 1):
            self.leaves_eval_cnt += 1
            return self.calUtility(), None
        # 静态启发式评价
        empty_pos = self.static_eval(mode='max', layer=layer)

        value = -self.inf  # 评估值
        pos = None  # 棋盘下满后该怎么办？
        best_pos = None  # 存放该结点的最优落子
        while empty_pos:  # 从empty_pos中取值赋给pos  按效用值从大到小取
            pos = empty_pos.pop()
            # 得到该步产生的结果
            self.board[pos[0]][pos[1]] = self.ctrl_side

            # 子节点的评估值
            tmp = self.minValue(alpha, beta, layer + 1)
            if value < tmp[0]:
                value = tmp[0]
                best_pos = np.array([pos[0], pos[1]])

            # 取消该步产生的结果
            self.board[pos[0]][pos[1]] = self.empty
            # 剪枝
            if value >= beta:
                return value, best_pos
            alpha = max(alpha, value)
        return value, best_pos  # 没发生剪枝

    def minValue(self, alpha, beta, layer):
        """
        求当前状态的极小值
        :param layer:
        :param alpha:
        :param beta:
        :return: 极小值和存有类型为numpy.ndarray的最佳选择位置   传入终止棋盘时返回的位置为None
        """
        # 传入终止状态时返回效用值
        if self.terminalTest(layer - 1):
            self.leaves_eval_cnt += 1
            return self.calUtility(), None
        # 静态启发式评价
        empty_pos = self.static_eval(mode='min', layer=layer)

        value = self.inf  # 评估值
        pos = None  # 棋盘下满后该怎么办？
        best_pos = None  # 存放该结点的最优落子
        while empty_pos:  # 从empty_pos中取值赋给pos  按效用值从小到大取
            pos = empty_pos.pop()
            # 得到该步产生的结果
            self.board[pos[0]][pos[1]] = self.opposite_side

            tmp = self.maxValue(alpha, beta, layer + 1)
            if value > tmp[0]:
                value = tmp[0]
                best_pos = np.array([pos[0], pos[1]])

            # 取消该步产生的结果
            self.board[pos[0]][pos[1]] = self.empty
            # 剪枝
            if value <= alpha:
                return value, best_pos
            beta = min(beta, value)
        return value, best_pos  # 没发生剪枝

    def evalInRow(self, eval_items):
        """
        按行进行评估
        :return: 评估值
        """
        value = 0
        for row in self.board[1:self.board.shape[0] - 1]:  # 上下边界不评估
            # 把该行转为字符串，用正则表达式计算匹配个数
            row_str = ''.join([str(i) for i in row])
            for item in eval_items.items():
                value += len(item[0].findall(row_str)) * item[1]  # 匹配个数乘对应分值
        return value

    def evalInDiag(self, eval_items):
        """
        按方向为从左上到右下的对角线进行评估
        :return: 评估值
        """
        value = 0
        # 按对角线从左下角到右上角的顺序评估
        for diag_offset in range(-self.board.shape[0] + 3, self.board.shape[1] - 2):
            # 把该对角线转为字符串，用正则表达式计算匹配个数
            diag_str = ''.join([str(i) for i in np.diag(self.board, k=diag_offset)])
            for item in eval_items.items():
                value += len(item[0].findall(diag_str)) * item[1]  # 匹配个数乘对应分值

        return value

    def startSearch(self, board):
        """
        对棋局进行搜索，给出下一步的最佳策略
        :param board: 输入的棋局
        :return: 下一步落子的坐标，坐标类型为np.array
        """
        start = time()

        try:
            self.readBoard(board)
        except Exception:  # 棋盘中没有棋子,返回棋盘中间位置
            return np.array([board.shape[0] // 2, board.shape[1] // 2])
        choice = self.maxValue(-self.inf, self.inf, layer=1)[1] + np.array([self.top - 1, self.left - 1])
        end = time()
        # 计算理论最大搜索结点数
        empty_cnt = 0  # 棋盘上的空位置数
        for row in self.board:
            for col in row:
                if col == self.empty:
                    empty_cnt += 1
        single_layer_node_cnt = 1  # 单层上的结点数
        for i in range(self.max_layer):
            single_layer_node_cnt = empty_cnt * single_layer_node_cnt
            self.theo_node_cnt += single_layer_node_cnt
            empty_cnt -= 1

        self.round_cnt += 1  # 回合数

        print('第' + str(self.round_cnt) + '回合')
        print('搜索用时：' + str(end - start) + '秒')
        print('理论最大搜索结点数：' + str(self.theo_node_cnt))
        print('实际搜索结点数：' + str(self.node_cnt))
        print('叶子结点数：' + str(self.leaves_eval_cnt))
        print('静态评估次数：' + str(self.static_eval_cnt))
        print('总评估次数：' + str(self.eval_cnt))
        print()

        # 自适应调整搜索层数、静态评估层数
        if self.node_cnt >= 3000:  # 实际搜索结点过多
            self.max_layer = 2
            if self.node_cnt >= 5000:
                self.static_eval_layer = 0
                print('搜索2层，静态评估1层')
            else:
                self.static_eval_layer = -1
                print('搜索2层，无静态评估')
        else:  # 搜索结点较少时采用更深的搜索
            if self.round_cnt >= 7:  # 超过一定回合后开启3层搜索
                self.max_layer = 3
                self.static_eval_layer = 0
                print('搜索3层，静态评估1层')
            elif self.round_cnt >= 3:  # 回合较少，搜索2层
                self.max_layer = 2
                self.static_eval_layer = 0
                print('搜索2层，静态评估1层')
            else:
                self.max_layer = 2
                self.static_eval_layer = -1
                print('搜索2层，无静态评估')

        self.static_eval_cnt = 0
        self.eval_cnt = 0
        self.node_cnt = 0
        self.leaves_eval_cnt = 0
        return choice
