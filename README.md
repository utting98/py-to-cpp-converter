# py-to-cpp-converter

NOTE: Full code rework currently in progress to remove line by line string replacement, using AST tree instead then replacing node wise, see the folder files for how this approach is currently being worked once it is up to date with what the string replacement method could do it will be fully documented, the information below corresponds to the top level string replacement method.


This project is a work in progress python script that will read in another python script and attempt to convert it to a C++ program via line by line conversion and file writeout. In the first instance it will be written only to handle base library python, possibly extending in the future.


To use the script scroll to the bottom of the PytoCpp.py file and you will find three lines not in any functions. To the first write in the name of the python script you are attempting to convert. To the third line write out the name you want the C++ file to have.

If there are any function calls within your python script, there is a space within the PytoCpp script below line 700 where you must write out a typical call for this function in a comment. An example of this is given in the code. Instead of writing a function call with any variables, write it with the raw values. The example given is: #TestFunction(1,[2.2,3.3,4.4],'Hello',2.2). It is required to do this to assist the code in determining the variable types for each variable in the function definition as is required by C++ (and not by python).

As previously mentioned the project is not finished, this is the list of commands able to be converted:

Comments[1]

Integer declaration

Float declaration

String declaration

Print statements

If statements

Elif statements

Else statements

Pass command

Simple maths

Function definitions

Function returns

Function calls

For loops

List declarations

List append commands

List element access/overwrite

Store list elements under a variable

[1]Please note that currently comments can only be converted if they are on their own line, this is to avoid converting strings to comments incorrectly

For the best example of syntax to follow in your python script to maximise conversion accuracy please refer to the Test.py python script within this repository. Attempts to nest these functions that can be converted have not been made so may also cause issue as this is untested. IF you find any issues with the conversion after following the Test.py syntax please flag them and I will address them when I can. If any lines fail conversion the line will be formatted as //Failed Conversion - [Python line], such that users can see what failed and easily look up and fix the conversion for any failed lines.

If you have a knowledge of both python and C++ please feel free to contribute to this project as it will be a huge undertaking by myself. IF you do contribute please ensure you document all of your code to help me and any other contributers understand your additions.
