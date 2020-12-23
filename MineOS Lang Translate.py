#!/usr/bin/env python3
# English to other lang file converter.
# -*- coding: utf-8 -*-

# Semi-compadable with Google Translate.
# If system breaks in bad translator mode, use the last
# number (ex. 28) in the function "getField" for the text
# accociated with that number.

# Can use input from other files by changing the filename of
# the variable READ below.

# For Lolcat use with https://funtranslations.com/lolcat, good translator

# Programmed by CoolCat467

__title__ = 'English to Lolcat lang file converter'
__author__ = 'CoolCat467'
__version__ = '0.1.0'
__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0

READ = 'English.lang'

def readData(filename):
    """Open filename and return data."""
    data = None
    with open(filename, mode='r') as readfile:
        data = readfile.read()
        readfile.close()
    return data

def writeData(filename, data):
    """Save <data> to <filename>."""
    with open(filename, mode='w', encoding='utf-8') as writefile:
        writefile.write(data)
        writefile.close()

def readLang(filename):
    """Read database from filename and convert to dictionary."""
    # Read data from file
    data = readData(filename)
    # Seperate data into individual lines
    lines = data.split('\n\t')
    # Remove first empty value ('')
    info = lines[1:]
    # Create dictionary to save to
    vsmap = {}
    # Go through all lines from read file
    for entry in info:
        # For each line, take off end and seperate variable to n and data to v
        n, v = entry[:-1].split(' = ')
        # Remove (") from start and end of value
        v = v[1:-1]
        # Record value in dictionary saved as key to value
        vsmap[n] = v
    # Fix last one with wierdness
    vsmap[n] = vsmap[n][:-3]
    # Return created dictionary
    return vsmap

def writeLang(filename, data):
    """Convert dictionary to database file string and save."""
    # Start with the open curly bracket
    info = ['{']
    # For the keys and values of the dictionary input,
    for k, v in ((k, data[k]) for k in data):
        # Add '<key> = "<value>",' to the line data list
        info.append('%s = "%s",' % (k, v))
    # Merge line data together with linebreak and tab characters
    # and take off the final tab and and add linebreak and
    # the end curly bracket to filedata string
    lines = '\n\t'.join(info)[:-1]+'\n}'
    # Finally, write filedata to file
    writeData(filename, lines)

def infIntGen(start=0, change=1):
    """Generate infinite intigers starting with <start> and incrementing by <change>."""
    n = int(start)
    c = int(change)
    while True:
        yield n
        n += c

def getField(number):
    """Function to get the number from data in the event of a falure."""
    global data, numToKey
    return data[numToKey[number]]

def run():
    global data, numToKey, keyToNum
    # Read language database
    data = readLang(READ)
    # Make conversion dictionarys for between key and numbers and backwards
    # Create number to key dict with infinite number gen zipped with keys
    numToKey = {i:k for i, k in zip(infIntGen(), list(data.keys()))}
    # Make a reverse of that for keys to numbers
    keyToNum = {numToKey[k]:k for k in numToKey}
    # Generate data to paste in translator
    toPaste = ''
    # For all the keys in our data,
    for key in data:
        # Get the number that corelates with that key
        num = keyToNum[key]
        # Add '#<key number>*<value>' to toPaste data
        toPaste += ('#%i*' % num) + data[key].replace('\n', '_n_')
    # Print for user and get translated back
    print('Somehow get the following translated:')
    print("'"+toPaste+"'")
    # Get translated back from user
    copied = input('Enter translated result: ')
    # If it's google translate, we need to fix data
    isbad = not input('Is translator nice? (output is not split by spaces)(yes/no) : ').lower() in ('y', 'yes')
    # If used bad (like google translate and it added spaces), fix it
    if isbad:
        # Fix weirdness google translate adds to our fine data
        hashfx = copied.replace(' # ', '#')
        hashfx2 = hashfx.replace('# ', '#')
        hashfx3 = hashfx2.replace(' #', '#')
        starfx = hashfx3.replace(' * ', '*')
        hashfx4 = starfx.replace('#\u200b\u200b', '#')
        copied = hashfx4        
        print('In some cases, may be so evil user has to help. Warning.')
        print('Printing lines so you can fix parsing problems.')
    # Decode translated data back into usable dictionary
    trans = {}
    # Get return characters back from data we changed earlier
    # and then get lines from the pound characters, and ignore the
    # first one which ends up being ''.
    lines = copied.replace('_n_', '\n').split('#')[1:]
    # For each line in output,
    for line in lines:
        # Seperate key number from data by splitting by '*' characters
        split = line.split('*')
        # If split data is empty, skip this line.
        if split == ['']:
            continue
        # If we are using google translate, print the line in case of errors
        if isbad:
            print(line)
        # If there is invalid split data, tell user and prepare for crash :(
        if len(split) != 2:
            print('An error is about to occor very likely.')
            print('Line data: "%s"' % line)
            print('Seperated Data: %r' % split)
        # Get number and value from split data
        num, value = split
        # Add data to translated dictionary and convert key number back to real key.
        trans[numToKey[int(num)]] = value
    # Get language name from user
    lang = input('Language save name: ')
    # Save file is language string + '.lang'
    filename = lang+'.lang'
    # Convert dictionary back into language database and save file
    writeLang(filename, trans)
    print('Done; File saved as %s.' % filename)

if __name__ == '__main__':
    print('%s v%s\nProgrammed by %s.' % (__title__, __version__, __author__))
    run()
