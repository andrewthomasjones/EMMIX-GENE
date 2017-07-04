import win32pipe
w, r = win32pipe.popen2('fake.exe', 't')
#w.write('123\0234\0345\0')
w.write('123\n')
w.write('234\n')
w.write('12\n')
print r.read()
