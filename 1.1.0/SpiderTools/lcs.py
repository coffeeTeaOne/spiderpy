# encoding: utf-8
# 最长公共子序列


class LCS:
    """
    计算两个序列的的最长公共子序列
    """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __lcs_len(self, a, b):
        '''
        a, b: strings
        '''
        n = len(a)
        m = len(b)
        l = [([0] * (m + 1)) for i in range(n + 1)]
        direct = [([0] * m) for i in range(n)]  # 0 for top left, -1 for left, 1 for top
        for i in range(n + 1)[1:]:
            for j in range(m + 1)[1:]:
                if a[i - 1] == b[j - 1]:
                    l[i][j] = l[i - 1][j - 1] + 1
                elif l[i][j - 1] > l[i - 1][j]:
                    l[i][j] = l[i][j - 1]
                    direct[i - 1][j - 1] = -1
                else:
                    l[i][j] = l[i - 1][j]
                    direct[i - 1][j - 1] = 1
        return l, direct

    def get_lcs(self):
        '''
        direct: martix of arrows
        a: 被认为是行的字符串
        i: len(a) - 1, for 赋初值
        j: len(b) - 1, for 赋初值
        '''
        lcs = []
        l, direct = self.__lcs_len(self.a, self.b)
        self.__get_lcs_inner(direct, self.a, len(self.a) - 1, len(self.b) - 1, lcs)
        return ''.join(lcs)

    def __get_lcs_inner(self, direct, a, i, j, lcs):
        if i < 0 or j < 0:
            return
        if direct[i][j] == 0:
            self.__get_lcs_inner(direct, a, i - 1, j - 1, lcs)
            lcs.append(a[i])
        elif direct[i][j] == 1:
            self.__get_lcs_inner(direct, a, i - 1, j, lcs)
        else:
            self.__get_lcs_inner(direct, a, i, j - 1, lcs)
