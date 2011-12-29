function deletecomment(key){
	var reason = prompt("What is the reason for deleting this comment?","");
	$("#reason_"+key).attr("value",reason);
	$("#form_"+key).submit();
}