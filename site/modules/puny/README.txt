Puny - Lightweight content editor for Balance applications
==========================================================

Puny is a lightweight content editing module for Balance applications. Puny makes
it easy for developers to add user-editable sections of content to their application
views and supports real-time, in-place editing of the content.

Overview
--------

Puny makes it easier to separate content from presentation and separate the 
role of the site developer and the content manager. As its name implies, it
provides the bare minimum necessary to accomplish this -- based on the 
understanding that excellent, full-fledged Content Management System options
are readily available and more appropriate for content-heavy sites. Puny simply 
provides a way for sites that are not generally suited to a CMS to nevertheless
reap the benefits of real-time, in-browser content editing by a user not 
intimately familiar with HTML.

How it Works
------------

Developers embed 'containers' in their views, and content editors provide the
content that get displayed in the containers. Puny loads up the most recent 
version of the content from the data store, renders it using the specified 
parser, and places the rendered text into the view container. 

By logging in with the editor credentials, a user can visually see the editable
'containers' on the application views, and, using a javascript-enabled browser,
can provide inline, real-time edits, creating a new version of the content.



### Flexibility ###

Puny has been designed so that it is easy to plug in custom back end data
stores (MySql, MongoDB, SQLite, etc) and template engines (Markdown, Textile,
bbcode, etc). If a driver for <insert data store or parser here> doesn't exist, 
there are two primary extension points: Puny_DataStore (a base class for developing 
drivers for data stores), and Puny_Parser (a base class for interfacing with text 
parsers and template engines). Using the examples in the /classes/data and 
/classes/parsers, it should be relatively easy to develop additional drivers.


Installation
------------

Copy the Puny module (this directory) to the /modules directory of
your Balance application. 


Configuration
-------------

All configuration for Puny takes place in the module's 'config.ini' file. See
the inline documentation in 'config.ini' for detailed information about each
configuration option. 


Developer Guide
---------------

### Including Puny in your application

In general, Puny needs to be available on each application view. To avoid having to load 
the module at the top of each view, it is possible to include the module once,in the 
Balance index.php at the root of your application. Simply add the following lines to the 
'index.php' file where it says 'Initialize any globally required modules here':

// Puny initialization
App::Get()->loadModule('puny');
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');


### Installing your data store ###

Look in the /schemas folder in the Puny module for a schema compatible with your datastore
driver. Install the schema using whatever method is most appropriate for the technology. The
default driver is the PDO driver implemented in ./classes/data/Puny_PdoDataStore.class.php.
The MySQL schema compatible with this driver is in ./schemas/puny.pdo.mysql.sql. Copy this
file and import it into the database you configured in the configuration step above.


### Including Puny containers in your application views ### 

The easiest way to include Puny containers in your application views is:

<?php echo Puny::container()->load('resourceid');?>

By default, container creates a '<div>' element and loads the content into it. To use
something other than a '<div>' simply specify the html element to the container() function:

<?php echo Puny::container('span')->load('resourceid');?>

It is also possible to specify arbitrary attributes to attach to your container. Examples 
include a DOM id, CSS class(es), style attribute, alt, rel, or anything else. This is 
accomplished by passing an associative array as the second parameter to container() where
the array keys are the attribute names, and the values are the attribute values. 

<?php echo Puny::container('div',array('id'=>'mydiv','class'=>'foo bar'))->load('resourceid');?>


### Allowing editors to log in and edit ###

Somewhere in your application, there should be a login link that allows editors to log in
and make edits to content. This is easily accomplished by adding the following line wherever
you want the login link to appear:

<?php echo Puny::status();?>

This will display either a login or logout link, depending on whether or not an editor
is currently logged in. 


That's all there is to it, it lives up to its name.