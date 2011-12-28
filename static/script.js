function reply(comment){
	link = $("#link_"+comment);
	link.html("cancel");
	link.attr('onclick', "cancel('"+comment+"')");
	
	div = $("#div_"+comment);
	div.append("<div class='replyAppendDiv' id='divAppend_"+comment+"'> <form name='reply' action='/replypost' method='post'><input type='hidden' name='commentKey' value='"+comment+"' /><textarea name='commentBody' cols='50' rows='6'></textarea><br /><input type='submit' value='Reply' /></form></div>");
	
}

function cancel(comment){
	link = $("#link_"+comment);
	link.html("reply");
	link.attr('onclick', "reply('"+comment+"')");
	$("#divAppend_"+comment).remove();
}