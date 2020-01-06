# encoding: utf-8
class HttpCode:
    def get_code_info(self,code):

        str = ''

        if code == '400':
            str =  '客户端请求有语法错误，不能被服务器所理解'
        if code == '401':
            str = '请求未经授权'
        if code == '403':
            str = '禁止访问，服务器收到请求，但是拒绝提供服务'
        if code == '404':
            str = '服务器无法取得所请求的网页，请求资源不存在'
        if code == '405':
            str = '用户在Request-Line字段定义的方法不允许'
        if code == '406':
            str = '根据用户发送的Accept拖，请求资源不可访问'
        if code == '408':
            str = '客户端没有在用户指定的时间内完成请求'
        if code == '411':
            str = '服务器拒绝用户定义的Content-Length属性请求'

        if code == '500':
            str = '服务器遇到错误，无法完成请求'
        if code == '501':
            str = '未实现'
        if code == '502':
            str = '网关错误'

        if str:
            str = '其它错误信息'

        return '状态码:%s,%s' % (code, str)

