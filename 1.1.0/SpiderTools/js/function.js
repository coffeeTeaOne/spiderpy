function exp(jsondata,param) {
    var jsond = jsondata;
    function jsonpath(bb) {
         return jsonPath(jsond,bb);
     }
     var aa = eval(param);
     return aa;
}

// function Templet(fun) {
//
//              function reference(a){
//                  return a;
//              }
//
//               function jsonpath(b){
//                 try {
//                   if(b.indexOf(".") == 13 || b.indexOf(".") == 14){
//                         var bb = b.split('.');
//                         var cc = "reference('" + bb[0].split('(')[1].split(')')[0] +"')";
//                         var vv = eval(cc);
//                         return [vv,bb[1]];
//                     }
//               }catch (e){
//                 return b;
//               }
//               return b;
//               }

             //  var aa = eval(fun);
             //  return aa;
             // }

function Templet(data,expr) {
    var reference = data

    function jsonpath(b){
                try {
                  if(b.indexOf(".") == 13 || b.indexOf(".") == 14){
                        var bb = b.split('.');
                        var cc = "reference('" + bb[0].split('(')[1].split(')')[0] +"')";
                        var vv = eval(cc);
                        return [vv,bb[1]];
                    }
              }catch (e){
                return b;
              }
              return b;
              }

    return eval(expr)
}
