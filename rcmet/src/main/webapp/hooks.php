<?php
/**
 * Copyright (c) 2010, California Institute of Technology.
 * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 * 
 * $Id$
 * 
 * 
 * OODT Balance
 * Web Application Base Framework
 */
/**
 * HOOKS.PHP
 * 
 * Hooks provide the ability, as the name implies, to hook into various parts of 
 * the view rendering process and insert customizations. The contents of these 
 * functions are run at the appropriate time *EVERY* time a view is rendered, i.e.
 * the content of the hooks is not by default view-specific but rather will be 
 * applied to all views. (However, there is nothing that prevents developers from 
 * inserting conditional logic inside a hook that then causes view-specific
 * them to exhibit view-specific behavior).
 * 
 * As an example, consider a hook that adds the amount of time Balance took to render
 * the page as an inline HTML comment at the bottom of each page after it has been sent:
 * 
 * function hook_after_send() {
 *     $timeStart = $GLOBALS['balance_request_start'];
 *     $timeNow   = microtime(true);
 *     $elapsed   = $timeNow - $timeStart;
 *     echo "<!-- page rendered in {$elapsed} seconds -->";
 * }
 * 
 * 
 * Take a look at the docblock descriptions of each hook to get a sense of where
 * in the view rendering process the hook is invoked.
 * 
 * @author ahart
 */

/**
 * hook_before_header
 * 
 * This hook is executed before the contents of the header file are processed.
 */
function hook_before_header() {}

/**
 * hook_before_view
 * 
 * This hook is executed before the contents of the main view are processed.
 */
function hook_before_view() {}

/**
 * hook_before_footer
 * 
 * This hook is executed before the contents of the footer are processed
 */
function hook_before_footer() {}

/**
 * hook_before_send
 * 
 * This hook is after all of the view components (header, view, footer) have been
 * processed but before the processed results are sent out across the wire to the 
 * browser. HTTP headers have not yet been sent to the browser.
 */
function hook_before_send() {}

/**
 * hook_after_send
 * 
 * This hook is after all of the view components (header, view, footer) have been
 * processed and sent out across the wire to the browser. It can be used for logging
 * or analytics purposes, or to append a common trailer to all content.
 */
function hook_after_send() {
	$timeStart = $GLOBALS['balance_request_start'];
	$timeEnd   = microtime(true);
	$elapsed   = $timeEnd - $timeStart;
	
	echo "\r\n<!-- page rendered in {$elapsed} seconds -->";
}