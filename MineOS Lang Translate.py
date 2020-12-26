#!/usr/bin/env python3
# Localization Translator Helper.
# -*- coding: utf-8 -*-

# Semi-compadable with Google Translate.
# If system breaks in bad translator mode, use the last
# number (ex. 28) in the function "getField" for the text
# accociated with that number.

# Can use input from other files by changing the filename of
# the variable READ below.

# For Lolcat use with https://funtranslations.com/lolcat, good translator

# Programmed by CoolCat467

__title__ = 'Localization Translator Helper'
__author__ = 'CoolCat467'
__version__ = '1.0.0'
__ver_major__ = 1
__ver_minor__ = 0
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

def readLang(filename, maxsplen=8, _recursion=False):
    """Read database from filename and convert to dictionary."""
    # Read data from file
    data = readData(filename)
    # Seperate data into individual lines
    lines = data.split('\n\t')
    # If it's a broken file (not split by tabs)
    if len(lines) == 1:
        # Figure out where the spaces start
        s = data.index(' ')
        # Find the end of the spaces
        e = data.index(data[s:s+maxsplen].replace(' ', '')[0])
        # Use start and end to find the seperation and get line data back properly
        lines = data.split('\n'+' '*(e-s))
        # If somehow it's still broken, try to fix it but don't explode.
        if len(lines) == 1:
            if not _recursion:
                return readLang(filename, maxsplen*3, True)
            else:
                raise RuntimeError(f'Invalid File "{filename}"')
    # Remove first empty value ('')
    info = lines[1:]
    # Create dictionary to save to
    vsmap = {}
    # Define search function
    def seccond(string, target, v=0.5):
        # Try to find seccond instance of target
        res = string.find(target, round(-len(string)*v))
        # If index is invalid, return None
        if res == -1:
            return None
        # Catch invalid selections (not seccond)
        if string[res-2:res] == '= ':
            # Delete first one we found from search and try again
            lst = list(string)
            del lst[res]
            # with an offset of one because we deleted a character.
            return seccond(''.join(lst), target, v) + 1
        return res
    # Go through all lines from read file
    an = False
    for entry in info:
        # Get start of removeing index
        rm = seccond(entry, '"', 0.6)
        # Set entry to up to the seccond double quote
        # and then get everything after that point
        entry, rm = entry[:rm], entry[rm+1:]
        # Seperate our entry into the key and the value that's in double quotes
        n, v = entry.split(' = ')
        # Remove double quotes from the start and end of our value.
        if v.startswith('"'):
            v = v[1:]
        if v.endswith('"'):
            v = v[:-1]
        # If a linebreak character was in our removed characters,
        if rm.startswith('\n'):
            # add a fake linebreak back into the data
            v += '_n_'
        # Record value in dictionary saved as key to value
        vsmap[n] = v
    # Fix last one with wierdness with the closing curly bracket
    if vsmap[n].endswith('_n_'):
        vsmap[n] = vsmap[n][:-3]
    # Return created dictionary
    return vsmap

def writeLang(filename, data):
    """Convert dictionary to database file string and save."""
    # Start with the open curly bracket
    info = ['{']
    # No linebreak char to add
    an = False
    # For the keys and values of the dictionary input,
    for k, v in ((k, data[k]) for k in data):
        # If there is a linebreak char, remove it and add it in in the proper place.
        if v.endswith('\n'):
            v = v[:-1]
            an = True
        # Add '<key> = "<value>",' to the line data list
        info.append('%s = "%s",' % (k, v))
        # Add linebreak char back
        if an:
            info[-1] += '\n'
            an = False
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
    print('Copy-paste the following into some sort of translator (text within single quotes):')
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
