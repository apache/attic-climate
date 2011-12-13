<?php
/**
 * CLAP: Command Line Argument Parser
 * Class for parsing command line arguments. Understands any combination of
 * the following argument types:
 *
 * 	--foo		(boolean flag argument)
 * 	--foo=bar	(named assignment argument)
 *  foo			(plain old argument value)
 *
 *  Returns the processed command line arguments as a php array.
 *
 *  Example:
 *
 *  script.php --foo --bar=baz somefile.xml someotherfile.xml
 *
 *  output: array(4) {
 *  	['foo'] => bool(true)
 *  	['bar'] => string(3) "baz"
 *  	[0] => string(12) "somefile.xml"
 *  	[1]	=> string(17) "someotherfile.xml"
 *  }
 *
 */
class CLAP {

	/**
	 * parse: Take a string and process it for arguments.
	 * @param $argv (array) an array of command line arguments as
	 * 			provided by the command line (argv)
	 * @return (array) a usable array representation of the arguments
	 */
	public static function parse($argv) {
		array_shift($argv);
		$out = array();
		foreach ($argv as $arg){
			if (substr($arg,0,2) == '--'){
				$eqPos = strpos($arg,'=');
				if ($eqPos === false){
					$key = substr($arg,2);
					$out[$key] = isset($out[$key]) ? $out[$key] : true;
				} else {
					$key = substr($arg,2,$eqPos-2);
					$out[$key] = substr($arg,$eqPos+1);
				}
			} else if (substr($arg,0,1) == '-'){
				if (substr($arg,2,1) == '='){
					$key = substr($arg,1,1);
					$out[$key] = substr($arg,3);
				} else {
					$chars = str_split(substr($arg,1));
					foreach ($chars as $char){
						$key = $char;
						$out[$key] = isset($out[$key]) ? $out[$key] : true;
					}
				}
			} else {
				$out[] = $arg;
			}
		}
		return $out;
	}
}