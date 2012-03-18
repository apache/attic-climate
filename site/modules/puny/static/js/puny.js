/**
 * Puny - A light-weight content editor for Balance applications
 * 
 * This library depends on JQuery v 1.4.1 or higher (http://www.jquery.com)
 */
$(document).ready(function() {
	
	// Add the overlay div to the body
	$('body').append($editor_overlay);
	// Add the editor div to the body
	$('body').append($editor);
	
	// Support click-to-edit on puny elements
	$('[puny]').live('click',function(event) {
		punyInitEditor($(this));
	});
	// Enable the editor save button
	$('.punyEditor .save').live('click', punyPersistChanges);
	// Enable the editor cancel button
	$('.punyEditor .cancel').live('click',punyCloseEditor);
	
});

var editingResourceId = false;
	
var $editor_overlay = $('<div/>').attr('id','editor_overlay');

var $editor = $('<div/>').attr('id','editor_container')
	.append($('<div/>')
		.attr('id','editor_contents'));

	
function punyInitEditor ( elmt ) {
	editingResourceId = elmt.attr('puny');
	$('#editor_overlay').fadeTo(200,0.8);
	$('#editor_container').show();
	$.get( puny_module_root + '/edit/' + editingResourceId,{},function(data) {
		var $data = $(data);
		$('#editor_contents').html(data);
	},'html');
};

function punyCloseEditor(event) {
	event.preventDefault();
	$('#editor_overlay').hide();
	$('#editor_contents').html('');
	$('#editor_container').hide();
	editingResourceId = false;
}

function punyPersistChanges(event) {
	$.post( puny_module_root + '/store.do',{
		'resourceId' : editingResourceId
		, 'content'  : $('#punyContent').val()
	},function( data ) {
		$('[puny="'+editingResourceId+'"]').html(data.parsedContent)
		punyCloseEditor(event);
	}, 'json');
}
