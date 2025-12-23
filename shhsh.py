
def Arabic(Text):
    Text=str(Text)
    Trans = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
    return Text.translate(Trans)

print(Arabic(12434))