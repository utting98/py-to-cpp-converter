# py-to-cpp-converter

This project is a work in progress python script that will read in another python script and attempt to convert it to a C++ program via accessing and replacing AST nodes with relevant C++ commands and file writeout. In the first instance it will be written only to handle base library python, possibly extending in the future.

To use the script scroll to the bottom of the PytoCpp.py file where there is two function calls to edit for your conversion.

```
converted_data = main('Test.py','CallTest.py')
write_file(converted_data,'Test.cpp')
```

The arguments of these functions constitute operation of the program, main takes arguments of: File_to_convert, Script_of_function_calls_with_example_values. For an example of each script see the Test.py script and CallTest.py script respectively. The CallTest.py script is required because functions could have variables passed to them instead of raw data values. This is an issue because the code attempts to determine what each variable type in a function is for the C++ function definition, the workaround is providing example inputs in the CallTest.py script from which the types are determined. Call examples also have to be made for classes and functions within classes, see the Test.py and CallTest.py scripts for an example. The second argument in the write_file function is the name of the output file to write. If no file name is specified the default will be Output.cpp

As previously mentioned the project is not finished, this is the list of commands able to be converted:

Integer declaration

Float declaration

String declaration

Print statements

If statements

Elif statements

Else statements

Pass command

Operator separated variables/numbers

Function definitions

Function returns

Function calls

For loops

List declarations (not empty)

List append commands

List element access/overwrite

Store list elements under a variable

While loops

Boolean statements

Basic class definitions / OOP

Input commands

List declarations (empty) (requires some user input to console but user is walked through it)

Simple file reading (note to user: either specify full path when opening the file, OR if you compile code with visual studio, when testing put file in ./solution_name/solution_name, where a .proj, .filters and .user are)

TODO:

Test advanced class definitions

Nesting more if statements inside a final else statement, currently causes an issue where the first if inside it becomes an else if

See @todo comments in PytoCpp.py for known bugs / missing features to work on

More base python functions e.g. reversed, type etc

File writing

Also see Test.py for show of currently convertible functions, each time one is added I update the Test.py script to include it to show that it works.

If you have a knowledge of both python and C++ please feel free to contribute to this project as it will be a huge undertaking by myself. If you do contribute please ensure you document all of your code to help me and any other contributers understand your additions.
