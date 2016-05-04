$(document).ready(function() {
	init();
	add_events();
});

var clickEventType=((document.ontouchstart!==null)?'click':'touchstart');

function onDeviceReady() {
	document.addEventListener("backbutton", onBackKeyDown, false);
	document.addEventListener("menubutton", onMenuKeyDown, false);
}
function init() {
	document.addEventListener("deviceready", onDeviceReady, false);
	$('#backoffice_login').submit();
}

function onMenuKeyDown() {
	go_home();
}
function onBackKeyDown() {
	go_home();
}

function add_events() {
	$('#enterCode').bind(clickEventType, function() {
		enter_bar_code();
		return false;
	});
}

