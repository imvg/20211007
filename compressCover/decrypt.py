

res = open('/Users/mrvg/Desktop/MG4wB6SlPFc.webp', 'rb')

with open('/Users/mrvg/Desktop/MG4wB6SlPFc-decrypt.webp', 'wb') as f:
    f.write(res.read()[8:-1])


res.close()