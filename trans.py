slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e', 'ж':'zh','з':'z',
'и':'i','й':'i','к':'k','л':'l','м':'m','н':'n', 'о':'o','п':'p','р':'r','с':'s',
'т':'t','у':'u','ф':'f','х':'h', 'ц':'c','ч':'cz','ш':'sh','щ':'scz','ъ':'',
'ы':'y','ь':'','э':'e', 'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G',
'Д':'D','Е':'E','Ё':'E', 'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L',
'М':'M','Н':'N', 'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F',
'Х':'H','Ц':'C','Ч':'CZ','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
'Ю':'U','Я':'YA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'','$':'',
'%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',':':'',';':'',
'<':'','>':'','"':'','\\':'','/':'','№':'','[':'',']':'','{':'','}':'','ґ':'',
'ї':'', 'є':'','Ґ':'g','Ї':'i', 'Є':'e', '—':'','a':'a','b':'b','c':'c','d':'d',
'e':'e','f':'f','g':'g','h':'h','i':'i','j':'j','k':'k','l':'l','m':'m','n':'n',
'o':'o','p':'p','q':'q','r':'r','s':'s','t':'t','u':'u','v':'v','w':'w','z':'z',
'y':'y','x':'x','A':'A','B':'B','C':'C','D':'D','E':'E','F':'F','G':'G','H':'H',
'I':'I','J':'J','K':'K','L':'L','M':'M','N':'N','O':'O','P':'P','Q':'Q','R':'R',
'S':'S','T':'T','U':'U','V':'V','W':'W','X':'X','Y':'Y','Z':'Z'}
trans_name = ''
def translit(name_of_file):
    trans_name = ''
    for lit in name_of_file:
        trans_name += slovar[lit]
    return trans_name

if __name__ == "__main__":
    print(translit('слава яйцам slava yaytsam'))
