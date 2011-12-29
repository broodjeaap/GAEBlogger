function deletecomment(key){
	var reason = prompt("What is the reason for deleting this comment?","");
	if(reason != null){
		$("#reason_"+key).attr("value",reason);
		$("#form_"+key).submit();
	}
}