# Localization-Translation-Utility
Script for simplifying the process of translating Language (.lang) files

Supports MineOS lang files, which is the main purpose of this project's existance

All you have to do in put this program in the same folder (directory) as a file named "English.lang" (can be changed by changing "READ" variable in script) and run the program.
There is a text-based interface;
Version 1 would have you copy-paste a big chunk of data into a translator and copy-paste the result back into the program, but this is slow and doesn't work very well.
Version 2 added the capability to translate a file automatically to a given language if you know it's language code, as defined by ISO 639-1. Using the function 
`automated_translation` with a list of language codes as an argument will translate the file defined by the READ variable ('English.lang' on default) to all of the languages listed, and save them as "<language_name>.lang" in a folder named "Translated" in the current directory.


Versions:
1.0.0 - Initial release
2.0.0 - Adding auto translation and general clean-up
