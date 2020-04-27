import xml.etree.ElementTree as ET
import random


baseAtts = {'AFFECTS_PRIMARY':'No','AFFECTS_TOTAL':'Yes','BASECOST':'0.0',
            'CARRIED':'Yes','ID':'1380091130683','INCLUDE_NOTES_IN_PRINTOUT':'Yes',
            'LEVELS':'0','MULTIPLIER':'1.0','PARENTID':'114386766304',
            'POSITION':'1','QUANTITY':'1','SHOW_ACTIVE_COST':'No'}
armorAtts = {'ALIAS':'Armor','XMLID':'ARMOR'}

listAtts = {'BASECOST':'0.0','CARRIED':'No','ID':'1380608255469',
            'INCLUDE_NOTES_IN_PRINTOUT':'Yes','LEVELS':'0','MULTIPLIER':'1.0',
            'NAME':'','POSITION':'117','PRICE':'0.0','SHOW_ACTIVE_COST':'Yes',
            'WEIGHT':'0.0','XMLID':'GENERIC_OBJECT'}

# *****   *****   *****   *****   Functions   *****   *****   *****

def prepareEQel(filename):
  global tree
  tree = ET.parse(filename)
  global eqel
  eqel = tree.find('./EQUIPMENT')

# needs regex in the name search
def setAttr(name, attrDict):
  elements = eqel.findall('./*[@NAME="'+name+'"]')
  if len(elements) < 1:
    print('name not found. Try again perhaps?\n')
    return False
  if len(elements) > 1:
    print('more than 1 element for that name found, please check file\n')
    return False
  for attr in attrDict:
    if elements[0].get(attr) != None:
      elements[0].set(attr,attrDict[attr])

def processLine(line):  # processes one line from SSV data copied from
  # a table in a players' handbook 
  pLine = ['']              # the beginning of the processed line
  statsDone = 0             # a counter for the item's stats
  nameDone = False
  
  for bit in line.split():  # for each bit in the line
    if not nameDone:          # if the item name has not been completed
      if bit.isnumeric():       # if the bit is a stat (number)...
        pLine.append(bit)         # append it
        statsDone += 1            # increment statsDone var
        nameDone = True           # done with item name
      else:                     # else...
        if pLine[-1]:  bit = ' '+bit  # if text already exists, add a space...
        pLine[-1] += bit              # add bit to last pLine cell
    elif statsDone < 5:       # if not done with stats... 
      if bit == 'CP': continue  # if CP, skip it
      elif bit == 'SP':         # if SP, multiply last cell by 10 ( 1SP = 10CP)
        pLine[-1] = str(int(pLine[-1])*10)
        continue                  # then continue
      try:                      # try the following...
        float(bit.replace(',',''))                # if the bit is a number...
        pLine.append(bit.replace(',',''))         # append it to pLine
        statsDone += 1            # increment stats counter
      except:                   # if float conversion threw an error...
        pLine.append('0')         # append a 0 in place of whatever it was.
        statsDone += 1            # increment stats counter
    elif statsDone == 5:      # once stats are done ( counter = 5 )
      statsDone += 1            # increment stats counter -> block called only once
      pLine.append(bit)         # append bit
    else:                     # if any other bits... 
      pLine[-1] += ' '+bit      # add them to the notes cell (last one)
  return pLine              # return processed line

def updatePosID(parName,wriName=False,xpath='./EQUIPMENT',position=0):

  if not wriName: wriName = parName[:-4]+'Out'+parName[-4:] # create write name
  elif wriName == True:  wriName = parName   # use parse name if true
  
  tree = ET.parse(parName)
  root = tree.getroot()
  localRoot = root.find(xpath)

  LL = 0  # starts 1 below the actual start value
  II = 0
  newPID = "{:02d}".format(LL)+"{:02d}".format(II)
  oldPID = "{:02d}".format(LL)+"{:02d}".format(II)
  
  for e in localRoot:
    if(e.get('POSITION')):  # if it has a position attribute
        # this hsould be unnecessary. If it doesnt have a Pos attribute, it
        # should have one...
      e.set('POSITION',str(position))
      position += 1 
    if e.tag == 'POWER':    # if tag is power
      II += 1
      e.set('PARENTID',newPID)
      e.set('ID',"{:02d}".format(LL)+"{:02d}".format(II))
    elif e.tag == 'LIST':   # if tag is list      
      LL += 1
      II = 0
      oldPID = e.get('ID')
      newPID = "{:02d}".format(LL)+"{:02d}".format(II)
      e.set('ID',newPID)
  tree.write(wriName,encoding='UTF-16LE')

def addFromSSV(parName,dataf='rawImport.txt',grouping='misc',xpath='./EQUIPMENT'):
  keys = ['NAME','PRICE','LEVELS','PDLEVELS','EDLEVELS','WEIGHT']
  # ugh, mixing weight and mass :(

  tree = ET.parse(parName)
  root = tree.getroot()
  localRoot = root.find(xpath)
  
  PID = 0
  listName = ''
  
  with open(dataf) as dfile:
    for line in dfile.readlines():
      values = processLine(line)
      
      if len(values) == 1: # if only one, it is a groupname and should be
        # handled as a list object
        PID = int(random.random()*10000)
        listName = values[0]
        listDict = listAtts.copy()
        listDict['ALIAS'] = listName # set the list alias to the group name
        listDict['ID'] = str(PID)
        ET.SubElement(localRoot,'LIST',listDict)
      else:
        itemDict = baseAtts.copy()
        for k,i in zip(keys,values[:6]):
          itemDict[k] = i
        itemDict['PARENTID'] = str(PID)
        itemDict['ALIAS'] = listName
        
        if grouping == 'misc':  itemDict['XMLID'] = 'COMPOUNDPOWER'
        elif grouping == 'armor': itemDict['XMLID'] = 'ARMOR'
        else: itemDict['XMLID'] = 'HKA'
        
        elem = ET.SubElement(localRoot,'POWER',itemDict)
        if len(values) > 6:
          notes = ET.SubElement(elem,'NOTES')
          notes.text = values[6]
    tree.write(parName[:-4]+'Out'+parName[-4:],encoding='UTF-16LE')

