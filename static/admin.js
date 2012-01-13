function deletecomment(key){
	var reason = prompt("What is the reason for deleting this comment?","");
	if(reason != null){
		$("#reason_"+key).attr("value",reason);
		$("#form_"+key).submit();
	}
}

function deletearticle(){
	var result = confirm("Are you sure you want to delete this article?");
	if(result){
		$("#hiddenDelete").val("delete");
		document.forms["deleteArticle"].submit();
	}
}