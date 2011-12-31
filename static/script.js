function deleteComment(comment){
	var choice = confirm("Are you sure you want to delete your comment?");
	if(choice){
		$("#deleteComment_"+comment).submit();
	}
}

function editComment(comment){
	link = $("#edit_"+comment);
	link.html("cancel");
	link.attr('onclick', "cancelEdit('"+comment+"')");
	div = $("#div_"+comment);
	div.append("<div class='editAppendDiv' id='divAppend_"+comment+"'> <form name='edit' action='/editcommentpost' method='post'><input type='hidden' name='commentKey' value='"+comment+"' /><textarea name='commentBody' cols='50' rows='6'>"+$("#commentBody_"+comment).html()+"</textarea><br /><input type='submit' value='Save' /></form></div>");
}

function cancelEdit(comment){
	link = $("#edit_"+comment);
	link.html("edit");
	link.attr('onclick', "editComment('"+comment+"')");
	$("#divAppend_"+comment).remove();
}

function reply(comment){
	link = $("#reply_"+comment);
	link.html("cancel");
	link.attr('onclick', "cancelReply('"+comment+"')");
	div = $("#div_"+comment);
	div.append("<div class='replyAppendDiv' id='divAppend_"+comment+"'> <form name='reply' action='/replypost' method='post'><input type='hidden' name='commentKey' value='"+comment+"' /><textarea name='commentBody' cols='50' rows='6'></textarea><br /><input type='submit' value='Reply' /></form></div>");
}

function cancelReply(comment){
	link = $("#reply_"+comment);
	link.html("reply");
	link.attr('onclick', "reply('"+comment+"')");
	$("#divAppend_"+comment).remove();
}