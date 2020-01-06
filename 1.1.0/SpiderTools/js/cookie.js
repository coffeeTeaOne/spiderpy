function ZGQYXYCookie(user_agent,script) {
    function a() {
        function a(a, b) {
            var c, d = 0;
            for (c = 0; c < b.length; c++) d |= h[c] << 8 * c;
            return a ^ d
        }
        var b = user_agent,
        f, g, h = [],
        k = 0;
        for (f = 0; f < b.length; f++) g = b.charCodeAt(f),
        h.unshift(g & 255),
        4 <= h.length && (k = a(k, h), h = []);
        0 < h.length && (k = a(k, h));
        return k.toString(16)
    }
    function b() {
        for (var a = 1 * new Date,
        b = 0; a == 1 * new Date;) b++;
        return a.toString(16) + b.toString(16)
    }
    
    function cn() {
        return Math.floor(2147483648 * Math.random()) + "-" + Math.round(new Date() / 1000) + "-" + "http%253A%252F%252Fsh.gsxt.gov.cn%252F%7C" + Math.round(new Date() / 1000)
    }



    function jsl_clearanc () {

        function setTimeout(a,b) {
            return 1
        }

        function cdocument(){
             this.cookie = {};
             this.createElement = function (a) {
                 return {'firstChild':{'href':'http://sh.gsxt.gov.cn/index.html'}}
             }
             this.addEventListener = function () {
                if (arguments.length == 0) return true;
                if (arguments.length > 1) arguments[1]();
            }
            this.attachEvent = function () {
                if (arguments.length > 1) arguments[1]();
            }

          }

        document = new cdocument;

        function cwindow() {
            this.headless = false;

        }

        window = new cwindow;

        eval(script);
    return document.cookie;
    }



    return function () {
        var cookie = {};
        var fbl = [1024000,1296000,1764000];
        var rf = fbl[Math.round(Math.random()*(fbl.length-1))];
        var c = rf.toString(16);

        cookie.UM_distinctid = b() + "-" + Math.random().toString(16).replace(".", "") + "-" + a() + "-" + c + "-" + b();
        
        cookie.CNZZDATA1261033118 = cn();

        cookie.__jsl_clearance=jsl_clearanc().replace('__jsl_clearance=','').split(';')[0];

        //return '"UM_distinctid" : ' + '"' + b() + "-" + Math.random().toString(16).replace(".", "") + "-" + a() + "-" + c + "-" + b() + '"';
        return cookie;
    }();
};


function location_info (item) {
    aa = []
	for (x in item)
	   aa.push(String.fromCharCode(item[x]));
	return aa.join("")
}

function token (item) {
    aa = []
	for (x in item)
	   aa.push(String.fromCharCode(item[x]));
	return aa.join("")
}