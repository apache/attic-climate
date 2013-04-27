<?php
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

$module = App::Get()->loadModule();

// Pass the installed site root to javascript                                                                   
App::Get()->response->addJavascript("var site_root = '" . SITE_ROOT . "';",true);
				
// Don't show a header or footer on this view
App::Get()->response->useHeaderFile(false);
App::Get()->response->useFooterFile(false);

// Include the main Puny class
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');

// Load the requested resource
$resource = Puny::load(App::Get()->request->segments[0]);

// Get the raw contents
$content = $resource->getContent(true);
?>

<!-- JAVASCRIPTS -->
<!-- STYLESHEETS -->
<script type="text/javascript">
	$(document).ready(function() {
		$.GollumEditor();
	});
</script>


<div id="wiki-wrapper" class="edit outer">
  <div id="head">
    <h1>Editing <strong><?php echo $resource->getId();?></strong></h1>
    <p>(latest version: <?php echo $resource->getVersion();?>)</p>
  </div>
  <div id="wiki-content">
		<div id="gollum-editor" data-escaped-name="Home" class="edit">
				<input type="hidden" id="punyResourceId" name="punyResourceId" value="<?php echo $resource->getId()?>"/>

					<div id="gollum-editor-function-bar">
						<div id="gollum-editor-function-buttons">
							<a href="#" id="function-h1" class="function-button" title="Header 1" tabindex="-1"> 
								<span>Header 1</span> </a>
							<a href="#" id="function-h2" class="function-button" title="Header 2" tabindex="-1">
								<span>Header 2</span> </a> 
							<a href="#" id="function-h3" class="function-button" title="Header 3" tabindex="-1">
								<span>Header 3</span> </a> 
							<span class="function-divider">&nbsp;</span> 
							<a href="#" id="function-internal-link" class="function-button" title="Wiki Link" tabindex="-1">
								<span>Wiki Link</span> </a> 
							<a href="#" id="function-link" class="function-button" title="Link" tabindex="-1">
								<span>Link</span> </a>
							<a href="#" id="function-image" class="function-button" title="Image" tabindex="-1">
								<span>Image</span> </a> 
							<span class="function-divider">&nbsp;</span>
							<a href="#" id="function-bold" class="function-button" title="Bold" tabindex="-1">
								<span>Bold</span> </a>
							<a href="#" id="function-italic" class="function-button" title="Italic" tabindex="-1">
								<span>Italic</span> </a>
							<a href="#" id="function-code" class="function-button" title="Code" tabindex="-1">
								<span>Code</span> </a> 
							<span class="function-divider">&nbsp;</span>
							<a href="#" id="function-ul" class="function-button" title="Unordered List" tabindex="-1">
								<span>Unordered List</span> </a> 
							<a href="#" id="function-ol" class="function-button" title="Ordered List" tabindex="-1">
								<span>Ordered List</span> </a>
							<a href="#" id="function-blockquote" class="function-button" title="Blockquote" tabindex="-1">
								<span>Blockquote</span> </a>
							<a href="#" id="function-hr" class="function-button" title="Horizontal Rule" tabindex="-1">
								<span>Horizontal Rule</span> </a> 
							<span class="function-divider">&nbsp;</span>
							<a href="#" id="function-help" class="function-button" title="Help" tabindex="-1">
								<span>Help</span> </a>
						</div>

						<div id="gollum-editor-format-selector">
							<!--  <select id="wiki_format" name="wiki[format]">
								<option value="asciidoc">AsciiDoc</option>
								<option value="creole">Creole</option>
								<option value="markdown" selected="selected">Markdown</option>
								<option value="mediawiki">MediaWiki</option>
								<option value="org">Org-mode</option>
								<option value="pod">Pod</option>
								<option value="rdoc">RDoc</option>
								<option value="textile">Textile</option>
								<option value="rest">reStructuredText</option>
							</select> -->
							<label id="wiki_format" name="wiki[format]">Markdown</label>
							<label for="wiki_format">Edit Mode</label>
						</div>
					</div>

					<div id="gollum-editor-help" class="jaws" data-autodisplay=&quot;true&quot;>
						<ul id="gollum-editor-help-parent">
							<li></li>
						</ul>
						<ul id="gollum-editor-help-list">
							<li></li>
						</ul>
						<div id="gollum-editor-help-wrapper">
							<div id="gollum-editor-help-content">
								<p></p>
							</div>
						</div>
					</div>
 
					<div id="gollum-error-message"></div>
					<textarea data-markup-lang="markdown" format="markdown"
						id="gollum-editor-body" name="punyContent"><?php echo stripslashes($content)?></textarea>
<!-- Edit Message -->
					<!--<div id="gollum-editor-edit-summary" class="singleline">
						<label class="jaws" for="wiki_commit">Edit Message</label> 
						<input id="gollum-editor-message-field" name="wiki[commit]"
							placeholder="Write a small message here explaining this change. (Optional)"
							type="text" />
					</div> -->

					<span class="jaws"><br> </span> 
					<input id="gollum-editor-submit" class="gollum-editor-input" name="commit"
						title="Save current changes" type="submit" value="Save" />
					<input id="gollum-editor-cancel" class="gollum-editor-input" name="cancel"
						title="Cancel changes" type="submit" value="Cancel" />
		</div>
	</div>
</div>
