function pad_b16_zero(n, len)
{
	var s;
	
	s = parseInt(n,10).toString(16);
	if (s.length < len)
	{
		s = ('00000000' + s).slice(-len);
	}
	return s;
}

function encode_ihd_msg(s)
{
	var hex = "";
	var x = unescape(encodeURI(s));
	for (var i=0; i<x.length; i++)
	{
		hex += ""+x.charCodeAt(i).toString(16);
	}
	
	return hex;
}

function decode_ihd_msg(hex)
{	
	var s = "";
	for (var i=0; i<hex.length; i+=2)
	{
		s += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
	}
	
	return decodeURI(escape(s));
}

function get_appr_ws_url()
{
	var pcol;
	var u = document.URL;
	
	if (u.substring(0, 5) == "https")
	{
		pcol = "wss://";
		u = u.substr(8);
	}
	else
	{
		pcol = "ws://";
		if (u.substring(0, 4) == "http")
			u = u.substr(7);
	}
	
	u = u.split('/');
	
	return (pcol + u[0] + ":9000");
}

Array.prototype.contains = function (elm)
{
	for (var i=0; i<this.length; i++)
		if (this[i] == elm) return true;
	return false;
}

function ws_init(f_onopen, f_onclose, f_onerror, f_onmsg)
{
	var _ws;
	
	try
	{
		if (typeof(WebSocket) != "undefined")
			_ws = new WebSocket(get_appr_ws_url());
		else if (typeof(MozWebSocket) != "undefined")
			_ws = new MozWebSocket(get_appr_ws_url());
		else
			return null;
			
		_ws.onopen = function (evt) { f_onopen(evt) };

		_ws.onclose = function (evt) { f_onclose(evt) };

		_ws.onerror = function (evt) { f_onerror(evt) };
			
		_ws.onmessage = function (evt) { f_onmsg(evt) };
			
		return _ws;
	}	
	catch (exception)
	{
		alert("WebSocket Error: " + exception);
	}
}