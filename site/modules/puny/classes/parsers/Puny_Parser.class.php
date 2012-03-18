<?php
/**
 * Puny_Parser
 * 
 * Base class for Puny parser implementations. 
 * 
 * @abstract
 * 
 * @author ahart
 */
abstract class Puny_Parser {
	
	/**
	 * Implementations of this function should return the 
	 * final (display-ready) version of the provided content.
	 * 
	 * @param string $content The content to parse
	 * @returns string
	 * @abstract
	 */
	public abstract function parse( $content );
	
}