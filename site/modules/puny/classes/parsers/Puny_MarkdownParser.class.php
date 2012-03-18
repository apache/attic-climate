<?php

// Require the markdown php library (https://github.com/michelf/php-markdown/)
require_once( App::Get()->settings['puny_module_path'] . '/libs/markdown.php');

/**
 * Markdown implementation of the Puny_Parser class
 * 
 * @author ahart
 */

class  Puny_MarkdownParser {
	
	public function parse ( $content ) {
		
		return Markdown( $content );
		
	}
	
}