# JWT TOKEN CONFIGURATION
# Encryption key
JWT_KEY = (r"86QEo9,a&<_XWqv3fu`)x-n1^B'1y(r09tq>u5TvSr4!@x`vXk85:r0;((k*]Fw{&$,`_IfvC\!CJfBxc£@6,$VM3v]N%/cPsgrd"
           r"9%5-5d'A24.r2bPEzl]M!=((C_0OyCS/f=~*4B5/miMk*m16*Yaxg)hk;cI06yhPUUMJeu}`8/8!#\5SW4YT1tx2`X5f'M^Mj^{S"
           r"ZyZ+7`9lUAF:(1rdx£jW}e+opkM2\XgB44EGN60We];kCP_5wQ5&16BEb:A'HXtZEP-w41/1CzH?9>%1}?M!&b{jo2$XI@jw(;1}")
# Hashing algorithm
JWT_ALGORITHM = "HS256"
# Default invalidation time in seconds (3 hours)
JWT_TOKEN_INVALIDATION_TIME = 60 * 60 * 3


# PASSWORD HASHING CONFIGURATION
# Hasing algorithm
PASSWORD_HASHING_ALGORITHM = "bcrypt"


# VALIDATION CONFIGURATION
PAYLOAD_MAX_SIZE = 1_000_000


# CACHING CONFIGURATION
CACHE_ITEM_LIMIT = 100
CACHE_TIME_TO_LIVE = 60 * 5
