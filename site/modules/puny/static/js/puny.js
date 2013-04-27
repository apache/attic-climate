/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Puny - A light-weight content editor for Balance applications
 * 
 * This library depends on JQuery v 1.4.1 or higher (http://www.jquery.com)
 */
$(document).ready(function() {
	
	// Support click-to-edit on puny elements
	$('[puny]').live('click',function(event) {
		punyInitEditor($(this));
	});
	// Enable the editor save button
	$('#gollum-editor-submit').live('click', punyPersistChanges);
	// Enable the editor cancel button
	$('#gollum-editor-cancel').live('click', punyCancel);
	
});

var editingResourceId = false;


function punyInitEditor ( elmt ) {
	editingResourceId = elmt.attr('puny');
	window.location = puny_module_root + '/edit/' + editingResourceId;
};

function punyCancel() {
	window.location = puny_current_url;
}

function punyPersistChanges(event) {
	editingResourceId = $('#punyResourceId').val();
	$.post( puny_module_root + '/store.do',{
		'resourceId' : editingResourceId
		, 'content'  : $('#gollum-editor-body').val()
	},function( data ) {
		window.location = puny_current_url;
	}, 'json');
}
