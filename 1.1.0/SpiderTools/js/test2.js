function exe(json,x,y,experence){
		function getJson(param) {
	     return jsonPath(json,param)
	 }
 	 x = getJson(x);
 	 y = getJson(y);
	 var a = eval(experence);
 	 return a;
}