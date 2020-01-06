
import pymysql
jrcp_codes = ['JRCP_LCCP_ZGLCW_ALL', 'JRCP_LCCP_ZGJSYH_GW_ALL1', 'JRCP_LCCP_ZGJSYH_GW_ALL', 'JRCP_LCCP_ZGNYYH_GW_ALL',
              'JRCP_LCCP_ZSYH_GW_ALL', 'JRCP_LCCP_ZGYH_GW_ALL', 'JRCP_LCCP_JTYH_GW_ALL', 'JRCP_LCCP_BHYH_GW_ALL',
              'JRCP_LCCP_ZGGDYH_GW_ALL', 'JRCP_LCCP_GFYH_GW_ALL', 'JRCP_LCCP_XYYH_GW_ALL', 'JRCP_LCCP_ZGMSYH_GW_ALL',
              'JRCP_LCCP_ZSYH_GW_CJ', 'JRCP_LCCP_ZSYH_GW_ALL1', 'JRCP_LCCP_HFYH_GW_ALL', 'JRCP_LCCP_ZXYH_GW_ALL',
              'JRCP_LCCP_HXYH_GW_ALL', 'JRCP_LCCP_ZGGSYH_GW_ALL', 'JRCP_LCCP_PAYH_GW_ALL', 'JRCP_LCCP_PAYH_GW_ALL1',
              'JRCP_LCCP_PFYH_GW_ALL', 'B_JRCP_LCCP_ZGJSYH_GW_ALL1', 'B_JRCP_LCCP_ZGJSYH_GW_ALL',
              'B_JRCP_LCCP_ZGNYYH_GW_ALL', 'B_JRCP_LCCP_ZSYH_GW_ALL', 'B_JRCP_LCCP_ZGYH_GW_ALL',
              'B_JRCP_LCCP_JTYH_GW_ALL', 'B_JRCP_LCCP_BHYH_GW_ALL', 'B_JRCP_LCCP_ZGGDYH_GW_ALL',
              'B_JRCP_LCCP_GFYH_GW_ALL', 'B_JRCP_LCCP_XYYH_GW_ALL', 'B_JRCP_LCCP_ZGMSYH_GW_ALL',
              'B_JRCP_LCCP_ZSYH_GW_ALL1', 'B_JRCP_LCCP_HFYH_GW_ALL', 'B_JRCP_LCCP_ZXYH_GW_ALL',
              'B_JRCP_LCCP_HXYH_GW_ALL', 'B_JRCP_LCCP_ZGGSYH_GW_ALL', 'B_JRCP_LCCP_PAYH_GW_ALL',
              'B_JRCP_LCCP_PAYH_GW_ALL1', 'B_JRCP_LCCP_PFYH_GW_ALL', 'JRCP_BX_ZGNYYH_GW_ALL', 'JRCP_BX_ZGYH_GW_ALL',
              'JRCP_BX_JTYH_GW_ALL', 'JRCP_BX_BHYH_GW_ALL', 'JRCP_BX_ZGJSY_GW_ALL', 'JRCP_BX_ZGGDYH_GW_ALL',
              'JRCP_BX_ZGGDYH_GW_ALL1', 'JRCP_BX_GFYH_GW_ALL', 'JRCP_BX_XYYH_GW_ALL', 'JRCP_BX_XYYH_GW_ALL_1',
              'JRCP_BX_ZASYH_GW_ALL', 'JRCP_BX_HFYH_GW_ALL', 'JRCP_BX_ZXYH_GW_ALL', 'JRCP_BX_HXYH_GW_ALL',
              'JRCP_BX_ZGGSYH_GW_CJ', 'JRCP_BX_ZGGSYH_GW_TCJ', 'JRCP_BX_PAYH_GW_ALL', 'B_JRCP_BX_ZGNYYH_GW_ALL',
              'B_JRCP_BX_ZGYH_GW_ALL', 'B_JRCP_BX_JTYH_GW_ALL', 'B_JRCP_BX_BHYH_GW_ALL', 'B_JRCP_BX_ZGJSY_GW_ALL',
              'B_JRCP_BX_ZGGDYH_GW_ALL', 'B_JRCP_BX_ZGGDYH_GW_ALL1', 'B_JRCP_BX_GFYH_GW_ALL', 'B_JRCP_BX_XYYH_GW_ALL',
              'B_JRCP_BX_ZASYH_GW_ALL', 'B_JRCP_BX_HFYH_GW_ALL', 'B_JRCP_BX_ZXYH_GW_ALL', 'B_JRCP_BX_HXYH_GW_ALL',
              'B_JRCP_BX_ZGGSYH_GW_TCJ', 'B_JRCP_BX_PAYH_GW_ALL', 'JRCP_JJ_ZGNYYH_GW_ALL', 'JRCP_JJ_ZGYH_GW_ALL',
              'JRCP_JJ_ZGYH_GW_ALL1', 'JRCP_JJ_ZGYH_GW_ALL2', 'JRCP_JJ_JTYH_GW_ALL', 'JRCP_JJ_BHYH_GW_ALL',
              'JRCP_JJ_ZGJSYH_GW_ALL', 'JRCP_JJ_ZGGDYH_GW_ALL', 'JRCP_JJ_GFYH_GW_ALL', 'JRCP_JJ_XYYH_GW_ALL',
              'JRCP_JJ_ZGMSYH_GW_ALL', 'JRCP_JJ_ZASYH_GW_ALL', 'JRCP_JJ_ZESYH_GW_ALL', 'JRCP_JJ_HFYH_GW_ALL',
              'JRCP_JJ_ZXYH_GW_ALL', 'JRCP_JJ_HXYH_GW_ALL', 'JRCP_JJ_ZGGSYH_GW_ALL', 'JRCP_JJ_PAYH_GW_ALL',
              'B_JRCP_JJ_ZGNYYH_GW_ALL', 'B_JRCP_JJ_ZGYH_GW_ALL', 'B_JRCP_JJ_ZGYH_GW_ALL1', 'B_JRCP_JJ_ZGYH_GW_ALL2',
              'B_JRCP_JJ_JTYH_GW_ALL', 'B_JRCP_JJ_BHYH_GW_ALL', 'B_JRCP_JJ_ZGJSYH_GW_ALL', 'B_JRCP_JJ_ZGGDYH_GW_ALL',
              'B_JRCP_JJ_GFYH_GW_ALL', 'B_JRCP_JJ_XYYH_GW_ALL', 'B_JRCP_JJ_ZGMSYH_GW_ALL', 'B_JRCP_JJ_ZASYH_GW_ALL',
              'B_JRCP_JJ_ZESYH_GW_ALL', 'B_JRCP_JJ_HFYH_GW_ALL', 'B_JRCP_JJ_ZXYH_GW_ALL', 'B_JRCP_JJ_HXYH_GW_ALL',
              'B_JRCP_JJ_ZGGSYH_GW_ALL', 'B_JRCP_JJ_PAYH_GW_ALL', 'JRCP_JJ_TTJJ_JZ_ALL', 'JRCP_JJ_TTJJ_JZ',
              'JRCP_JJ_TTJJ_FJZ_ALL', 'JRCP_JJ_TTJJ_FJZ', 'JRCP_XYK_WAK', 'JRCP_XYK_WAK_ALL',
              'ZX_CJXW_GJJRJG_GJSWZJ_GDSW', 'ZX_CJXW_GJJRJG_GJSWZJ_SWYW', 'ZX_CJXW_GJJRJG_GJSWZJ_XWFBH',
              'ZX_CJXW_GJJRJG_GJSWZJ_ZBGG', 'ZX_CJXW_GJJRJG_GJSWZJ_ZCJD', 'ZX_CJXW_GJJRJG_GJSWZJ_ZXWJ',
              'ZX_CJXW_GJJRJG_ZGQYLHH_BWXX', 'ZX_CJXW_GJJRJG_ZGQYLHH_CYDT', 'ZX_CJXW_GJJRJG_ZGQYLHH_GJCJ',
              'ZX_CJXW_GJJRJG_ZGQYLHH_HYXHDT', 'ZX_CJXW_GJJRJG_ZGQYLHH_QLDT', 'ZX_CJXW_GJJRJG_ZGQYLHH_QYJDT',
              'ZX_CJXW_GJJRJG_ZGQYLHH_QYJSCX', 'ZX_CJXW_GJJRJG_ZGQYLHH_QYYX', 'ZX_CJXW_ZYCJ_21SJJJW_CJ',
              'ZX_CJXW_ZYCJ_21SJJJW_DGW', 'ZX_CJXW_ZYCJ_21SJJJW_GD', 'ZX_CJXW_ZYCJ_21SJJJW_HG',
              'ZX_CJXW_ZYCJ_21SJJJW_JR', 'ZX_CJXW_ZYCJ_21SJJJW_QXB', 'ZX_CJXW_ZYCJ_21SJJJW_SD',
              'ZX_CJXW_ZYCJ_21SJJJW_SHY', 'ZX_CJXW_ZYCJ_21SJJJW_SYE', 'ZX_CJXW_ZYCJ_21SJJJW_XSD',
              'ZX_CJXW_ZYCJ_21SJJJW_YDYL', 'ZX_CJXW_ZYCJ_21SJJJW_ZMXX', 'ZX_CJXW_ZYCJ_CJW_HGSY', 'ZX_CJXW_ZYCJ_CJW_JR',
              'ZX_CJXW_ZYCJ_CJW_TJK', 'ZX_CJXW_ZYCJ_CJW_ZQ', 'ZX_CJXW_ZYCJ_TXCJ_HGJJ', 'ZX_CJXW_ZYCJ_XLCJ_GGKX',
              'ZX_CJXW_ZYCJ_XLCJ_GGXW', 'ZX_CJXW_ZYCJ_XLCJ_GNCJ', 'ZX_CJXW_ZYCJ_XLCJ_SSXW', 'ZX_CJXW_ZYCJ_XLCJ_YHDT',
              'ZX_CJXW_ZYCJ_XLCJ_YHFG', 'ZX_CJXW_ZYCJ_XLCJ_ZLYJ', 'ZX_GWDT_GDYH_GDXW', 'ZX_GWDT_GFYH_GFXW',
              'ZX_GWDT_GSYH_GHKX', 'ZX_GWDT_HFYH_YFXW', 'ZX_GWDT_HXYH_HXXW', 'ZX_GWDT_JSYH_DTJJ', 'ZX_GWDT_JTYH_JHXW',
              'ZX_GWDT_MSYH_MSXW', 'ZX_GWDT_NYYH_XWZX', 'ZX_GWDT_PAYH_YHXW', 'ZX_GWDT_ZGYH_ZHDT', 'ZX_GWDT_ZSYH_ZHXW',
              'ZX_GWDT_XYYH_XYDT', 'ZX_GWDT_ZSYH_WJBD', 'ZX_GWDT_ZXYH_JX', 'ZX_GWDT_PFYH_XWDT', 'ZX_GWDT_BHYH_BHXW',
              'ZX_HYBG_YDGXT_SJBG', 'ZX_HYBG_ARZX_CYYJBG', 'ZX_HYBG_ITJZ_YHBG', 'ZX_HYBG_YGZK_HYDC',
              'ZX_HYBG_PHYD_YJYDC', 'ZX_ZCGG_BJH_ZCFG', 'ZX_ZCGG_SJS_SJSGG', 'ZX_ZCGG_YJH_GGTZ', 'ZX_ZCGG_SZJS_SJSGG',
              'WD_JT_DT_BDDT_BJ', 'WD_JT_DT_BDDT_CD', 'WD_JT_DT_BDDT_NB', 'WD_JT_DT_BDDT_NN', 'WD_JT_DT_BDDT_SH',
              'WD_JT_DT_BDDT_XM', 'WD_JT_GJ_GJWZD_BJ', 'WD_JT_GJ_GJWZD_CD', 'WD_JT_GJ_GJWZD_NB', 'WD_JT_GJ_GJWZD_NN',
              'WD_JT_GJ_GJWZD_SH', 'WD_JT_GJ_GJWZD_XM', 'WD_JZ_FJ_LISPMM_CD_PAGE', 'WD_JZ_FJ_LISPZL_CD_PAGE',
              'WD_JZ_FJ_LIXQZL_CD_AREA', 'WD_JZ_FJ_LIXQZL_CD_AREA_PAGE', 'WD_JZ_FJ_LIXZLMM_CD_PAGE',
              'WD_JZ_FJ_LIXZLZL_CD_PAGE', 'WD_JZ_FJ_LJXQFJ_CD_AREA', 'WD_JZ_FJ_LJXQFJ_CD_AREA_PAGE',
              'WD_JZ_FJ_LISPMM_CD', 'WD_JZ_FJ_LISPZL_CD', 'WD_JZ_FJ_LIXQZL_CD', 'WD_JZ_FJ_LJXQFJ_CD',
              'WD_JZ_FJ_LIXZLMM_CD', 'WD_JZ_FJ_LIXZLZL_CD', 'WD_JZ_FJ_LISPMM_BJ_PAGE', 'WD_JZ_FJ_LISPZL_BJ_PAGE',
              'WD_JZ_FJ_LIXQZL_BJ_AREA', 'WD_JZ_FJ_LIXQZL_BJ_AREA_PAGE', 'WD_JZ_FJ_LIXZLMM_BJ_PAGE',
              'WD_JZ_FJ_LIXZLZL_BJ_PAGE', 'WD_JZ_FJ_LJXQFJ_BJ_AREA', 'WD_JZ_FJ_LJXQFJ_BJ_AREA_PAGE',
              'WD_JZ_FJ_LISPMM_BJ', 'WD_JZ_FJ_LISPZL_BJ', 'WD_JZ_FJ_LIXQZL_BJ', 'WD_JZ_FJ_LJXQFJ_BJ',
              'WD_JZ_FJ_LIXZLMM_BJ', 'WD_JZ_FJ_LIXZLZL_BJ', 'WD_JZ_FJ_LISPMM_NN_PAGE', 'WD_JZ_FJ_LISPZL_NN_PAGE',
              'WD_JZ_FJ_LIXQZL_NN_PAGE', 'WD_JZ_FJ_LIXZLMM_NN_PAGE', 'WD_JZ_FJ_LIXZLZL_NN_PAGE',
              'WD_JZ_FJ_LJXQFJ_NN_PAGE', 'WD_JZ_FJ_LISPMM_NN', 'WD_JZ_FJ_LISPZL_NN', 'WD_JZ_FJ_LIXQZL_NN',
              'WD_JZ_FJ_LJXQFJ_NN', 'WD_JZ_FJ_LIXZLMM_NN', 'WD_JZ_FJ_LIXZLZL_NN', 'WD_JZ_FJ_LISPMM_SH_PAGE',
              'WD_JZ_FJ_LISPZL_SH_PAGE', 'WD_JZ_FJ_LIXQZL_SH_AREA', 'WD_JZ_FJ_LIXQZL_SH_AREA_PAGE',
              'WD_JZ_FJ_LIXZLMM_SH_PAGE', 'WD_JZ_FJ_LIXZLZL_SH_PAGE', 'WD_JZ_FJ_LJXQFJ_SH_AREA',
              'WD_JZ_FJ_LJXQFJ_SH_AREA_PAGE', 'WD_JZ_FJ_LISPMM_SH', 'WD_JZ_FJ_LISPZL_SH', 'WD_JZ_FJ_LIXQZL_SH',
              'WD_JZ_FJ_LJXQFJ_SH', 'WD_JZ_FJ_LIXZLMM_SH', 'WD_JZ_FJ_LIXZLZL_SH', 'WD_JZ_FJ_LISPMM_XM_PAGE',
              'WD_JZ_FJ_LISPZL_XM_PAGE', 'WD_JZ_FJ_LIXQZL_XM_AREA', 'WD_JZ_FJ_LIXQZL_XM_AREA_PAGE',
              'WD_JZ_FJ_LIXZLMM_XM_PAGE', 'WD_JZ_FJ_LIXZLZL_XM_PAGE', 'WD_JZ_FJ_LJXQFJ_XM_AREA',
              'WD_JZ_FJ_LJXQFJ_XM_AREA_PAGE', 'WD_JZ_FJ_LISPMM_XM', 'WD_JZ_FJ_LISPZL_XM', 'WD_JZ_FJ_LIXQZL_XM',
              'WD_JZ_FJ_LJXQFJ_XM', 'WD_JZ_FJ_LIXZLMM_XM', 'WD_JZ_FJ_LIXZLZL_XM', 'WD_JZ_FJ_LISPMM_NB_PAGE',
              'WD_JZ_FJ_LISPZL_NB_PAGE', 'WD_JZ_FJ_LIXQZL_NB_AREA', 'WD_JZ_FJ_LIXQZL_NB_AREA_PAGE',
              'WD_JZ_FJ_LIXZLMM_NB_PAGE', 'WD_JZ_FJ_LIXZLZL_NB_PAGE', 'WD_JZ_FJ_LJXQFJ_NB_PAGE', 'WD_JZ_FJ_LISPMM_NB',
              'WD_JZ_FJ_LISPZL_NB', 'WD_JZ_FJ_LIXQZL_NB', 'WD_JZ_FJ_LJXQFJ_NB', 'WD_JZ_FJ_LIXZLMM_NB',
              'WD_JZ_FJ_LIXZLZL_NB', 'WD_SH_SQ_DZDPSC', 'WD_SH_XX_51SXW', 'WD_SH_YY_YFW_PROVINCE', 'WD_SH_YY_YFW_YM',
              'WD_SH_YY_YFW', 'ABCORGANIZE', 'BOCCity', 'BOCPage', 'BOCPage1', 'BOCORGANIZE', 'BOCORGANIZE1',
              'BOCOMCity', 'BOCOMArea', 'BOCOMORGANIZE', 'BOCOMORGANIZE1', 'CBHBCity', 'CBHBORGANIZE', 'CCBCity',
              'CCBProvince', 'CCBArea', 'CCBPage', 'CCBPage2', 'CCBPage3', 'CCBORGANIZE', 'CCBORGANIZE2',
              'CCBORGANIZE3', 'CGBCity', 'CGBORGANIZE', 'CGBORGANIZE1', 'CGBORGANIZE2', 'CIBORGANIZE', 'CMBCProvince',
              'CMBCORGANIZE', 'CMBCORGANIZE1', 'CMBCity', 'CMBORGANIZE', 'CMBORGANIZE1', 'CMBORGANIZE2', 'CZBORGANIZE',
              'EBCLCity', 'EBCLORGANIZE', 'ECITICORGANIZE', 'ICBCORGANIZEPAGE', 'ICBCORGANIZE1PAGE', 'ICBCORGANIZE1',
              'ICBCORGANIZE', 'PABCity', 'PABORGANIZE', 'PABORGANIZE1', 'SPDBORGANIZE', 'SPDBORGANIZE1',
              'MAPBAR_DEATAIL', 'MAPBAR_DEATAIL_BJ', 'MAPBAR_DEATAIL_FIRST_CD', 'MAPBAR_DEATAIL_CD',
              'MAPBAR_DEATAIL_FIRST_NB', 'MAPBAR_DEATAIL_NB', 'MAPBAR_DEATAIL_FIRST_XM', 'MAPBAR_DEATAIL_XM',
              'MAPBAR_DEATAIL_FIRST_NN', 'MAPBAR_DEATAIL_NN','MAPBAR_DEATAIL_FIRST_FS','MAPBAR_DEATAIL_FS','MAPBAR_DEATAIL_FIRST_SJZ','MAPBAR_DEATAIL_SJZ']

class ConnMySQLLCA(object):

    def __init__(self):
        """
        连接数据库
        :return:
        """
        self.conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='spder_product', charset='utf8')

    def insert_data(self, table_name, data):
        """
        添加数据
        :param tablename: 表名
        :param data: 添加数据(元祖转换为字符串)
        :return:
        """
        sql = "insert into {} values {};".format(table_name,data)
        with self.conn.cursor() as cur:
            try:
                self.conn.ping(reconnect=True)
                cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)
                self.conn.rollback()
        self.conn.close()

    def delete_data(self,table_name, condition=None):
        """
        删除表中数据
        :param tablename: 表名
        :param condition: 条件
        :return:
        """
        sql = "delete from {} where {};".format(table_name, condition)
        with self.conn.cursor() as cur:
            try:
                self.conn.ping(reconnect=True)
                cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)
                self.conn.rollback()
        self.conn.close()

    def updata_data(self, table_name, data, condition):
        """
        更新列表中的数据
        :param table_name: 表名
        :param data: 更新数据
        :param condition: 条件
        :return:
        """
        sql = "update {} set {} where {};".format(table_name, data, condition)
        with self.conn.cursor() as cur:
            try:
                self.conn.ping(reconnect=True)
                cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)
                self.conn.rollback()
        self.conn.close()

    def select_data(self, table_name, condition,fields='*'):
        """
        查询数据
        :param table_name: 表名
        :param fields: 查询字段
        :return:
        """
        sql = "select {} from {} where {};".format(fields, table_name, condition)
        with self.conn.cursor() as cur:
            try:
                self.conn.ping(reconnect=True)
                cur.execute(sql)
                results = cur.fetchall()
                return results
            except Exception as e:
                print(e)
            self.conn.close()


if __name__ == '__main__':
    for i in jrcp_codes:
        try:
            result = ConnMySQLLCA().select_data(table_name='spi_scra_entity',condition=f'CODE_="{i}"',fields='NAME_')
            print(result[0][0])
        except:
            print('********')

