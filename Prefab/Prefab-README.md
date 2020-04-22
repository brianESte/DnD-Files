#Prefabs
are (as i understand it) intended as a way to save complex hero powers from one character to the next. But they are also the only way I have found to add equipment to a character file...

The procedure so far has been...
1. Copy the text from an item/weapon/armor table in a PHB
2. save as a txt, clean up/out anything unnecessary
3. Run the python script.

Known issues:
- Encoding: The files use UTF-16LE encoding, which is kind of uncommon, and either not supported or (more likely) properly detected by all text editors (mistaken for the more common UTF-8). So far Geany has worked pretty well. 
- Ungrouped items: _Most_ items in PHB tables are grouped (food, swords, hats, poison, etc), but there are singular items (bread for example, only has one type..). When the text is copied from the PHB, no formatting is copied with it, thus, currently no way to programmatically determine if the item should fall under the current grouping or stand alone.
- *BODY* stat: Almost all items have a *BODY* stat. This is known. How to properly code that in to the .hdp's so that the HD program recognizes it, is not known, nor if it really matters...
