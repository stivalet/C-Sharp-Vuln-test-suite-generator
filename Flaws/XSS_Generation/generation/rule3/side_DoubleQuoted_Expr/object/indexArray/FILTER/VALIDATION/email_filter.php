<!-- 
Safe sample
File : use of untrusted data in one side of a double quoted expression in a script
input : get the field userData from the variable $_GET via an object, which store it in a array
Flushes content of $sanitized if the filter email_filter is not applied -->

<!--Copyright 2014 Herve BUHLER, David LUCAS, Fabien NOLLET, Axel RESZETKO

Permission is hereby granted, without written agreement or royalty fee, to

use, copy, modify, and distribute this software and its documentation for

any purpose, provided that the above copyright notice and the following

three paragraphs appear in all copies of this software.


IN NO EVENT SHALL AUTHORS BE LIABLE TO ANY PARTY FOR DIRECT,

INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 

USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF AUTHORS HAVE

BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


AUTHORS SPECIFICALLY DISCLAIM ANY WARRANTIES INCLUDING, BUT NOT

LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A

PARTICULAR PURPOSE, AND NON-INFRINGEMENT.


THE SOFTWARE IS PROVIDED ON AN "AS-IS" BASIS AND AUTHORS HAVE NO

OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR

MODIFICATIONS.-->

<!DOCTYPE html>
<html>
<head>
<script>
<?php
class Input{
	private $input;

	public function getInput(){
		return $this->input['realOne'];
	}
	
	public  function __construct(){
		$this->input = array();
		$this->input['test']= 'safe' ;
		$this->input['realOne']= $_GET['UserData'] ;
		$this->input['trap']= 'safe' ;
	}
}
$temp = new Input();
$tainted =  $temp->getInput();		
		
if (filter_var($tainted, FILTER_VALIDATE_EMAIL)) 
$checked_data = $sanitized ;
else
$checked_data = "" ;
echo "x=\"". $checked_data."\"" ;
?>
</script>
</head>
<body>
<h1>Hello World!</h1>
</body>
</html>